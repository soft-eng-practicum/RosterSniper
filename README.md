# ggc-class-monitor
A utility for monitoring course availability at Georgia Gwinnett College

## TODO

- [ ] Format this README :p
- [ ] Decide on platform(s)
  - [ ] Web
  - [ ] Mobile
  - [ ] Desktop
- [ ] Decide on language(s) to use
- [ ] Decide whether to store course availability history in memory, a database, etc
- [ ] Decide on notification type(s)
  - [ ] Email
  - [ ] Push notification
- [ ] Decide whether to allow user account creation and login
- [ ] RESTful API to more easily allow for various clients and future development
- [ ] Gather information ideally without authentication
  - [x] All registration terms
  - [ ] Current registration term
  - [ ] Available courses
  - [x] Available seats for a course
  
## Tools
  
### urlwatch
https://github.com/thp/urlwatch

### Web Push Notifications
https://developers.google.com/web/fundamentals/push-notifications
https://developers.google.com/web/fundamentals/codelabs/push-notifications

### Useful URLs
**Class Information** *html*  
https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/getClassDetails?term=202002&courseReferenceNumber=21494

**Detailed Class Information** *html*  
https://ggc.gabest.usg.edu/pls/B400/bwckschd.p_disp_detail_sched?term_in=202002&crn_in=21494

**Instructor Details** *json*  
https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/getFacultyMeetingTimes?term=202002&courseReferenceNumber=21494

**Seat Availability** *html*  
https://ggc.gabest.usg.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term=202002&courseReferenceNumber=21494

**Available Terms** *html*  
https://ggc.gabest.usg.edu/pls/B400/bwckctlg.p_disp_dyn_ctlg  
*Optionally, each term has an ID that matches the pattern $year$id, where $year is the term year and $id is 02, 05, or 08 for the Spring, Summer, and Fall semesters respectively. EG: Spring 2020 is 202002, Summer 2018 is 201805.*

**Available Disciplines** *html*  
https://ggc.gabest.usg.edu/pls/B400/bwckctlg.p_display_courses?term_in=202005&call_proc_in=bwckctlg.p_disp_dyn_ctlg&sel_subj=dummy&sel_levl=dummy&sel_schd=dummy&sel_coll=dummy&sel_divs=dummy&sel_dept=dummy&sel_attr=dummy
