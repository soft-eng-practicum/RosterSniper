
function favorite() {

	clicked = $(this);

	// Toggles the classes between (font awesome) regular and solid
	// Solid -> favorited
	clicked.toggleClass('far fas');

	$.get('/favorite/', {
		crn: clicked.attr('id'),
		fav: clicked.hasClass('fas')
	});
}
