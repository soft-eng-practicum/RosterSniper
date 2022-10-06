# <img src="docs/img/logo.png" height="40">

RosterSniper is a web application used for monitoring course availability at Georgia Gwinnett College.

- **Website:** https://rostersniper.com
- **Source Code:** https://github.com/soft-eng-practicum/RosterSniper
- **Bug Reports:** https://github.com/soft-eng-practicum/RosterSniper/issues
- **Discord:** https://discord.gg/xHu7UV6

## About

The website is built using Django, jQuery and plugins, Font Awesome, et al.

Here is the Add Courses page:

<img src="docs/img/add-courses.png" width="600">

## Installation

The project requires Python 3.8 or higher along with a few packages as described in [requirements.txt](requirements.txt). To install these packages, it is recommended that you first create a virtual environment using a tool such as `venv`. To install the packages listed in requirements.txt, run `pip install -r requirements.txt`.

The website also uses jQuery, Popper.js, Bootstrap, and Font Awesome, but they are not hosted locally, instead they are hot-linked from a few CDNs and no installation is required.

The development web server is run using the command `python manage.py runserver`.

Our developer documentation can be found [here](docs) and a list of contributors can be found [here](Contributors.md).

# Fall-2022 (Team "Three Musketeers+1")

As a part of our Software Development II course with Dr. Anca, our team has been working on furthering development for a web application called RosterSniper, as several prior teams have before us. The application itself allows users to view class listings from select Banner compatible colleges. It also allows them to filter through the listings and setup a notification methods should any listing the user dictiate be updated, alongside finding rooms that do not have classes during specified timeframes. The current team is adding many QOL features alongside extra notification methods, such as collapsing sections for classes that have a detrimentally large number of them.

For all features that are planned, or currently work in progress, please read [this](/Docs-Fall2022/TODO.md).

## If you are a DEVELOPER:

The project requires Python 3.8 or higher along with a few packages as described in [requirements.txt](requirements.txt). To install these packages, it is recommended that you first create a virtual environment using a tool such as `venv`. To install the packages listed in requirements.txt, run `pip install -r requirements.txt`. Then, activate the venv and type `python manage.py runserver` to activate the localhost version of RosterSniper - accessed in browser at localhost:8000.

For a more in depth explanation and setup tutorial, please visit [this](/Docs-Fall2022/TM_DevSetup.md) page.

## If you are a USER:

To run the web application, simply go to the [RosterSniper](https://rostersniper.com/) website, but if you need a tutorial, go to the [about page](https://rostersniper.com/about/). Though, if you have NoScript - or any other security browser plugins that disable scripts - please ensure it is disabled - or RosterSniper is whitelisted - or the website may not work properly.
