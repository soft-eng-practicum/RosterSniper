Note: There are two separate areas for the database in the `core` and `users`
folders, under the `django_project` folder. This document refers to the general
process, not one or the other, so while the names might change,
the process will not.

# 1. Altering the code

### ./models.py
This creates the classes that will be converted into tables for the database.

### ./forms.py
This handles the forms/text-boxes that will appear when called to edit a model.

EX: "users/templates/registration/profile.html" 

# 2. Updating the database

The database - at least for localhost environments - is located at 
"./django_project/rostersniper/db.sqlite3". It will not immediately update upon the code
being changed. So, commands must be run to alter it.

### py manage.py makemigrations

This will take what is listed in models.py and convert it into code that will create/alter the
database file. This code will be stored in new files under "./migrations/xxxx.py".
If no migration files are present it will always be called 0001_initial.py, 
otherwise it will be in sequential order and have a title based upon what it does. 

EX: "0002_alter_military_time.py"

### py manage.py migrate

`makemigrations` must be done before this command will work, or at least, pycharm won't allow it.
Regardless, this command will execute the migrations listed in the files created prior, and update
the database.

