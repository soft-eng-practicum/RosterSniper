# Commands

There is currently one [custom django-admin command](https://docs.djangoproject.com/en/dev/howto/custom-management-commands/) which is implemented [here](/django_project/core/management/commands/). To get more information about each command, run
```
./manage.py command_name -h
```

### update_courses
Updates course/section information by fetching it from banner. If a section opens or closes an email is sent to any watchers.
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

To only update the enrollment information of favorited sections, use the `-f` option.
```
$ ./manage.py update_courses -f -v 2
```
