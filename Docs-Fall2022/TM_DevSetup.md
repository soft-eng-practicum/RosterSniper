Git & Pycharm Community Edition setup instructions for Three Musketeer's RosterSniper localhost development.


### `Git Setup`

Open git
```
cd preferred\project\storage\location
git clone repoURL
cd rostersniper
git init
```

### `PyCharm Setup`

Pycharm Community Edition can be utilized as the command prompt for the venv, but it requires some ExecutionPolicy changes for the scripts to work.
Skip to `LOCALHOST SETUP` if you prefer the standard command console.

Open PyCharm, then the Terminal tab at the bottom.
You should notice it saying something along the lines of
".\RosterSniper\venv\Scripts\activate.ps1 cannot be loaded because running scripts is disabled on this system."

```
Get-ExecutionPolicy -List
```
This will show the current executionpolicies, it should be undefined for all unless you've edited them before.

Now, if you can deal with doing this everytime you open PyCharm:
```
Set-ExecutionPolicy -Scope Process unrestricted
.\venv\Scripts\activate.ps1
```
This will allow the script to run once and then reset the policies upon closing the program.

If you want it to automatically run every single time you open PyCharm,
I would highly recommend checking out https:/go.microsoft.com/fwlink/?LinkID=135170 first.
However, if you don't care about potential issues that may or may not be present:
```
Set-ExecutionPolicy -Scope CurrentUser unrestricted
Set-ExecutionPolicy -Scope CurrentUser undefined (to undo it)
```

### `LOCALHOST SETUP`

Activate the venv then navigate to the main rostersniper folder:
```
python pip install -r requirements.txt
cd django_project
pthon manage.py migrate
python manage.py loaddata --app core schools.json
python manage.py update_terms
python manage.py update_sections
```

The update_sections command will take a minute, but once it is done:
```
python manage.py runserver
```
Open your preferred browser, url localhost:8000
