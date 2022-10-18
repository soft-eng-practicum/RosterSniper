This document dictates what files need to be changed in order to update 
the existing database structure.

## Note:
There are two separate areas for the database in the `core` and `users`
folders, under the `django_project` folder. This document refers to the general
process, not one or the other, so while the names might change,
the process will not.

# 1. ./migrations/0001_initial.py
This creates the tables that will be utilized by the sqlite database.
Name is the name, fields are the columns/variables of the table.

# 2. ./models.py
### Prerequisites: 0001_initial.py

This creates classes/objects to store variables in order to then
update the database with them.

# 3. ./forms.py
### Prerequisites: models.py | 0001_initial.py
This handles the forms/text-boxes that will allow the user
to enter information on the website, that will then be passed to
the respective models, and then update the database.




