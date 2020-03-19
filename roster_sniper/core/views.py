from random import randint

from django.db.models import Value as V
from django.db.models.functions import Concat

from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse

from .models import Course


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


def courses(request):

    # if request.user.is_authenticated: for adding a track option

    courses = base_search(request)

    if request.is_ajax():

        if page := request.GET.get("page"):
            page = int(page)

            more = len(courses) > page*10
            courses = courses[(page-1)*10:page*10]
        else:
            # Requesting everything (clicked View All button)
            more = False

        return JsonResponse(data={
            "course_rows": render_to_string("courses_rows.html", {'courses': courses}),
            'more': more
        }, safe=False)

    else:

        return render(request, 'courses.html', {'hide_sidebar': True})


def courses2(request):

    if request.is_ajax():

        courses = base_search(request)

        return JsonResponse(data={
            "course_rows": render_to_string("courses_rows.html", {'courses': courses}),
            'more': more
        }, safe=False)
            
    return render(request, 'courses2.html', {'hide_sidebar': True})


def base_search(request):

    courses = Course.objects.all()

    if crn := request.GET.get("crn"):
        courses = courses.filter(CRN__contains=crn)

    if code := request.GET.get("code"):
        # stackoverflow.com/a/36224347
        courses = courses.annotate(
            code=Concat('subject', V('-'), 'number', V(' '), 'section')
        ).filter(
            code__icontains=code
        )

    if title := request.GET.get("title"):
        courses = courses.filter(title__icontains=title)

    if professor := request.GET.get("professor"):
        courses = courses.filter(professor__icontains=professor)

    return courses
