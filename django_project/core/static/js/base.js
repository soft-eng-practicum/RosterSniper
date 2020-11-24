
// While most browsers display the console in a monospace font, Safari doesn't
// so it's needed to make sure the RosterSniper ascii art is displayed correctly
logo = "font-family: monospace; font-weight: bold;"
logo_green = logo + " text-shadow: 1px 1px 2px black, 0 0 20px green, 0 0 5px darkgreen;"
// String.raw lets us use "\" without having to escape it
console.log(String.raw`%c
    ____             __            _____       _                
   / __ \____  _____/ /____  _____/ ___/____  (_)___  ___  _____
  / /_/ / __ \/ ___/ __/ _ \/ ___/\__ \/ __ \/ / __ \/ _ \/ ___/
 / _, _/ /_/ (__  ) /_/  __/ /   ___/ / / / / / /_/ /  __/ /    
/_/ |_|\____/____/\__/\___/_/   /____/_/ /_/_/ .___/\___/_/ %c.com%c
                                            /_/                 


%cHello! We hope you like our site!

`, logo_green, logo, logo_green, "font-size: 18px;")


// Navbar active links https://gist.github.com/daverogers/5375778
// * prevents selection of the navbar-brand
$(document).ready(function() {
	const pathname = window.location.pathname;
	$("#rs-nav * a[href='"+pathname+"']").addClass("active");
})
