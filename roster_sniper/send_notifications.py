#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import requests

# Set up django
import django
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roster_sniper.settings")
django.setup()
from core.models import Favorite, Course

# URL for checking seat availability given a term and CRN
AVAIL_URL = "https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term={term}&courseReferenceNumber={crn}"

# Cache for CRN lookups
crn_cache = dict()

# Class for regex parsing mishaps
class ParseException(Exception): pass

# Function for checking if a course's availability has become available
def is_newly_available(course):
    # If the result is cached, simply return that
    if course.CRN in crn_cache:
        return crn_cache[course.CRN]
    
    # If the user is watching an already available course,
    # then they don't deserve a notification
    if course.available > 0:
        return False
    
    # Get the latest availability information
    res = requests.get(AVAIL_URL.format(crn=course.CRN, term=course.term))
    
    try:
        # Because yay no json
        available, capacity = re.findall('<span dir="ltr"> (.*?) </span>', res.text)
        available = int(available)
        capacity = int(capacity)
    except ValueError as e:
        # We might need to see if their html changed... should probably send an email besides just printing
        raise ParseException(f"[CRN: {favorite.course.CRN}-{favorite.course.term}] Error parsing updated enrollment info!")

    # Check to see if the new availability matches the old
    actual = capacity - available
    if available != course.available:
        # No match, so update the old course info
        course.actual = actual
        course.capacity = capacity
        course.available = available
        # mixing requests with saving doesn't work in dev mode
        #course.save()

        # Cache the result
        crn_cache[favorite.course.CRN] = True

        return True
    else:
        return False

def send_notification(favorite):
    context = {
        'name': favorite.user.username,
        'title': favorite.course.title,
        'professor': favorite.course.professor,
        'crn': favorite.course.CRN
    }
    email_text = get_template('email.txt')
    email_html = get_template('email.html')
    email_text = email_text.render(context)
    email_html = email_html.render(context)
    
    subject = f"{favorite.course.title} is available!"
    addr_to = favorite.user.email
    addr_from = "Roster Sniper <no-reply@shitchell.com>"
    msg = EmailMultiAlternatives(subject, email_text, addr_from, [addr_to])
    msg.attach_alternative(email_html, "text/html")
    msg.send()

# Loop over the list of enabled favorites
for favorite in Favorite.objects.filter(emailNotify=True):
    should_notify = False
    
    try:
        should_notify = is_newly_available(favorite.course)
    except ParseException as e:
        print(e)
        # send_email()
    
    if should_notify:
        print("[{}] {}: {}-{} is newly available!".format(
            time.strftime('%Y.%m.%d-%H.%M.%S'),
            favorite.course.CRN,
            favorite.course.title,
            favorite.course.section
        ))
        send_notification(favorite)
        time.sleep(2)