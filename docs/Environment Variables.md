# Environment Variables

RosterSniper uses environment variables to specify which setting file is used and to manage settings which are not tracked by git for security reasons. On linux, environment variables can be set using 
```
export VARIABLE_NAME='VALUE'
```

To make this change persistent you must add this line to one of your shell's startup scripts (eg \~/.bashrc).

### RS_ENVIRONMENT

By default, RosterSniper runs in development mode. To run in production mode, you must set `RS_ENVIRONMENT='production'` which will cause RosterSniper to load the [`production.py`][prod] setting file. In this case, you must also specify the following two environment variables.

### RS_SECRET_KEY

In development mode the `SECRET_KEY` is hard-coded in the [`developement.py`][dev] setting file. Obviously we don't want to use the same (public!) secret key in production so you must set `RS_SECRET_KEY='...s0me_rAnDoM_sTr1nG...'`

To generate a new secret key locally, you can run the following in your django python environment:
```
python -c 'from django.core.management import utils; print(utils.get_random_secret_key())'
```

### RS_DB_PASSWORD
In development mode a non-password-protected SQLite database is used. In production, we use a Postgres database whose connection parameters are stored in the [`production.py`][prod] setting file which retrieves the password from the `RS_DB_PASSWORD` environment variable.

[prod]: /django_project/roster_sniper/settings/production.py
[dev]: /django_project/roster_sniper/settings/development.py
