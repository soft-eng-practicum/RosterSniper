// See github.com/SHxKM/django-ajax-search for a more complex example
// I originally did something like that but I felt it was too slow

let ajax_call = function() {
	search_params = {}
	if ( $("#search-crn").val() ) search_params.crn = $("#search-crn").val()
	if ( $("#search-code").val() ) search_params.code = $("#search-code").val()
	if ( $("#search-title").val() ) search_params.title = $("#search-title").val()

	// Example: "GET /courses/?crn=50&title=Intro HTTP/1.1" 200 156
	$.getJSON('/courses/', search_params)
		.done(response => {
        	$('#replaceable-content').html(response['html_from_view'])
    	})
}

// Is fired even when 'non textual' keys are released e.g. shift
// not really a big deal
$("#search-crn").keyup(ajax_call)
$("#search-code").keyup(ajax_call)
$("#search-title").keyup(ajax_call)
