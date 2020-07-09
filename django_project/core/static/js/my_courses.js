
function update_favorites() {

	clicked = $(this);
	clicked_row = clicked.parent().parent();

	// Toggles the classes between (font awesome) solid and regular
	// Solid: enabled, regular: disabled
	clicked.toggleClass('fas far');

	$.get('/my-courses/', {
		crn: clicked_row.attr('id'),
		[clicked.data('type')]: clicked.hasClass('fas')
	});

	if (clicked.data('type') == 'favorite') {
		// stackoverflow.com/a/18570833
		// Maybe add undo pop-up at bottom?
		clicked_row.children('td')
			.animate({'padding-top': 0, 'padding-bottom': 0}, 600)
			.wrapInner('<div />')
			.children()
			.slideUp(600, function () { clicked_row.remove(); });
	}
}

$('tbody > tr > td > span').on('click', update_favorites);
$('.meeting').tooltip({delay: {show: 1500, hide: 100}});
