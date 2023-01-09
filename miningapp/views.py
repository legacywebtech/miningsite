from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse_lazy
from .models import *
from .utils import updateInvestment, deleteOldNotifications
from decimal import Decimal
import json
# Mailing imports
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Auth imports
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
# Report lab imports
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter



# Create your views here.

def index(request):
    company = CompanyInfo.objects.last()
    packages = Package.objects.all()
    last_deposits = LastDeposit.objects.all().order_by('-date')[:10]
    last_withdraws = LastWithdraw.objects.all().order_by('-date')[:10]

    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST['location']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        try:
            email.index('@') and email.index('.')
        except ValueError:
            messages.info(request, 'Your email is not valid')
        else:
            try:
                html_content = render_to_string('email_template.html', {'subject':subject, 'message':message, 'company':company})
                email = EmailMessage(subject, html_content, email, [company.email, settings.EMAIL_HOST_USER])
                email.content_subtype = 'html'
                email.fail_silently = False
                email.send()
                print(f'Successfully sent...')
            except Exception as e:
                print(e)
            message = Message.objects.create(name=name, location=location, email=request.POST['email'], subject=subject, message=message)
            message.save()
            messages.success(request, 'Your message was sent successfully')
    contexts = {'company':company, 'packages':packages, 'last_deposits': last_deposits, 'last_withdraws': last_withdraws}
    return render(request, 'index.html', contexts)



def register(request):
    company = CompanyInfo.objects.last()

    if request.method == "POST":
        if 'register-submit' in request.POST:
            email = request.POST['email']
            first_name = request.POST['first-name']
            last_name = request.POST['last-name']
            location = request.POST['location']
            timezone = request.POST['timezone']
            password1 = request.POST['password1']
            password2 = request.POST['password2']

            if password2 == password1:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Sorry this email has already been taken!')
                else:
                    if len(password2) >= 5:
                        # Saving user and user instances
                        user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, password=password2)
                        user.save()
                        # On user save, a profile instance is created dynamically from signals.py
                        # Fetching profile of user created from signals.py to update upliner
                        profile = Profile.objects.get(user=user)
                        # Setting timezone of user
                        profile.timezone = timezone
                        # Checking if user allowed location
                        if location != '' or location != ' ':
                            profile.location = location
                        profile.save()
                        # Send success email
                        try:
                            html_content = render_to_string('email_welcome.html', {'user':user, 'company':company})
                            email = EmailMessage(f'{user.first_name}, your account was successfully created', html_content, company.email, [user.email,])
                            email.content_subtype = 'html'
                            email.fail_silently = False
                            email.send()
                        except Exception as e:
                            print(e)
                        messages.success(request, f'{user.first_name}, your account has successfully been created... you can now sign in!')
                        return redirect('mining:login')
                    else:
                        messages.error(request, 'Password length cannot be less than 7... Please try again')
            else:
                messages.error(request, 'Passwords does not match... Please try again')
    return render(request, 'register.html', {'company':company})



def uplineRegister(request, refcode):
    try:
        upline = Profile.objects.get(ref_code=refcode)
    except:
        return redirect('mining:register')
    
    company = CompanyInfo.objects.last()

    if request.method == "POST":
        if 'register-submit' in request.POST:
            email = request.POST['email']
            first_name = request.POST['first-name']
            last_name = request.POST['last-name']
            location = request.POST['location']
            timezone = request.POST['timezone']
            password1 = request.POST['password1']
            password2 = request.POST['password2']

            if password2 == password1:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Sorry this email has already been taken!')
                else:
                    if len(password2) >= 5:
                        # Saving user and user instances
                        user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, password=password2)
                        user.save()
                        # On user save, a profile instance is created dynamically from signals.py
                        # Fetching profile of user created from signals.py to update upliner
                        profile = Profile.objects.get(user=user)
                        profile.upline = upline.user
                        # Setting timezone of user
                        profile.timezone = timezone
                        # Checking if user allowed location
                        if location != '' or location != ' ':
                            profile.location = location
                        profile.save()
                        # Updating downlines for upline
                        upline.downlines.add(user)
                        upline.save()
                        # Send success email
                        try:
                            html_content = render_to_string('email_welcome.html', {'user':user, 'company':company})
                            email = EmailMessage(f'{user.first_name}, your account was successfully created', html_content, company.email, [user.email,])
                            email.content_subtype = 'html'
                            email.fail_silently = False
                            email.send()
                        except Exception as e:
                            print(e)
                        messages.success(request, f'{user.first_name}, your account has successfully been created... you can now sign in!')
                        return redirect('mining:login')
                    else:
                        messages.error(request, 'Password length cannot be less than 5... Please try again')
            else:
                messages.error(request, 'Passwords does not match... Please try again')
    return render(request, 'register.html', {'company': company,'upline':upline})



def login(request):
    company = CompanyInfo.objects.last()

    if request.method == "POST":
        if 'login-submit' in request.POST:
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('/account/')
            else:
                messages.error(request, 'Invalid credentials..   Please try again')
    return render(request, 'login.html', {'company':company})



def logout(request):
    auth.logout(request)
    return redirect('/')



def about(request):
    company = CompanyInfo.objects.last()
    return render(request, 'about.html', {'company':company})



def faq(request):
    company = CompanyInfo.objects.last()
    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST['location']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        try:
            email.index('@') and email.index('.')
        except ValueError:
            messages.info(request, 'Your email is not valid')
        else:
            try:
                html_content = render_to_string('email_template.html', {'subject':subject, 'message':message, 'company':company})
                email = EmailMessage(subject, html_content, email, [company.email, settings.EMAIL_HOST_USER])
                email.content_subtype = 'html'
                email.fail_silently = False
                email.send()
                print(f'Successfully delivered... Response will be sent shortly')
            except Exception as e:
                print(e)
            message = Message.objects.create(name=name, location=location, email=request.POST['email'], subject=subject, message=message)
            message.save()
            messages.success(request, 'Successfully delivered... Response will be sent shortly')
    return render(request, 'faq.html', {'company':company})



def team(request):
    company = CompanyInfo.objects.last()
    return render(request, 'team.html', {'company':company})



def reviews(request):
    company = CompanyInfo.objects.last()
    return render(request, 'reviews.html', {'company':company})



def plans(request):
    company = CompanyInfo.objects.last()
    packages = Package.objects.all()
    last_deposits = LastDeposit.objects.all().order_by('-date')[:10]
    last_withdraws = LastWithdraw.objects.all().order_by('-date')[:10]
    contexts = {'company':company, 'packages':packages, 'last_deposits': last_deposits, 'last_withdraws': last_withdraws}
    return render(request, 'plans.html', contexts)



def tac(request):
    company = CompanyInfo.objects.last()
    return render(request, 'tac.html', {'company':company})



def contact(request):
    company = CompanyInfo.objects.last()
    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST['location']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        try:
            email.index('@') and email.index('.')
        except ValueError:
            messages.info(request, 'Your email is not valid')
        else:
            try:
                html_content = render_to_string('email_template.html', {'subject':subject, 'message':message, 'company':company})
                email = EmailMessage(subject, html_content, email, [company.email, settings.EMAIL_HOST_USER])
                email.content_subtype = 'html'
                email.fail_silently = False
                email.send()
                print(f'Successfully sent...')
            except Exception as e:
                print(e)
            message = Message.objects.create(name=name, location=location, email=request.POST['email'], subject=subject, message=message)
            message.save()
            messages.success(request, 'Your message was sent successfully')
    return render(request, 'contact.html', {'company':company})



@login_required
def account(request):
    # run check and update investments
    updateInvestment(request.user)
    company = CompanyInfo.objects.last()
    account = Account.objects.get(user=request.user)
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    

    # checking for active mining to display mining animation on frontend or not
    if Investment.objects.filter(user=request.user, status="approved").exists():
        mining = True
    else:
        mining = False

    context = {
        'company':company,
        'notifications':notifications,
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications,
        'account': account,
        'mining': mining,
    }
    return render(request, 'dashboard.html', context)



@login_required
def profile(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    user = request.user
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]

    if request.method == 'POST':
        if 'profile-pic-submit' in request.POST:
            if 'picture' in request.FILES:
                pic = request.FILES['picture']

                profile = Profile.objects.get(user=request.user.id)
                profile.profile_pic = pic
                profile.save()
                messages.success(request, 'Profile picture successfully updated!')
        elif 'update-user-submit' in request.POST:
            first_name = request.POST['first-name'] or None
            last_name = request.POST['last-name'] or None
            email = request.POST['email'] or None
            timezone = request.POST['timezone']

            if email=='' or email==None:
                email = request.user.email

            if first_name=='' or first_name==None:
                first_name = request.user.first_name

            if last_name=='' or last_name==None:
                last_name = request.user.last_name


            user = User.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            # Updating user timezone
            profile = user.profile
            profile.timezone = timezone
            profile.save()
            messages.success(request, 'Details successfully updated')
            return redirect('mining:profile')
    context = {
        'user':user, 
        'company':company, 
        'notifications':notifications,
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'profile.html', context)



class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('mining:password_change_success')



@login_required
def passwordChangeSuccess(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    context = {
        'company':company,
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications
    }
    return render(request, 'success.html', context)



@login_required
def investHistory(request):
    # run check and update investments
    updateInvestment(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    user_investments = Investment.objects.filter(user=request.user).order_by('-date')
    p = Paginator(user_investments, 10)
    page = request.GET.get('page')
    investments = p.get_page(page)
    page_list = range(1, investments.paginator.num_pages + 1)
    context = {
        'company':company, 
        'notifications':notifications,
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications,
        'investments':investments,
        'page_list': page_list
    }
    return render(request, 'investment_history.html', context)



@login_required
def investmentDetail(request, investment_id):
    # run check and update investments
    updateInvestment(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    investment = get_object_or_404(Investment, investment_id=investment_id)
    context = {
        'company':company, 
        'notifications':notifications,
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications,
        'investment':investment
    }
    return render(request, 'investment_detail.html', context)



@login_required
def withdrawalHistory(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    user_withdrawals = Withdraw.objects.filter(user=request.user).order_by('-date')
    p = Paginator(user_withdrawals, 10)
    page = request.GET.get('page')
    withdrawals = p.get_page(page)
    page_list = range(1, withdrawals.paginator.num_pages + 1)
    context = {
        'company': company,
        'notifications': notifications, 
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications,
        'withdrawals':withdrawals,
        'page_list': page_list
    }
    return render(request, 'withdrawal_history.html', context)



@login_required
def withdrawalAssets(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    account = Account.objects.get(user=request.user)

    if request.method == 'POST':
        if 'withdraw-submit' in request.POST:
            payment_method = request.POST['method']
            payment_addresss = request.POST['address']
            amount = int(request.POST['amount'])
            network = request.POST['network']

            if not network or network == '':
                network = None

            if amount <= account.total_balance:
                try:
                    withdraw_request = Withdraw.objects.create(
                        user=request.user,
                        payment_method=payment_method,
                        amount=amount,
                        payment_address=payment_addresss,
                        network=network
                    )
                    withdraw_request.save()
                    messages.success(request, 'Withdraw request was successsfully placed')
                except Exception as e:
                    print(e)
                    messages.error(request, e)
            else:
                messages.error(request, 'Insufficient funds...')
    context = {
        'company':company, 
        'notifications':notifications,
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'withdraw_assets.html', context)



@login_required
def createInvest(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    packages = Package.objects.all()
    context = {
        'company':company, 
        'notifications': notifications, 
        'total_notifications': total_notifications,
        'recent_notifications': recent_notifications,
        'packages':packages
    }
    return render(request, 'create_invest.html', context)



@login_required
def invoice(request, investment_id):
    # run check and update investments
    updateInvestment(request.user)
    investment = get_object_or_404(Investment, investment_id=investment_id)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]

    context = {
        'company':company,
        'notifications':notifications,
        'recent_notifications': recent_notifications,
        'total_notifications':total_notifications,
        'investment':investment, 
    }
    return render(request, 'invoice.html', context)



@login_required
def affiliates(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user)
    total_notifications = notifications.count
    recent_notifications = notifications.order_by('-date')[:5]
    profile = Profile.objects.get(user=request.user)
    p = Paginator(profile.downlines.all(), 10)
    page = request.GET.get('page')
    downlines = p.get_page(page)
    context = {
        'company':company, 
        'notifications':notifications, 
        'recent_notifications':recent_notifications, 
        'total_notifications':total_notifications,
        'downlines':downlines
    }
    return render(request, 'affiliates.html', context)



def notifications(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user).order_by('-date')
    total_notifications = notifications.count
    recent_notifications = notifications[:5]
    p = Paginator(notifications, 10)
    page = request.GET.get('page')
    notifications = p.get_page(page)
    page_list = range(1, notifications.paginator.num_pages + 1)
    context = {
        'company':company, 
        'notifications':notifications, 
        'recent_notifications':recent_notifications,
        'total_notifications':total_notifications,
        'page_list': page_list
    }
    return render(request, 'notifications.html', context)



def error404(request, exception):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user).order_by('-date')[:5]
    context = {'company':company, 'notifications':notifications}
    return render(request, 'error404.html', context)



def error500(request):
    # delete notifications of user > 3days
    deleteOldNotifications(request.user)
    company = CompanyInfo.objects.last()
    notifications = Notification.objects.filter(user=request.user).order_by('-date')[:5]
    context = {'company':company, 'notifications':notifications}
    return render(request, 'error500.html', context)



# Pseudo views

# View to start new mining investment
def processInvestment(request):
    company = CompanyInfo.objects.last()
    data = json.loads(request.body)
    investment_id = data['investment']['id']
    package_id = int(data['investment']['package'])
    payment = data['investment']['payment']
    amount = data['investment']['amount']
    package = Package.objects.get(id=package_id)
    
    try:
        investment = Investment.objects.create(
            investment_id = investment_id,
            user = request.user,
            package = package,
            payment_method = payment,
            amount = amount
        )
        investment.save()

        # Send success mail for placing investment
        try:
            html_content = render_to_string('email_investment.html', {'investment':investment, 'company':company})
            email = EmailMessage(f'Your mining package ${investment.amount} was successfully placed', html_content, company.email, [request.user.email,])
            email.content_subtype = 'html'
            email.fail_silently = False
            email.send()
            print('mailing successful')
        except Exception as e:
            print('error while mailing: ', e)

        response = {
            'status': 'success',
            'message': 'Mining package was successfully placed',
            'invoice-url': f'/account/invest/invoice/{investment.investment_id}/'
        }
    except Exception as e:
        print(e)
        response = {
            'status': 'error',
            'message': 'Sorry there was an error while placing mining package',
            'error-message': e
        }
    return JsonResponse(response, safe=False)


# View to invest from account balance
def investFromBalance(request):
    data = json.loads(request.body)
    investment_id = data['investment']['id']
    amount = Decimal(data['investment']['amount'])
    account = Account.objects.get(user=request.user)
    investment = Investment.objects.get(investment_id=investment_id)

    if amount <= account.total_balance:
        if investment.status != "approved":
            updateAccount(account, "debit", amount)
            # Approving investment since user balance has sufficient funds
            investment.status = "approved"
            investment.save()
            
            response = {
                'status': 'success',
                'message': "Mining has been successfully approved and started",
            }
        else:
            response = {
                'status': 'error',
                'message': "Mining has already been approved",
            }
    else:
        response = {
            'status': 'error',
            'message': "Insufficient funds",
        }

    return JsonResponse(response, safe=False)


# view to alert admins of payment
def confirmPayment(request):
    data = json.loads(request.body)
    company = CompanyInfo.objects.last()
    investment = Investment.objects.get(investment_id=int(data['id']))
    subject = f'PAYMENT CONFIRMATION FOR INVESTMENT {investment.investment_id}'
    message = f'Hello Admin, you have an investment confirmation request to process with the following details:<br><br>*Investment ID - {investment.investment_id}<br><hr>*Payment Method - {investment.payment_method}<br><hr>*Amount - {investment.amount}<br><hr>*Date/Time - {investment.date}<br><hr><br><br>'

    # Trying to notify company or admins via mail
    try:
        html_content = render_to_string('email_template.html', {'subject':subject, 'message':message, 'company':company})
        email = EmailMessage(subject, html_content, request.user.email, [company.email, settings.EMAIL_HOST_USER])
        email.content_subtype = 'html'
        email.fail_silently = False
        email.send()
        print(f'Message was successfully sent to admins...')
    except Exception as e:
        print(e)
    message = Message.objects.create(name=request.user.fullname, email=request.user.email, subject=subject, message=message)
    message.save()
    return JsonResponse("Your payment would be confirmed and updated... check back later", safe=False)


# view to allow users download investment info in PDF
def investmentPDF(request, investment_id):
    company = CompanyInfo.objects.last()
    #Get investment
    investment = get_object_or_404(Investment, investment_id=investment_id)
    #Create Bytestream buffer
    buf = io.BytesIO()
    #create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    #create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 12)

    # Converting investment date according to user timezone
    date = investment.date.astimezone(pytz.timezone(investment.user.profile.timezone)).strftime("%b %d %Y %H:%M:%S") #.strftime("%d/%m/%Y, %H:%M:%S")

    if investment.status == 'approved':
        # Converting investment approval and end dates according to user timezone
        approved_date = investment.approved_date.astimezone(pytz.timezone(investment.user.profile.timezone)).strftime("%b %d %Y %H:%M:%S")
        end_date = investment.end_date.astimezone(pytz.timezone(investment.user.profile.timezone)).strftime("%b %d %Y %H:%M:%S")

        #Add lines of text
        lines = [
        f'{company.name}',
        '',
        '===============================================================',
        '',
        'Mining details',
        '',
        '* Issued date: ' + str(date),
        '',
        '* Mining ID: ' + investment.investment_id,
        '',
        '* Investor name: ' + investment.user.fullname,
        '',
        '* Investor email: ' + investment.user.email,
        '',
        '* Mining package: ' + investment.package.package,
        '',
        '* Mining amount: $' + str(investment.amount),
        '',
        '* Mining daily profit: $' + str(investment.daily_profit),
        '',
        '* Mining total profits: $' + str(investment.total_profit),
        '',
        '* Mining returns: $' + str(investment.roi),
        '',
        '* Mining current returns: $' + str(investment.returns),
        '',
        '* Mining duration: ' + str(investment.package.duration_in_days) + 'days',
        '',
        '* Mining status: ' + investment.get_status_display(),
        '',
        '* Mining approved date: ' + str(approved_date),
        '',
        '* Mining end date: ' + str(end_date),
        '',
        '===============================================================',
        '',
        ]
    else:
        #Add lines of text
        lines = [
        f'{company.name}',
        '',
        '===============================================================',
        '',
        'Mining details',
        '',
        '* Issued date: ' + str(date),
        '',
        '* Mining ID: ' + investment.investment_id,
        '',
        '* Investor name: ' + investment.user.fullname,
        '',
        '* Investor email: ' + investment.user.email,
        '',
        '* Mining package: ' + investment.package.package,
        '',
        '* Mining amount: $' + str(investment.amount),
        '',
        '* Mining daily profit: $' + str(investment.daily_profit),
        '',
        '* Mining total profits: $' + str(investment.total_profit),
        '',
        '* Mining returns: $' + str(investment.roi),
        '',
        '* Mining current returns: $' + str(investment.returns),
        '',
        '* Mining duration: ' + str(investment.package.duration_in_days) + 'days',
        '',
        '* Mining status: ' + investment.get_status_display(),
        '',
        '===============================================================',
        '',
        ]

    for line in lines:
        textob.textLine(line)
     
    #finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=f'mining-{investment.investment_id}.pdf')