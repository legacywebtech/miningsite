# About
This is a django mining investment website where users invest and get profits depending on selected mining package.
Investment package increments profit everyday and returns capital + profits on the last day of the package.


# Technical details
* How investment process works is that it starts to drop daily profits from the approval date and finally drops RIO(Returns On Investment) which
is capital + total calculated profits, after end date of investment
* Function to run investment process to increment profit till end of investment was implemented without use of background task running services 
such as celery, redis, crontab, django-scheduler etc
* Function to delete notifications of user longer than 3days was implemented using similar method to the above
* Diverse pages were made to run either of the above functions rather than both to reduce load time(increase speed)
* A single function handles account credit and debit, saves the transaction record and sends appropriate notification 
* Users can get their investment details in PDF format
* Gets users location and timezone on sign up and profile settings
* Cryptocurrencies qr code are generated from address
* Email uses html templates for formatting
* Ajax and animations


# Features
* Emailing functionality
* Authentication and authorization
* User referral and commission program
* Function to update investments without background tasks libraries like celery, redis etc
* Ajax functionalities to communicate to backend without page reload
* Notification features and auto delete functionality
* Beautiful admin dashboard using django-jazzmin
* Error 404 and 500 pages implemented to handle error pages
* Configured to use cloudinary cloud storage to serve media files
* Password reset functionality


# Technologies
* Python
* Django
* Vanilla Javascript
* Ajax


# Pages
Project contains 25+ pages in total outside admin dashboard which includes index, contact, faq, register, login,
dashboard, profile, update password, create investment, invoice, investment history, withdraw, withdraw history, notifications,
affiliates, success, error pages(404 and 500), password reset pages, and email templates.


# Libraries used
// Dependent libraries
python==3.7.0
Django==3.2.2
Pillow==8.0.0
django-cloudinary-storage==0.3.0
python-magic==0.4.25
python-decouple==3.6
django-jazzmin>=2.6.0
reportlab==3.5.50
whitenoise==5.3.0
gunicorn==20.1.0

// Non dependent libraries
psycopg2==2.9.2
dj-database-url==0.5.0
mysqlclient==2.0.3
PyMySQL==1.0.2


# Notes
* To run on cpanel host, some packages are not compatible so older versions of libraries are used
* Pillow, pscopg2, reportlab and mysqlclient(for mySQLdb) had conflicts
* mysqlclient requires an extra setting with PyMySQL library on settings.py
* Error deploying live with django-cloudinary-storage: import error for libmagic for video upload libraries


# Colors
purple - #8e54e9
orange - #8e54e9
