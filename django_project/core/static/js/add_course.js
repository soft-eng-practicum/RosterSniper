
$(function () {
	$('#q, #sidebar-col input').keypress(e => { if (e.keyCode == 13) update_courses() });
	$('#days > button').tooltip({delay: {show: 1500, hide: 100}});

	var searchParams = new URLSearchParams(window.location.search);
	searchParams.forEach(function(value, key) {
		if (key == "days") {
			$('#days').children().each(function() {
				if (value.includes(this.innerHTML)) $(this).addClass('active');
			});
		} else {
			$("#" + key).val(value);
		}
	});

	// I'd imagine the newest term will be the most used option
	if ( !searchParams.has("term") )
		$("#term option:last").attr("selected", "selected");

	update_courses();
})

function update_courses() {
	var searchParams = new URLSearchParams();

	$("#term, #sidebar-col input, #q").each(function() {
		if ( x = $(this).val().trim() ) searchParams.append($(this).attr('id'), x);
	});

	days = '';
	$('#days > button').each(function() {
		if ($(this).hasClass('active')) days += this.innerHTML;
	});
	if (days) searchParams.append("days", days);

	// Don't allow empty searches (term will always be present)
	if ([...searchParams].length < 2) {
		if ( !$('#courses-col').hasClass('bear') ) {
			$('#courses-col').addClass('bear');
			$('#courses').html('');
			history.pushState(null, '', '/add-courses/'); 
		}
		return;
	} // else..

	params = searchParams.toString()
	$('#courses-col').removeClass('bear');
	history.pushState(null, '', '/add-courses/?' + params);
	$.getJSON('/get-courses/?' + params).done(
		response => {
			$('#courses').html(response['courses']);
			$('.meeting').tooltip({delay: {show: 1500, hide: 100}});
			$('#courses .card-footer button').click(show_all);
			$('#courses td i.fa-star').on('click', favorite);
		}
	)
}

function show_all() {
	$(this).parent().prev().children().eq(1).removeClass('limit-four');
	$(this).parent().remove();
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
