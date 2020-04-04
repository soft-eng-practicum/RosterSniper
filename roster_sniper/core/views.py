from random import randint

from django.db.models import Value as V
from django.db.models.functions import Concat

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import Course, Favorite
from users.models import Profile


def home(request):
    return render(request, 'home.html')


def about(request):
    names = ['Ryan Cosentino', 'Shaun Mitchell']
    temp = randint(0, 1)
    context = {
        'title': 'About',
        'name1': names[temp],
        'name2': names[1-temp],
    }

    return render(request, 'about.html', context)


def add_course(request):
    ''' First course search page that was developed '''

    if request.is_ajax():

        courses = base_search(request)

        if page := request.GET.get('page'):
            page = int(page)

            more = len(courses) > page*10
            courses = courses[(page-1)*10:page*10]

        else: # Requesting everything (clicked View All button)
            more = False

        return JsonResponse(data={
            'course_rows': render_to_string('add_course_rows.html', {
                'courses': courses,
                'CRNs': request.user.course_set.values_list('CRN', flat=True)
                    if request.user.is_authenticated else None
            }),
            'more': more
        }, safe=False)

    else:
        return render(request, 'add_course.html', {'hide_sidebar': True})


def add_course_2(request):
    ''' Developed after courses(), this view uses the tablesorter jQuery plugin
    to display courses in a nice sortable table '''

    if request.is_ajax():

        courses = base_search(request)

        return JsonResponse(data={
            'course_rows': render_to_string('add_course_rows.html', {
                'courses': courses,
                'CRNs': request.user.course_set.values_list('CRN', flat=True)
                    if request.user.is_authenticated else None
            })
        }, safe=False)

    else:
        return render(request, 'add_course_2.html', {'hide_sidebar': True})


def base_search(request):
    ''' Not an actual view but a helper function '''

    courses = Course.objects.all()

    if crn := request.GET.get('crn'):
        courses = courses.filter(CRN__contains=crn)

    if code := request.GET.get('code'):
        # stackoverflow.com/a/36224347
        courses = courses.annotate(
            code=Concat('subject', V('-'), 'number', V(' '), 'section')
        ).filter(
            code__icontains=code
        )

    if title := request.GET.get('title'):
        courses = courses.filter(title__icontains=title)

    if professor := request.GET.get('professor'):
        courses = courses.filter(professor__icontains=professor)

    return courses


@login_required
def my_courses(request):
    ''' Shows all of the user's favorited courses and lets them enable / disable
    email notifications and unfavorite courses. '''

    if request.is_ajax() and (crn := request.GET.get('crn')):

        if favorite := request.GET.get('favorite'):
            if favorite == 'true':
                request.user.course_set.add(crn)
            elif favorite == 'false':
                request.user.course_set.remove(crn)

        elif (email := request.GET.get('email')) \
            and (email == 'true' or email == 'false'):

            f = Favorite.objects.get(user=request.user, course__CRN=crn)
            f.emailNotify = email == 'true'
            f.save()

        return HttpResponse('')

    else:
        return render(request, 'my_courses.html', {
            'hide_sidebar': True,
            'favorites': request.user.favorite_set.all()
        })


def unsubscribe(request, unsubType, unsubID):
    '''
    Unsubscribe requests contain an unsubType and an unsubID. The unsubID is
    used to safely allow users to unsubscribe without logging in by clicking a
    link sent within an email, accessing a URL unique to the particular
    unsubscribe request. Because there are 2^122 different version 4 UUIDs it is
    unlikely that someone would guess a correct one or even want to.
    '''
        
    try:
        if unsubType == 'favorite':
            unsubObject = Favorite.objects.get(emailUnsubID=unsubID)
            text = f'emails related to {unsubObject.course}'

        elif unsubType == 'all':
            unsubObject = Profile.objects.get(emailUnsubID=unsubID)
            text = 'all emails'

        else:
            return render(request, 'unsubscribe_error.html')

        # Ordinarily unsubscribe links sent in emails will not have the
        # 'subscribe' parameter in the query string so the following will
        # evaluate to False.
        #
        # This is meant to be used by a button on the unsubscribe page that lets
        # users re subscribe by making a GET request in the background. It
        # doesn't actually matter what the argument is, as long as it exists.
        if request.is_ajax():
            unsubObject.emailNotify = request.GET.get('subscribe') is not None
            unsubObject.save()
            return HttpResponse('')

        else:
            unsubObject.emailNotify = False
            unsubObject.save()
            return render(request, 'unsubscribe.html', { 'text': text })

    except ObjectDoesNotExist:
        return render(request, 'unsubscribe_error.html')
