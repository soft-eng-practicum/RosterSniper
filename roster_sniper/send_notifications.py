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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roster_sniper.settings." + os.environ.get('DJANGO_ENVIRONMENT', 'development'))
django.setup()
from core.models import Favorite, Course

# URL for checking seat availability given a term and CRN
AVAIL_URL = "https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term={term}&courseReferenceNumber={crn}"

# Cache for CRN lookups
crn_cache = dict()

# Class for regex parsing mishaps
class ParseException(Exception): pass

# debug function
DEBUG = bool(os.environ.get('DEBUG'))
def debug(*args):
    if DEBUG:
        print('[DEBUG] ', end="")
        print(*args)

# Function for checking if a course's availability has become available
def is_newly_available(course):
    # If the result is cached, simply return that
    if course.CRN in crn_cache:
        return crn_cache[course.CRN]
    
    # If the user is watching an already available course,
    # then they don't deserve a notification
    if course.available > 0:
        return False
    
    # Try to get the latest availability information
    res = requests.get(AVAIL_URL.format(crn=course.CRN, term=course.term), timeout=5)
    
    try:
        # Because yay no json
        available, capacity = re.findall('<span dir="ltr"> (.*?) </span>', res.text)
        debug("CRN: {} | Available: {} | Capacity: {}".format(course.CRN, available, capacity))
        available = int(available)
        capacity = int(capacity)
    except ValueError as e:
        # We might need to see if their html changed... should probably send an email besides just printing
        raise ParseException(f"[CRN: {favorite.course.CRN}-{favorite.course.term}] Error parsing updated enrollment info!")

    # Check to see if the new availability matches the old
    enrolled = capacity - available
    if available != course.available:
        # No match, so update the old course info
        course.enrolled = enrolled
        course.capacity = capacity
        course.available = available
        # mixing requests with saving doesn't work in dev mode
        course.save()

        # Cache the result
        crn_cache[favorite.course.CRN] = True

        return True
    else:
        return False

def send_notification(favorite):
    debug(f'Sending notification for "{favorite}"')
    # http://{{ hostname }}/unsubscribe/favorite/{{ un_fav }}
    if favorite.user.profile.emailConfirmed:
        context = {
            'name': favorite.user.first_name or favorite.user.username,
            'title': favorite.course.title,
            'professor': favorite.course.professor,
            'crn': favorite.course.CRN,
            'hostname': 'rsniper.shitchell.com',
            'un_fav': str(favorite.emailUnsubID),
            'un_all': str(favorite.user.profile.emailUnsubID)
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
    debug(f'Checking "{favorite}: {favorite.course.CRN}"')
    
    try:
        should_notify = is_newly_available(favorite.course)
    except ParseException as e:
        print(e)
        # send_email()
    except Exception as e:
        print(e)
    
    if should_notify:
        print("[{}] {}: {}-{} is newly available!".format(
            time.strftime('%Y.%m.%d-%H.%M.%S'),
            favorite.course.CRN,
            favorite.course.title,
            favorite.course.section
        ))
        send_notification(favorite)
