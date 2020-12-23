# Commands

There is currently one [custom django-admin command](https://docs.djangoproject.com/en/dev/howto/custom-management-commands/) which is implemented [here](/django_project/core/management/commands). To get more information about a command, run
```
$ ./manage.py command_name -h
```

### `update`
The `update` command can be used to update terms, sections, or favorites by fetching information from Banner. If a section opens or closes as a result of running one of these commands, an email is sent to the section's watchers (if there are any). These commands also have a verbosity option: `-v {0,1,2,3}`.

### Updating Terms
To update terms run the following command. This command also determines which terms are displayed on the Add Courses page and which terms are updated using the `update {sections,favorites}` command.
```
$ ./manage.py update terms
[info] Updated 45 term(s)
[info] Using term Spring 2021 as default
```

### Updating Sections
To update sections run the following command. Because every section references a subject and course, the command first updates subjects and courses. The command only updates sections 
```
$ ./manage.py update sections
[info] Updating subjects and courses using latest term: Summer 2021
[Summer 2021] Downloaded 69 subject(s)
[Summer 2021] Downloaded 500/968 course(s)
[Summer 2021] Downloaded 968/968 course(s)
[info] Updating sections for Summer 2021
[Summer 2021] Downloaded 450/450 section(s)
[Summer 2021] Updating database
[info] Updating sections for Spring 2021
[Spring 2021] Downloaded 500/2126 section(s)
[Spring 2021] Downloaded 1000/2126 section(s)
[Spring 2021] Downloaded 1500/2126 section(s)
[Spring 2021] Downloaded 2000/2126 section(s)
[Spring 2021] Downloaded 2126/2126 section(s)
[Spring 2021] Updating database
```

### Updating Favorites
```
$ ./manage.py update favorites
[info] Updated 5 favorites
```
