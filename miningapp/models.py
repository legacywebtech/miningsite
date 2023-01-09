from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
import datetime, pytz
from .utils import generateRefCode, updateAccount
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decimal import Decimal
# RawMediaCloudinaryStorage for cloudinary document export
from cloudinary_storage.storage import RawMediaCloudinaryStorage




currencies = (
    ('USD', 'USD'),
    ('Bitcoin', 'Bitcoin'),
    ('Ethereum', 'Ethereum'),
    ('Binance', 'Binance'),
    ('Ripple', 'Ripple'),
    ('Dogecoin', 'Dogecoin'),
    ('Litecoin', 'Litecoin'),
    ('Bitcoin cash', 'Bitcoin cash'),
    ('Dash', 'Dash'),
    ('USDT', 'USDT'),
    ('BUSD', 'BUSD'),
    ('Tron', 'Tron'),
    ('Solana', 'Solana'),
    ('Cardano', 'Cardano')
)


# Create your models here.

# Manager class for custom user
class UserManager(BaseUserManager):
    # Determines how to create our user model and validations
    def create_user(self, email, first_name, last_name, password=None):
        # Use this check for as many field you want
        if not email:
            raise ValueError("email is required")
        if not first_name:
            raise ValueError("provide a first name")
        if not last_name:
            raise ValueError("provide a last name")


        user = self.model(
            # normalize_email ensures our email is properly formatted
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
        )
        # Setting password for user
        user.set_password(password)
        # Saving user to database
        user.save(using=self._db)
        # Creating welcome message For user
        notification = Notification.objects.create(user=user, message=f'Hello {user.first_name}, Your account setup was successful. Create a mining package to start mining and earning')
        notification.save()
        # Return user after saving
        return user

    # Determines how to create superuser
    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            password = password
        )
        # Granting permissions to the super user
        user.is_staff = True
        user.is_superuser = True
        # Saving user to database
        user.save(using=self._db)
        # Return user after saving
        return user
    

    '''
    Make sure to set this manager as the manager in your custom model
    objects = MyUserManager()
    '''



# Custom user model class
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(verbose_name="first name", max_length=60)
    last_name = models.CharField(verbose_name="last name", max_length=60)
    username = models.CharField(verbose_name="username", max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField(verbose_name="email address", max_length=60, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    @property
    def fullname(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        if self.user.fullname:
            name = self.user.fullname
        elif self.user.username:
            name = self.user.username
        elif self.user.email:
            name = self.user.email
        else:
            name = '-'
        return name

    # Setting to determing what field to use as login parameter
    USERNAME_FIELD = "email"

    # Setting to set required fields
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # Setting a manager for this custom user model
    objects = UserManager()

    # Setting to determine what field to show on our database
    def __str__(self):
        return self.fullname

    # Determines if signup user has permissions
    def has_perm(self, perm, obj=None):
        return True

    # Determines if the signed up user will have acccess to other models
    # In our app or project
    def has_module_perms(self, app_label):
        return True

    # Function to get url per user for sitemapping
    def get_absolute_url(self):
        return f'/profile/{self.id}'

    '''
    Make sure to set this custom model as our user model in settings.py
    AUTH_USER_MODEL = "App.CustomUserModel"
    Make sure to delete previous migration files incase of errors
    Then make migrations
    '''



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    profile_pic = models.ImageField(upload_to="images/profiles", null=True, blank=True)
    location = models.CharField(max_length=160, null=True, blank=True, help_text="country/state")
    timezone = models.CharField(max_length=160, null=True, blank=True)
    ref_code = models.CharField(verbose_name="referral code", max_length=30, unique=True, null=True, blank=True)
    upline = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="upline", related_name="upline")
    downlines = models.ManyToManyField(User, verbose_name="referred", related_name="downlines", blank=True)

    def save(self, *args, **kwargs):
        if self.ref_code == "" or self.ref_code == None or self.ref_code == ' ':
            code = generateRefCode()
            self.ref_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user.fullname:
            name = self.user.fullname
        elif self.user.username:
            name = self.user.username
        elif self.user.email:
            name = self.user.email
        elif self.ref_code:
            name = self.ref_code
        else:
            name = '-'
        return name



class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=False, blank=False)
    referral_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=False, blank=False)

    @property
    # Function to return TOTAL ACCOUNT BALANCE
    def total_balance(self):
        return round(self.balance + self.referral_balance, 2)

    @property
    # Function to return CURRENT ACTIVE/APPROVED INVESTMENTS' RETURNS
    def active_investments(self):
        investments = Investment.objects.filter(user=self.user, status='approved')
        total = sum([item.returns for item in investments])
        return  round(total, 2)

    @property
    # Function to return TOTAL AMOUNT OF ALL PENDING/UNAPPROVED INVESTMENTS
    def pending_investments(self):
        investments = Investment.objects.filter(user=self.user, status='pending')
        total = sum([item.amount for item in investments])
        return  round(total, 2)

    @property
    # Function to return TOTAL RETURNS OF ACTIVE & COMPLETED INVESTMENTS
    def total_investments(self):
        approved_investments = Investment.objects.filter(user=self.user, status='approved')
        completed_investments = Investment.objects.filter(user=self.user, status='completed')
        investments = list(approved_investments) + list(completed_investments)
        total = sum([item.returns for item in investments])
        return  round(total, 2)

    @property
    # Function to return TOTAL PENDING WITHDRAWALS
    def pending_withdrawals(self):
        withdrawals = Withdraw.objects.filter(user=self.user, status='pending')
        total = sum([item.amount for item in withdrawals])
        return  round(total, 2)

    @property
    # Function to return TOTAL COMPLETED WITHDRAWALS
    def completed_withdrawals(self):
        withdrawals = Withdraw.objects.filter(user=self.user, status='approved')
        total = sum([item.amount for item in withdrawals])
        return  round(total, 2)

    def __str__(self):
        if self.user.fullname:
            name = self.user.fullname
        elif self.user.username:
            name = self.user.username
        elif self.user.email:
            name = self.user.email
        else:
            name = ''
        return name



class CompanyInfo(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    site_domain = models.CharField(max_length=150, blank=False, null=False, help_text="site url/link i.e miningsite.com")
    logo = models.ImageField(upload_to="images/company", blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    whatsapp_link  = models.URLField(max_length=200, blank=True, null=True)
    facebook_link  = models.URLField(max_length=200, blank=True, null=True)
    instagram_link  = models.URLField(max_length=200, blank=True, null=True)
    twitter_link  = models.URLField(max_length=200, blank=True, null=True)
    linked_in = models.URLField(max_length=200, blank=True, null=True)
    youtube_link = models.URLField(max_length=200, blank=True, null=True)
    certificate = models.ImageField(upload_to="images/company", blank=True, null=True)
    document = models.FileField(upload_to='document', blank=True, null=True, storage=RawMediaCloudinaryStorage())
    video = models.URLField(max_length=1250, blank=True, null=True)
    youtube_video = models.CharField(max_length=500, blank=True, null=True, help_text='Youtube embedded video code')
    bitcoin_address = models.CharField(max_length=200, blank=True, null=True)
    ethereum_address = models.CharField(max_length=200, blank=True, null=True)
    litecoin_address = models.CharField(max_length=200, blank=True, null=True)
    bitcoincash_address = models.CharField(max_length=200, blank=True, null=True)
    binance_address = models.CharField(max_length=200, blank=True, null=True)
    dogecoin_address = models.CharField(max_length=200, blank=True, null=True)
    dashcoin_address = models.CharField(max_length=200, blank=True, null=True)
    usdt_trc20_address = models.CharField(max_length=200, blank=True, null=True)
    usdt_erc20_address = models.CharField(max_length=200, blank=True, null=True)
    usdt_bep20_address = models.CharField(max_length=200, blank=True, null=True)
    busd_address = models.CharField(max_length=200, blank=True, null=True)
    tron_address = models.CharField(max_length=200, blank=True, null=True)
    xrp_address = models.CharField(max_length=200, blank=True, null=True)
    solana_address = models.CharField(max_length=200, blank=True, null=True)
    cordano_address = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id and CompanyInfo.objects.exists():
            raise ValueError("This model cannot have two or more records")
        else:
            super().save(*args, **kwargs)




class LastDeposit(models.Model):
    date = models.DateField(blank=False)
    name = models.CharField(max_length=150, blank=False)
    amount = models.PositiveSmallIntegerField(blank=False)
    currency = models.CharField(max_length=50, choices=currencies, blank=False)

    def __str__(self):
        return f'{str(self.date)} {self.name} {str(self.amount)} {self.currency}'

    
    def save(self, *args, **kwargs):
        if len(LastDeposit.objects.all()) > 30:
            raise ValueError("This model cannot have more than 30 records")
        else:
            super().save(*args, **kwargs)



class LastWithdraw(models.Model):
    date = models.DateField(blank=False)
    name = models.CharField(max_length=150, blank=False)
    amount = models.PositiveSmallIntegerField(blank=False)
    currency = models.CharField(max_length=50, choices=currencies, blank=False)

    def __str__(self):
        return f'{str(self.date)} {self.name} {str(self.amount)} {self.currency}'

    
    def save(self, *args, **kwargs):
        if len(LastDeposit.objects.all()) > 30:
            raise ValueError("This model cannot have more than 30 records")
        else:
            super().save(*args, **kwargs)




class Package(models.Model):
    package = models.CharField(max_length=25, unique=True, blank=False, null=False)
    daily_profit_percentage = models.DecimalField(max_digits=3, decimal_places=1, blank=False, null=False, help_text="in percentage(%)")
    minimum_amount = models.PositiveIntegerField(blank=False, null=False)
    maximum_amount = models.PositiveIntegerField(blank=False, null=False)
    referral_commission = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(0, 100)], default=10, blank=False, null=False, help_text="in percentage %")
    duration_in_days = models.PositiveSmallIntegerField(blank=False, null=False, help_text="in_days")

    def __str__(self):
        return self.package

    @property
    def duration(self):
        period = ['week', 'month', 'year']
        if self.duration_in_days == 7:
            return f'1 {period[0]}'
        elif self.duration_in_days == 14:
            return f'2 {period[0]}s'
        elif self.duration_in_days == 30:
            return f'1 {period[1]}'
        elif self.duration_in_days == 60:
            return f'2 {period[1]}s'
        elif self.duration_in_days == 90:
            return f'3 {period[1]}s'
        elif self.duration_in_days == 180:
            return f'6 {period[1]}s'
        elif self.duration_in_days == 360:
            return f'1 {period[2]}'



class Investment(models.Model):
    status = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('completed', 'Completed')
    )
    date = models.DateTimeField(auto_now_add=True)
    investment_id = models.CharField(max_length=12, blank=False, null=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=60, null=False, blank=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    status = models.CharField(max_length=60, choices=status, default='pending')
    returns = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=False, blank=False)
    approved_date = models.DateTimeField(null=True, blank=True)
    end_date =  models.DateTimeField(null=True, blank=True, help_text="This field is calculated and depends on approved date")

    def __str__(self):
        return str(self.id)

    # This function performs a task while saving
    def save(self, *args, **kwargs):
        if self.status == 'pending':
            super().save(*args, **kwargs)
        elif self.status == 'completed':
            super().save(*args, **kwargs)
        elif self.status == 'approved':
            if not self.approved_date:
                '''
                * Remember that if we don't have an approved date then it's the first time we are 
                approving the investment and that's when we want to carry out all activities
                * Becareful of identations else alot will break
                '''
                # Setting approved date to current date and time
                self.approved_date = datetime.datetime.now(tz=pytz.UTC)
                # Setting end date to date and time after package duration from approved date
                self.end_date = self.approved_date + datetime.timedelta(days=self.package.duration_in_days)
                # Sending approval mail
                try:
                    company = CompanyInfo.objects.last()
                    html_content = render_to_string('email_approved.html', {'investment':Investment.objects.get(id=self.id), 'company':company})
                    email = EmailMessage(f'Dear {self.user.first_name}, your mining package of ${self.amount} and ID {self.investment_id} has been approved', html_content, company.email, [self.user.email,])
                    email.content_subtype = 'html'
                    email.fail_silently = False
                    email.send()
                except Exception as e:
                    print(e)
                # Notifying user of approved investment
                notification = Notification.objects.create(user=self.user, message=f"Your investment of ${self.amount}({self.payment_method}) and ID - {self.investment_id} has successfully been approved")
                notification.save()
                # Adding referral commission to upline
                if self.user.profile.upline:
                    commission = round(Decimal(self.package.referral_commission/100) * self.amount, 2)
                    upliner_account = Account.objects.get(user=self.user.profile.upline)
                    upliner_account.referral_balance += commission
                    upliner_account.save()
            # Saving
            super().save(*args, **kwargs)
        elif self.status == 'declined':
            updateAccount(self.user.account, "credit", self.amount)
            investment = Investment.objects.get(id=self.id)
            investment.delete()
        
    @property
    # This defines the percentage daily profit returns
    def daily_profit_percentage(self):
        return self.package.daily_profit_percentage

    @property
    # This defines daily profit for investment amount
    def daily_profit(self):
        daily_profit = (self.daily_profit_percentage/100) * self.amount
        return round(daily_profit, 2)

    @property
    # This defines daily profit for investment amount
    def total_profit(self):
        total_profit = self.daily_profit * self.package.duration_in_days
        return round(total_profit, 2)
        
    @property
    # This is investment amount + profits
    def roi(self):
        return round(self.amount + self.total_profit, 2)

    @property
    # This is the amount that accumulates for investor
    # for each duration day
    def daily_roi(self):
        return round(self.roi/self.package.duration_in_days, 2)

    # Payment address to be used for investment
    @property
    def payment_address(self):
        company = CompanyInfo.objects.last()

        if self.payment_method == 'BITCOIN':
            address = company.bitcoin_address
        elif self.payment_method == 'ETHEREUM':
            address = company.ethereum_address
        elif self.payment_method == 'BINANCE':
            address = company.binance_address
        elif self.payment_method == 'USDT-TRC20':
            address = company.usdt_trc20_address
        elif self.payment_method == 'USDT-ERC20':
            address = company.usdt_erc20_address
        elif self.payment_method == 'USDT-BEP20':
            address = company.usdt_bep20_address
        elif self.payment_method == 'BUSD':
            address = company.busd_address
        elif self.payment_method == 'TRON':
            address = company.tron_address
        elif self.payment_method == 'LITECOIN':
            address = company.litecoin_address
        elif self.payment_method == 'BITCOIN CASH':
            address = company.bitcoincash_address
        elif self.payment_method == 'DOGECOIN':
            address = company.dogecoin_address
        elif self.payment_method == 'XRP':
            address = company.xrp_address
        elif self.payment_method == 'SOLANA':
            address = company.solana_address
        elif self.payment_method == 'CARDANO':
            address = company.cordano_address
        elif self.payment_method == 'DASHCOIN':
            address = company.dashcoin_address
        return address



class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date)



class Withdraw(models.Model):
    status = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=60, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    payment_address = models.CharField(max_length=60, null=True, blank=True)
    network = models.CharField(max_length=60, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, blank=False, choices=status, default='pending')

    def __str__(self):
        return str(self.date)

    # Function to run while saving model instance
    def save(self, *args, **kwargs):
        if self.status == 'pending':
            super().save(*args, **kwargs)
        elif self.status == 'approved':
            updateAccount(self.user.account, "debit", self.amount)
            super().save(*args, **kwargs)
        elif self.status == 'declined':
            updateAccount(self.user.account, "credit", self.amount)
            withdrawal = Withdraw.objects.get(id=self.id)
            withdrawal.delete()
            notification = Notification.objects.create(
                user=self.user, 
                message=f"Your withdrawal request of ${self.amount} was declined"
            )
            notification.save()
   


class Message(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    location = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=100, null=False, blank=False)
    subject = models.CharField(max_length=100, null=False, blank=False)
    message = models.TextField(max_length=3000, null=False, blank=False)
    date_received = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.date_received}'



class Notification(models.Model):
    date  = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    message = models.TextField(max_length=5000, null=False, blank=False)

    def __str__(self):
        return str(self.date)
