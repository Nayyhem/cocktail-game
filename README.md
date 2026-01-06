# BoycottLudo - Projet Flask (SQLite + Argon2)

## Quick start

### 1. Create a virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```
### 2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
### 3. Initialize database (optional - creates a demo user alice/password123):
   ```bash
   flask --app app init-db
   ```
### 4. Run:
   ```bash
   python app.py
   ```
### 5. Open 
http://127.0.0.1:5000

## Notes
- Tailwind is used via CDN for convenience; for production build, integrate Tailwind properly.
- Change `FLASK_SECRET` env var to a secure random value in production.

Projet réalisé par :
**Bonnet Samuel, Therage Ludovic, Huyghe Néo, Baillet Quentin**
