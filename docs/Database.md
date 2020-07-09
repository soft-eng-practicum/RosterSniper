# About the Database

To make django turn the models into tables, first run
```
./manage.py makemigrations
```

To see the actual SQL, run
```
./manage.py sqlmigrate <app-name> <migration-number>
```

To make the migrations, run
```
./manage.py migrate
```

To start the django shell, run
```
./manage.py shell
```

### Data

Here is a code snippet that might come in handy for debugging
```
from core.models import Section
from django.contrib.auth.models import User

s = Section.objects.get(pk=50080)
u = User.objects.get(username='ryan')

s.watchers.all()
u.course_set.all()
u.favorite_set.all()
```

To delete all regular data (e.g. not the django_migrations table) run
```
./manage.py flush
```
You could also delete the the sqlite file and rerun migrations if you want to
start from scratch

To delete all data from a particular model, run
```
from core.models import Model
Model.objects.all().delete()
```

To import Course sample data, run
```
./manage.py loaddata notes/sample_data.json
```

To export all data from a particular app, run
```
./manage.py dumpdata <appname> --indent=4 > appdata.json
```

### Users

An admin can be created using the command
```
./manage.py createsuperuser
```
which prompts you for a username, email, and password.

To turn a preexisting user into an admin, run
```
from django.contrib.auth.models import User
user = User.objects.get(username='username')
user.is_staff = True
user.is_superuser = True
user.save()
```
