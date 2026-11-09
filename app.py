from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.utils import secure_filename
import os
from config import Config
from database import db, User, Summary, Keyword
from summarizer.summary import process_document
from utils.email_sender import send_report_email

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

db.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('upload'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('upload'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('upload'))
    return render_template('register.html')

@app.route('/guest')
def guest():
    # create or get a temporary guest user
    guest_user = User.query.filter_by(username='guest').first()
    if not guest_user:
        guest_user = User(username='guest')
        guest_user.set_password('guest')
        db.session.add(guest_user)
        db.session.commit()
    login_user(guest_user)
    return redirect(url_for('upload'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('document')
        if not file:
            flash('No file selected')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Process document
        summary_data = process_document(filepath, current_user.id)
        # Store summary record
        summary = Summary(user_id=current_user.id,
                          pdf_path=summary_data['pdf_path'],
                          docx_path=summary_data.get('docx_path'),
                          raw_text_path=summary_data['raw_text_path'],
                          created_at=summary_data['timestamp'])
        db.session.add(summary)
        db.session.commit()
        flash('Document processed')
        return redirect(url_for('summary_view', summary_id=summary.id))
    return render_template('upload.html')

@app.route('/summary/<int:summary_id>')
@login_required
def summary_view(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    with open(summary.raw_text_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    # The stored HTML version with risk underline is saved in the DB (for simplicity we re‑load from file)
    with open(summary.pdf_path.replace('.pdf', '.html'), 'r', encoding='utf-8') as f:
        html_summary = f.read()
    return render_template('summary.html', html_summary=html_summary, summary=summary)

@app.route('/download/pdf/<int:summary_id>')
@login_required
def download_pdf(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    return send_from_directory(os.path.dirname(summary.pdf_path), os.path.basename(summary.pdf_path), as_attachment=True)

@app.route('/download/word/<int:summary_id>')
@login_required
def download_word(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    if not summary.docx_path:
        flash('Word version not generated')
        return redirect(url_for('summary_view', summary_id=summary_id))
    return send_from_directory(os.path.dirname(summary.docx_path), os.path.basename(summary.docx_path), as_attachment=True)

@app.route('/email/<int:summary_id>', methods=['POST'])
@login_required
def email_report(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    recipient = request.form['email']
    send_report_email(recipient, summary.pdf_path, summary.docx_path)
    flash('Email sent')
    return redirect(url_for('summary_view', summary_id=summary_id))

# Admin keyword management
@app.route('/admin/keywords', methods=['GET', 'POST'])
@login_required
def admin_keywords():
    if not current_user.is_admin:
        flash('Admin access required')
        return redirect(url_for('upload'))
    if request.method == 'POST':
        word = request.form['keyword'].strip().lower()
        if word and not Keyword.query.filter_by(word=word).first():
            db.session.add(Keyword(word=word))
            db.session.commit()
    keywords = Keyword.query.all()
    return render_template('admin_keywords.html', keywords=keywords)

@app.route('/admin/keywords/delete/<int:kw_id>', methods=['POST'])
@login_required
def delete_keyword(kw_id):
    if not current_user.is_admin:
        flash('Admin access required')
        return redirect(url_for('upload'))
    kw = Keyword.query.get_or_404(kw_id)
    db.session.delete(kw)
    db.session.commit()
    return redirect(url_for('admin_keywords'))

if __name__ == '__main__':
    app.run(debug=True)
