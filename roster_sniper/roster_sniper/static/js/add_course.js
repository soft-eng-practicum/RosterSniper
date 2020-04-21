// Runs when the page is 'ready'
$(function() {
	$('table').tablesorter({
		theme : 'bootstrap',
		widthFixed: true,
		sortReset: true,
		sortRestart : true
	}).tablesorterPager({
		container: $('.ts-pager'),
		cssGoto: '.pagenum',
		output: '{startRow} - {endRow} / {totalRows}'
	});

	// Triggers search if enter is pressed while in a search box
	$('thead input').keypress(e => { if (e.keyCode == 13) update_courses() });
});

function update_courses() {
	search_params = {};
	if ( x = $('#search-crn').val() ) search_params.crn = x;
	if ( x = $('#search-code').val() ) {
		// I originally had the following but apparently Firefox doesn't support
		// lookaheads and lookbehinds: x.replace(/(?<=[A-Za-z]) (?=[0-9])/, '-')
		search_params.code = /[a-zA-Z]{4} /.test(x)? x.replace(' ', '-') : x;
	}
	if ( x = $('#search-title').val() ) search_params.title = x;
	if ( x = $('#search-professor').val() ) search_params.professor = x;

	// Don't allow empty searches
	if ($.isEmptyObject(search_params)) {
		$('#course_rows').html('');
		$('table').trigger('update');
		return;
	} // else..

	if ( x = $('#search-term').val() ) search_params.term = x;

	days = '';
	$('#days').children().each(function() {
		if ($(this).hasClass('active')) days += this.innerHTML;
	});
	if (days) search_params.days = days;

	$.getJSON('/add-course/', search_params).done(
		response => { 
			$('#course_rows').html(response['course_rows']);
			$('table').trigger('update');
			$('#course_rows td span.fa-star').on('click', favorite);
		}
	)
}

function favorite() {

	clicked = $(this);

	// Toggles the classes between (font awesome) regular and solid
	// Solid -> favorited
	clicked.toggleClass('far fas');

	if (logedin) {
		$.get('/my-courses/', {
			crn: clicked.attr('id'),
			favorite: clicked.hasClass('fas')
		});
	} else {
		window.location.href = '/login/'
	}
}
