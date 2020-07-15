# Commands

There are currently two [custom django-admin commands](https://docs.djangoproject.com/en/dev/howto/custom-management-commands/) which are implemented [here](/django_project/core/management/commands/). To get more information about each command, run
```
./manage.py command_name -h
```

### update_courses
Updates course/section information by fetching it from banner. Eg
```
$ ./manage.py update_courses -v 2
Term: 202005
[downloading] 464/464 open courses collected
[downloading] 90/90 closed courses collected
Term: 202008
[downloading] 500/849 open courses collected
[downloading] 849/849 open courses collected
[downloading] 500/1039 closed courses collected
[downloading] 1000/1039 closed courses collected
[downloading] 1039/1039 closed courses collected
[info] 2442 courses were downloaded
[updating] Adding courses to database
[202005, 50035, Intro to Financial Accounting      ] Successfully updated
...
```

### send_notifications
Updates the enrollment information of sections which are currently being tracked by users and sends out notification emails.
