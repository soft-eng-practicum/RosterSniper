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
	if ( x = $('#search-code').val() ) search_params.code = x;
	if ( x = $('#search-title').val() ) search_params.title = x;
	if ( x = $('#search-professor').val() ) search_params.professor = x;

	// Don't allow empty searches
	if ($.isEmptyObject(search_params)) {
		$('#course_rows').html('');
		$('table').trigger('update');
		return;
	} // else..

	$.getJSON('/courses/', search_params).done(
		response => { 
			$('#course_rows').html(response['course_rows']);
			$('table').trigger('update');
			$('#course_rows td span.fa-heart').on('click', favorite);
		}
	)
}
