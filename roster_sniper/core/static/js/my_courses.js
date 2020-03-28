
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
            .animate({ padding: 0 })
            .wrapInner('<div />')
            .children()
            .slideUp(function () {
            	$(this).closest('tr').remove();
        	});
	}
}

$('#course_rows span').on('click', update_favorites);
