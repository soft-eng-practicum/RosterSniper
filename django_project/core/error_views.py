from django.shortcuts import render


# These are Django's default handlers:
# https://github.com/django/django/blob/master/django/conf/urls/__init__.py
# https://github.com/django/django/blob/master/django/views/defaults.py

# Django's HttpResponseNotFound, HttpResponseServerError etc response objects
# only set the status_code for you.. that's literally all they do.. so I don't
# really see a season to use them here

# Helper function, not a view
def handler(status_code, title, emoji):
    # We don't need to render the template with the request context
    response = render(None, 'base/http_error.html', {
        'title': f'{status_code} {title}',
        'emoji': emoji
    })
    response.status_code = status_code
    return response


def handler400(request, *args, **argv):
    return handler(400, 'Bad Request', '🤨')


def handler403(request, *args, **argv):
    return handler(403, 'Forbidden', '😵')


def handler404(request, *args, **argv):
    return handler(404, 'Page Not Found', '😢')


def handler500(request, *args, **argv):
    return handler(500, 'Server Error', '🔥🔥')
