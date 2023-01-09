from . import models
import datetime, pytz, time, uuid
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def generateRefCode():
    code = str(uuid.uuid4()).replace("-","")[:6]
    return code



# Function to perform account operations and create notification
def updateAccount(account, action, amount):
    if action == "credit":
        # Adding to account balance
        account.balance += amount
        # Recording the deposit
        deposit = models.Deposit.objects.create(user=account.user, amount=amount)
        deposit.save()
        # Creating notification
        notification = models.Notification.objects.create(
            user=account.user, 
            message=f'${amount} was added to your account. Go to your dashboard to view balance'
        )
    elif action == "debit":
        if amount <= account.total_balance:
            # Merging up account balance and referral balance
            account.balance += account.referral_balance
            account.referral_balance = 0
            # Deducting amount from account balance to fund investment
            account.balance -= amount
            # Creating notification
            notification = models.Notification.objects.create(
                user=account.user, 
                message=f'${amount} was deducted from your balance. Go to your dashboard to view balance'
            )
    account.save()
    notification.save()



# Function to delete old notifications
def deleteOldNotifications(user):
    notifications = models.Notification.objects.filter(user=user)
    today = datetime.datetime.now(tz=pytz.UTC)

    for notification in notifications:
        # Getting number of days the notification has lasted
        notification_period = (today - notification.date).days
        #print(f'notification date: {notification.date} notification period: {notification_period}')
        if notification_period >= 3:
            notification.delete()
        


# Investment process function for load time
def updateInvestment(param):
    account = param.account
    investments = models.Investment.objects.filter(user=param, status="approved")
    
    # We have to loop through investments because user may have one or more approved investments

    for investment in investments:
        current_investment = models.Investment.objects.get(id=investment.id)
        today = datetime.datetime.now(tz=pytz.UTC)

        if  today < current_investment.end_date:
            if today > current_investment.approved_date:
                # Getting number of days after approved date
                days_after_approval = (today - current_investment.approved_date).days
                print(days_after_approval)
                # If days is equal or greater than 1 then multiply daily profits by number of days
                if days_after_approval >= 1:
                    current_investment.returns = current_investment.daily_profit * days_after_approval
                    print(f'current investment returns: {current_investment.returns} where daily profit: {current_investment.daily_profit}')
        # Else if today has reached OR passed end date of investment
        # in other words investment has ended
        elif today >= current_investment.end_date:
            if current_investment.returns != current_investment.roi:
                current_investment.returns = current_investment.roi
                current_investment.status = "completed"
                updateAccount(account, "credit", current_investment.roi)
                # Sending success mail
                try:
                    company = models.CompanyInfo.objects.last()
                    html_content = render_to_string('email_congrats.html', {'investment':investment, 'company':company})
                    email = EmailMessage(f'Congrats.. Your mining package of ${investment.amount} has successfully been completed', html_content, company.email, [investment.user.email,])
                    email.content_subtype = 'html'
                    email.fail_silently = False
                    email.send()
                except Exception as e:
                    print(e)
                # Creating notification of completion
                notification = models.Notification.objects.create(
                    date = current_investment.end_date,
                    user=account.user,
                    message=f'Your mining package ID - {current_investment.investment_id}, amount - {current_investment.amount} has been completed and ${current_investment.roi} has been credited to your balance.'
                )
                notification.save()
        current_investment.save()



def convertTimezone(user):
    '''
    Django by default uses UTC timezone. Since we need to save time based on the various users' geographical location, 
    it is recommended to save time in UTC while reconverting to user's timezone while displaying. You can convert in your 
    views and pass new datetime in your context or you convert on your frontend using javascript or other frontend technologies.
    However note that you cannot save a different timezone from the one set in your settings.py as TIME_ZONE value which is UTC by default
    as django will reconvert back to the default timezone before saving to the database. This is a dummy function to display timezone conversion
    in python/django
    '''
    # todays utc time
    today = datetime.datetime.now(tz=pytz.UTC)
    # converting todays time to designated timezone
    localized_today = today.astimezone(pytz.timezone('Africa/Lagos'))
    # converting todays time according to user's timezone saved in database
    user_localised_time = today.astimezone(pytz.timezone(user.profile.timezone))
    print(f'{today}\n{localized_today}\n{user_localised_time}')




# Investment process function for background services
def runInvestmentProcess(instance):
    '''
    This function is a duplicate of updateInvestment function but developed to run via background after an investment is approved
    using async and backround task running libraries such as celery, celery beats, cronjob and crontab, django-scheduler et cetra.
    so choose whichever function to update investment depending on project requirements
    '''
    # if a saved investment was altered(not created) and status is approved 
    if instance.status == 'approved':
        if instance.returns < instance.amount:
            instance.returns += instance.amount
            instance.save()
    # for each day
    for each_day in range(instance.package.duration_in_days):
        print(instance.returns)
        # checking to make sure investment returns isn't exceeded
        if instance.returns < instance.roi:
            # sleep for 1day = 86400seconds
            time.sleep(86400)
            # accumulate or add profits to investment returns
            instance.returns = instance.returns + instance.daily_profit
            instance.save()
            # checking to see if investment plan is completed
            if instance.returns == instance.roi:
                if instance.status != 'completed':
                    account = models.Account.objects.get(user=instance.user)
                    account.balance += instance.returns
                    account.save()
                    instance.status = 'completed'
                    instance.save()
                    break
