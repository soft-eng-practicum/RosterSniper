#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import django

# Load class data
classes = list()
if len(sys.argv) > 1:
    import json
    classes = open(sys.argv[1]).read()
    classes = json.loads(classes)
else:
    print('provided a class data json file')
    sys.exit(1)

# Set up django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roster_sniper.settings." + os.environ.get('DJANGO_ENVIRONMENT', 'production'))
django.setup()

# Load the Course module to add items to database *after* django has been set up
from core.models import Course

# Add courses to table
for c in classes:
    try:
        # Try to get the CRN
        try:
            crn = c['faculty'][0]['courseReferenceNumber']
        except:
            crn = c['meetingsFaculty'][0]['courseReferenceNumber']

        subject = c['subject']
        number = c['courseNumber']
        title = c['courseTitle']

        term = c['term']
        section = c['sequenceNumber']
        try:
            professor = c['faculty'][0]['displayName']
        except:
            professor = "TBA"
            print("[{}] Failed to find a professor".format(c['id']))

        enrolled = c['seatsAvailable']
        available = c['enrollment']
        capacity = enrolled + available

        # Add it to the database hopefully
        try:
            Course.objects.create(CRN=crn, subject=subject, number=number, title=title, term=term, section=section, professor=professor, enrolled=enrolled, available=available, capacity=capacity)
            print("[{}] Successfully added {}{}!".format(c['id'], subject, number))
        except Exception as e:
            print(f"[{c['id']}] Failed to add to database: {e}")
    except:
        print(f"[{c['id']}] Failed to collect any data")
