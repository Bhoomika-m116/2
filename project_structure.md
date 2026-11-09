# Project Structure

```
legal-doc-summarizer/
├─ app.py
├─ config.py
├─ requirements.txt
├─ database.py
├─ utils/
│  ├─ __init__.py
│  ├─ email_sender.py
│  └─ file_storage.py
├─ summarizer/
│  ├─ __init__.py
│  ├─ nlp_preprocessor.py
│  ├─ risk_extractor.py
│  ├─ report_generator.py
│  ├─ word_exporter.py
│  └─ summary.py
├─ templates/
│  ├─ layout.html
│  ├─ login.html
│  ├─ register.html
│  ├─ upload.html
│  ├─ summary.html
│  ├─ admin_keywords.html
│  └─ history.html
├─ static/
│  ├─ css/
│  │  └─ main.css
│  └─ js/
│     └─ main.js
└─ instance/   (runtime: app.db, uploaded files)
```

All source files are placed under `C:\Users\pc\OneDrive\Desktop\2` ready to be committed to a GitHub repository.
