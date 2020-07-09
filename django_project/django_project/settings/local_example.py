'''
If you want to use local settings, copy this file and rename it to 'local.py',
then change the settings as you like. The renamed file is in the gitignore but
you should always make sure you aren't committing your passwords!
'''

# List of people who get error email notifications
# Django only sends them when DEBUG=False however
# core.utils.send_admin_email() will send regardless of DEBUG status
# ADMINS = [('YourName', 'YourEmail')]

# Email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'email@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587

# Custom Database?
