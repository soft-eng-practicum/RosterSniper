#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import datetime
import argparse

SEARCH_URL = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_subject=&txt_term={term}&pageOffset={offset}&pageMaxSize=500'
SESSION_URL = 'https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/term/search?mode=search&term={term}'

# Collect some command line arguments
parser = argparse.ArgumentParser(description='Update all course information from banner.')
parser.add_argument('-t', '--term', dest='term', type=int,
                    help='The semester to search for course information (ex: 202005)')
parser.add_argument('-o', '--outfile', dest='outfile', type=str,
                    help='Output the course information to the specified file in JSON format')
parser.add_argument('-i', '--infile', dest='infile', type=str,
                    help='Update the database using the specified JSON file')
parser.add_argument('-p', '--production', dest='production', action='store_true',
                    help='Update the production database')
parser.add_argument('-d', '--development', dest='development', action='store_true',
                    help='Update the development database')
parser.add_argument('-n', '--no-update', dest='no_update', action='store_true',
                    help='Fetch course information but do not update the database')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='More verbose output')
args = parser.parse_args()

# Load class data
classes = list()
if args.infile:
    # Load from JSON file
    classes = open(args.infile).read()
    classes = json.loads(classes)
else:
    # Load from web
    import requests
    session = requests.Session()
    # Get session cookies
    session.get(SESSION_URL.format(term=args.term))
    # Load course information until finished
    total = 0
    offset = 0
    empty_results = False
    while not empty_results:
        res = session.get(SEARCH_URL.format(term=args.term, offset=offset))
        data = res.json()['data']
        if len(data) == 0:
            empty_results = True
        else:
            classes.extend(data)
            total += len(data)
            offset += 500
            print('[downloading] {}/{} courses collected'.format(total, res.json()['totalCount']))

# Save the data if necessary
if args.outfile:
    with open(args.outfile, 'w') as f:
        f.write(json.dumps(classes, indent=2))
        print('[writing] saved course information to {}'.format(args.outfile))

# If we aren't supposed to update the database, exit here
if args.no_update:
    sys.exit(0)

# Set up django
import django
from django.db.utils import IntegrityError
if args.production:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roster_sniper.settings.production")
elif args.development:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roster_sniper.settings.development")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roster_sniper.settings." + os.environ.get('DJANGO_ENVIRONMENT', 'production'))
django.setup()

# Load the Course module to add items to database *after* django has been set up
from core.models import Course

# Add courses to table
print('[updating] Adding courses to database')
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
            if args.verbose:
                print(f"[{c['id']}] Failed to find a professor")

        # Get the meeting time
        meeting_time = c.get('meetingsFaculty', [{}])
        days = ""
        if len(meeting_time) > 0:
            meeting_time = meeting_time[0].get('meetingTime', {})
            if meeting_time.get('monday'):
                days += "M"
            if meeting_time.get('tuesday'):
                days += "T"
            if meeting_time.get('wednesday'):
                days += "W"
            if meeting_time.get('thursday'):
                days += "T"
            if meeting_time.get('friday'):
                days += "F"
            if meeting_time.get('saturday'):
                days += "S"

            try:
                start_hour = int(meeting_time.get('beginTime', '0000')[:2])
                start_min = int(meeting_time.get('beginTime', '0000')[2:])
                end_hour = int(meeting_time.get('endTime', '0000')[:2])
                end_min = int(meeting_time.get('endTime', '0000')[2:])
                start_time = datetime.time(start_hour, start_min)
                end_time = datetime.time(end_hour, end_min)
            except:
                start_time = datetime.time(0, 0)
                end_time = datetime.time(0, 0)
        else:
            start_time = datetime.time(0, 0)
            end_time = datetime.time(0, 0)

        enrolled = c['seatsAvailable']
        available = c['enrollment']
        capacity = enrolled + available

        # Add it to the database hopefully
        try:
            Course.objects.create(CRN=crn, subject=subject, number=number, title=title, term=term, section=section, professor=professor, days=days, start_time=start_time, end_time=end_time, enrolled=enrolled, available=available, capacity=capacity)
            if args.verbose:
                print(f"[{c['id']}] Successfully added {subject}{number}-{section}!")
        except IntegrityError:
            course = Course.objects.filter(CRN=crn)[0]
            course.subject = subject
            course.number = number
            course.title = title
            course.term = term
            course.section = section
            course.professor = professor
            course.enrolled = enrolled
            course.available = available
            course.capacity = capacity
            course.save()
            if args.verbose:
                print(f"[{c['id']}] Successfully updated {subject}{number}-{section}")
        except Exception as e:
            if args.verbose:
                print(f"[{c['id']}] Failed to add to database: {e}")
    except Exception:
        if args.verbose:
            print(f"[{c['id']}] Failed to collect any data" )
