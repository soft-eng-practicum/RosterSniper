
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
