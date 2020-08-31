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

# USAGE:

NL Bot doesn't support registration form the Frontend because it was originally not intended for **SaaS*. You must manually create a User object from the command Line.

Before a user can create any Spamming Job, they must activate the App with a valid license key. However, this is useless if the end user has a good knowledge about Python.

** NB: ** The license key is weakly generated. You'd probably need a better mechanism to generate any validate License key.

# License Key:

If you have a better License Key validation system, you'll have to edit the `license` function in *views.py*

```

@login_required(login_url='/login/')
def license(request):
    #your code goes here

    return render(request, 'bot/theme/license.html')

```

You probably have to remove the originally dependencies if the need arises.
