from random import randint
from functools import reduce
import datetime
import operator
import re

from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import School, Term, Section, Favorite
from users.models import User


def home(request):
	return render(request, 'home.html', {
		'schools': School.objects.filter(active=True),
	})


def about(request):
	names = ['Ryan Cosentino', 'Shaun Mitchell']
	temp = randint(0, 1)
	context = {
		'name1': names[temp],
		'name2': names[1-temp],
	}

	return render(request, 'about.html', context)


def get_courses(request, school):

	if not request.is_ajax():
		raise Http404()

	try:
		s = School.objects.get(short_name=school)
	except School.DoesNotExist:
		raise Http404()

	if term := request.GET.get('term'):
		# The custom order_by is needed so the regroups work in the template
		sections = (
			Section.objects
			.order_by('course', 'section_title', 'section_num')
			.select_related('professor', 'course')
			.filter(school=s, term=term)
		)
	else:
		return JsonResponse(data={})

	query = Q()

	if q := request.GET.get('q'):
		#
		# TODO: split on : and - characters also
		# https://stackoverflow.com/a/23720594
		#
		for term in q.split():
			query &= (
				Q(crn__exact=term)
				| Q(section_num__exact=term)
				| Q(section_title__icontains=term)
				| Q(course__number__exact=term)
				| Q(course__subject__pk__iexact=term)
			)

	if days := request.GET.get('days'):
		query &= Q(days__contains=days)

	if crsNumMin := request.GET.get('crsNumMin'):
		query &= Q(course__number__gte=crsNumMin)
	if crsNumMax := request.GET.get('crsNumMax'):
		query &= Q(course__number__lte=crsNumMax)

	if creditHourExact := request.GET.get('creditHourExact'):
		query &= Q(credit_hours=creditHourExact)
	if creditHourMin := request.GET.get('creditHourMin'):
		query &= Q(credit_hours__gte=creditHourMin)
	if creditHourMax := request.GET.get('creditHourMax'):
		query &= Q(credit_hours__lte=creditHourMax)

	if professor := request.GET.get('professor'):
		for term in professor.split():
			query &= Q(professor__firstname__icontains=term) \
				| Q(professor__lastname__icontains=term)

	if room := request.GET.get('room'):
		query &= Q(room__icontains=room.replace(' ', '-'))

	sections = sections.filter(query)

	return JsonResponse(
		data={
			'courses': render_to_string(
				'courses/add_courses_rows.html', {
					'all_sections': sections,
					'crns': request.user.section_set.values_list('crn', flat=True)
						if request.user.is_authenticated else None
				}
			)
		},
		safe=False
	)


def add_courses(request, school):
	""" The Add Courses page lets users search for and favorite sections. """

	try:
		s = School.objects.get(short_name=school)
	except School.DoesNotExist:
		raise Http404()

	return render(
		request,
		'courses/add_courses.html',
		{
			'terms': Term.objects.filter(school=s, display=True),
			'color' : s.color_hex
		}
	)


def get_rooms(request, school):

	# TODO: uncomment
	# if not request.is_ajax():
	# 	raise Http404()

	try:
		s = School.objects.get(short_name=school)
	except School.DoesNotExist:
		raise Http404()

	# Get all sections (with a room) for the given school
	if term := request.GET.get('term'):
		sections = (
			Section.objects
			.order_by('room')
			.filter(school=s, term__code=term)
			.exclude(room='')
		)
	else:
		return JsonResponse(data={})

	# get all room ids
	room_ids = set(sections.values_list('room', flat=True).distinct())

	# Find all classes taking place in the specified time window
	query = Q()

	# check the day
	if days := request.GET.get('days'):
		query &= reduce(operator.or_, (Q(days__contains=x) for x in days))

	# check start/end times
	time_start = datetime.time(0, 0)
	time_end = datetime.time(23, 59)

	if request_start := request.GET.get("timeStart"):
		times = re.findall('\d+', request_start)[:2]
		if len(times) == 2:
			times = [int(x) for x in times]
			if 'pm' in request_start.lower() and times[0] != 12:
				times[0] += 12
			time_start = datetime.time(*times)

	if request_end := request.GET.get("timeEnd"):
		times = re.findall('\d+', request_end)[:2]
		if len(times) == 2:
			times = [int(x) for x in times]
			if 'pm' in request_end.lower() and times[0] != 12:
				times[0] += 12
			time_end = datetime.time(*times)

	# A class does not intersect with a given time window if:
	# - The class ends before (lt) the window starts, or
	# - The class starts after (gt) the window ends
	# The following is the negation of that
	query &= Q(end_time__gte=time_start) & Q(start_time__lte=time_end)

	# run our query
	sections = sections.filter(query)

	# get only the room numbers
	unavailable_room_ids = set(sections.values_list('room', flat=True).distinct())

	# find all rooms that aren't in the list of rooms having classes at the given time
	available_room_ids = room_ids.difference(unavailable_room_ids)

	return JsonResponse(data={
		'startTime': time_start,
		'endTime': time_end,
		'days': days,
		'totalRoomCount': len(room_ids),
		'allRoomIDs': list(room_ids),
		'availableCount': len(available_room_ids),
		'unavailableCount': len(unavailable_room_ids),
		'availableRoomIDs': sorted(available_room_ids),
		'unavailableRoomIDs': list(unavailable_room_ids),
		'unavailableSections': list(sections.values())
	}, safe=False)


def find_rooms(request, school):

	try:
		s = School.objects.get(short_name=school)
	except School.DoesNotExist:
		raise Http404()

	return render(
		request,
		'rooms/room_finder.html',
		{
			'terms': Term.objects.filter(school=s, display=True),
			'color' : s.color_hex
		}
	)


@login_required
def my_courses(request):
	""" Shows user their favorites, lets them remove favorites, and lets them
	enable / disable email notifications. """

	if (
		request.is_ajax()
		and (term := request.GET.get('term'))
		and (crn := request.GET.get('crn'))
	):

		if favorite := request.GET.get('favorite'):
			s = Section.objects.get(term_id=term, crn=crn)
			if favorite == 'true':
				request.user.section_set.add(s)
			elif favorite == 'false':
				request.user.section_set.remove(s)

		elif email := request.GET.get('email'):
			Favorite.objects.filter(
				user=request.user, section__term_id=term, section__crn=crn
			).update(email_notify=email == 'true')

		return HttpResponse('')

	else:
		return render(
			request,
			'courses/my_courses.html',
			{'favorites': request.user.favorite_set.all()}
		)


def unsubscribe(request, unsub_type, unsub_id):
	"""
	Unsubscribe requests contain an unsub_type and an unsub_id. The unsub_id is
	used to safely allow users to unsubscribe without logging in by clicking a
	link sent within an email, accessing a URL unique to the particular
	unsubscribe request. Because there are 2^122 different version 4 UUIDs it is
	unlikely that someone would guess a correct one or even want to.
	"""

	try:
		if unsub_type == 'favorite':
			unsub_object = Favorite.objects.get(email_unsub_id=unsub_id)
			text = f'emails related to {unsub_object.section}'

		elif unsub_type == 'all':
			unsub_object = User.objects.get(email_unsub_id=unsub_id)
			text = 'all emails'

		else:
			raise ObjectDoesNotExist()

		# Ordinarily unsubscribe links sent in emails will not have the
		# 'subscribe' parameter in the query string so the following will
		# evaluate to False.
		#
		# This is meant to be used by a button on the unsubscribe page that lets
		# users re subscribe by making a GET request in the background. It
		# doesn't actually matter what the argument is, as long as it exists.
		unsub_object.email_notify = request.GET.get('subscribe') is not None
		unsub_object.save()

		if request.is_ajax():
			return HttpResponse('')
		else:
			return render(request, 'unsubscribe.html', { 'text': text })

	except ObjectDoesNotExist:
		return render(
			request,
			'base/message.html',
			{
				'title': 'Unsubscribe Error',
				'message': 'Your unsubscribe link is invalid! 😕'
			}
		)
