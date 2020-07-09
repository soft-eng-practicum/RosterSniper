from random import randint

from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import Professor, Term, Course, Section, Favorite
from users.models import User


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


def add_courses(request):

    if request.is_ajax():

        query = Q()
        sections = Section.objects.select_related('professor', 'course').all()

        if term := request.GET.get('term'):
            sections = sections.filter(term=term)
        else:
            return JsonResponse(data={})

        if q := request.GET.get('q'):
            #
            # TODO: split on : and - characters also
            # https://stackoverflow.com/a/23720594
            #
            for term in q.split():
                query &= Q(CRN__exact=term) | Q(section_num__exact=term) \
                    | Q(course__number__exact=term) | Q(course__title__icontains=term) \
                    | Q(course__subject__pk__iexact=term)

        if days := request.GET.get('days'):
            query &= Q(days__contains=days)

        if crsNumMin := request.GET.get('crsNumMin'):
            query &= Q(course__number__gte=crsNumMin)
        if crsNumMax := request.GET.get('crsNumMax'):
            query &= Q(course__number__lte=crsNumMax)

        if creditHourExact := request.GET.get('creditHourExact'):
            query &= Q(course__credit_hours=creditHourExact)
        if creditHourMin := request.GET.get('creditHourMin'):
            query &= Q(course__credit_hours__gte=creditHourMin)
        if creditHourMax := request.GET.get('creditHourMax'):
            query &= Q(course__credit_hours__lte=creditHourMax)

        if professor := request.GET.get('professor'):
            for term in professor.split():
                query &= Q(professor__firstname__icontains=term) \
                    | Q(professor__lastname__icontains=term)

        # page = request.GET.get('page', 1)

        sections = sections.filter(query)

        return JsonResponse(data={
            'courses': render_to_string('courses/add_courses_rows.html', {
                'all_sections': sections,
                'CRNs': request.user.section_set.values_list('CRN', flat=True)
                    if request.user.is_authenticated else None
            })
        }, safe=False)

    else:
        return render(request, 'courses/add_courses.html',
            { 'terms': Term.objects.filter(active=True) }
        )


@login_required
def my_courses(request):
    ''' Shows all of the user's favorited sections and lets them enable / disable
    email notifications and unfavorite sections. '''

    if request.is_ajax() and (crn := request.GET.get('crn')):

        if favorite := request.GET.get('favorite'):
            if favorite == 'true':
                request.user.section_set.add(crn)
            elif favorite == 'false':
                request.user.section_set.remove(crn)

        elif (email := request.GET.get('email')) \
            and (email == 'true' or email == 'false'):

            f = Favorite.objects.get(user=request.user, section__CRN=crn)
            f.emailNotify = email == 'true'
            f.save()

        return HttpResponse('')

    else:
        return render(request, 'courses/my_courses.html', {
            'favorites': request.user.favorite_set.all()
        })


def unsubscribe(request, unsubType, unsubID):
    '''
    Unsubscribe requests contain an unsubType and an unsubID. The unsubID is
    used to safely allow users to unsubscribe without logging in by clicking a
    link sent within an email, accessing a URL unique to the particular
    unsubscribe request. Because there are 2^122 different version 4 UUIDs it is
    unlikely that someone would guess a correct one or even want to.

    TODO: Test and reuse error code
    '''

    try:
        if unsubType == 'favorite':
            unsubObject = Favorite.objects.get(emailUnsubID=unsubID)
            text = f'emails related to {unsubObject.section}'

        elif unsubType == 'all':
            unsubObject = User.objects.get(emailUnsubID=unsubID)
            text = 'all emails'

        else:
            return render(request, 'base/message.html', {
                'title': 'Unsubscribe Error',
                'message': 'Your unsubscribe link is invalid! 😕'
            })

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
        return render(request, 'base/message.html', {
            'title': 'Unsubscribe Error',
            'message': 'Your unsubscribe link is invalid! 😕'
        })
