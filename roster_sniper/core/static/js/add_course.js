// See github.com/SHxKM/django-ajax-search for a more complex example
// I originally did something like that but I felt it was too slow

// Is fired even when 'non textual' keys are released e.g. shift
// not really a big deal

var page = 0;

function update_courses(btn='') {

	// This only adds a parameter to the query string if it is non-empty
	search_params = {};
	if ( x = $('#search-crn').val() ) search_params.crn = x;
	if ( x = $('#search-code').val() ) search_params.code = x;
	if ( x = $('#search-title').val() ) search_params.title = x;
	if ( x = $('#search-professor').val() ) search_params.professor = x;

	// Don't allow empty searches
	if ($.isEmptyObject(search_params)) {
		$('#course_rows').html('');
		$('#morebtns').hide();
		$('#howtosearch').show();
		return;
	} // else..

	$('#howtosearch').hide();

	var updt_func;
	if (btn == 'more') {
		page++;
		search_params.page = page;

		updt_func = response => { $('#course_rows').append(response['course_rows']); }

	} else {
		if (btn != 'all') {
			page = 1;
			search_params.page = page;
		}

		updt_func = response => { $('#course_rows').html(response['course_rows']); }
	}

	$.getJSON('/add-course/', search_params).done(updt_func,
		response => { 
			if (response['more']) $('#morebtns').show();
			else $('#morebtns').hide();
			$('#course_rows td span.fa-heart').on('click', favorite);
		}
	)
}

// on 'paste' too?
$('#search-parent input').on('keyup', update_courses);

// Automatically run search in case user reloads page with search parameters
update_courses();
