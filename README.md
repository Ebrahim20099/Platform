# Platform

## Requirements
- Python 3.13
- PostgreSQL database on Render

## Local setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

## Production on Render
1. Push the project to GitHub.
2. Create a new Web Service on Render.
3. Connect the repo.
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add environment variables:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `MAIL_SERVER`
   - `MAIL_PORT`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `MAIL_SENDER`
6. Create a PostgreSQL database from Render Dashboard if needed.
7. Deploy.

## Important
- Use `DATABASE_URL` supplied by Render.
- Remove local SQLite dependency in production by setting `DATABASE_URL`.
- The app will use SQLite only when no `DATABASE_URL` is set.
