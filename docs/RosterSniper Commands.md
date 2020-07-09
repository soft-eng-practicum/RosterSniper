# RosterSniper Commands

There are currently two [custom django-admin commands](https://docs.djangoproject.com/en/dev/howto/custom-management-commands/) which are implemented [here](/django_project/core/management/commands/). To get more information about each command, run
```
./manage.py command_name -h
```

### update_courses
Updates course/section information by fetching it from banner. Eg
```
$ ./manage.py update_courses -t 202008
Term: 202008
[downloading] 500/1100 open courses collected
[downloading] 1000/1100 open courses collected
[downloading] 1100/1100 open courses collected
[downloading] 500/781 closed courses collected
[downloading] 781/781 closed courses collected
[updating] Adding courses to database
```

### send_notifications
Updates the enrollment information of sections which are currently being tracked by users and sends out notification emails.
