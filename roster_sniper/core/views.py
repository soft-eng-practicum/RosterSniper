from random import randint

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

    # TODO: maybe use pagination when all of the courses are added?

    # TODO: change order when clicking header entries: stackoverflow.com/q/24033294
    courses = Course.objects.all()

    crn = request.GET.get("crn")
    if crn:
        courses = courses.filter(CRN__icontains=crn)

    code = request.GET.get("code")
    if code:
        # TODO
        pass

    title = request.GET.get("title")
    if title:
        courses = courses.filter(title__icontains=title)

    # if request.user.is_authenticated: for adding a track option

    if request.is_ajax():
        html = render_to_string("courses_search_rows.html", {'courses': courses})

        return JsonResponse(data={"html_from_view": html}, safe=False)

    else:
        context = {
            'title': 'Courses',
            'courses': courses
        }
            
        return render(request, 'courses.html', context)
