# nl_bot
A Spam Bot to automate spamming activities on Nairaland.

# SETUP:

```
pip install -r requirements.txt

```

User must have to set `SECRET_KEY` and `DATABASE_URL` environment variables
in a .env file

If `DATABASE_URL` is not set, default SQLite3 would be used as default

```
touch .env

#Add the following to the .env file

SECRET_KEY='********'
DATABASE_URL='postgresql://....'

```

**Apply migrations:**

```
python manage.py migrate

```
**Run server:**

```

gunicorn project.wsgi

```


