from django.urls import path
from . import views
from .views import PasswordsChangeView

app_name='mining'
urlpatterns = [
    # Page urls and paths
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('reviews/', views.reviews, name='reviews'),
    path('team/', views.team, name='team'),
    path('tac/', views.tac, name='tac'),
    path('plans/', views.plans, name='plans'),
    path('account/', views.account, name='account'),
    path('account/login/', views.login, name='login'),
    path('account/logout/', views.logout, name='logout'),
    path('account/register/', views.register, name='register'),
    path('account/register/<str:refcode>/', views.uplineRegister, name='upline_register'),
    path('account/mining-history/',views.investHistory, name='invest_history'),
    path('account/mining/<str:investment_id>/',views.investmentDetail, name='investment_detail'),
    path('account/withdrawal-history/', views.withdrawalHistory, name='withdrawal_history'),
    path('account/withdraw/', views.withdrawalAssets, name='withdraw'),
    path('account/invest/', views.createInvest, name='invest'),
    path('account/invest/invoice/<str:investment_id>/', views.invoice, name='invoice'),
    path('account/profile/', views.profile, name='profile'),
    path('account/affiliates/', views.affiliates, name='affiliates'),
    path('account/notifications/', views.notifications, name='notifications'),
    path('account/change-password/', PasswordsChangeView.as_view(template_name="change_password.html")),
    path('account/change-password/success/', views.passwordChangeSuccess, name="password_change_success"),

    # Pseudo views
    path('process_investment/', views.processInvestment, name='process_investment'),
    path('invest_from_balance/', views.investFromBalance, name='invest_from_balance'),
    path('confirm_payment/', views.confirmPayment, name='confirm_payment'),
    path('investment-pdf/<str:investment_id>/', views.investmentPDF, name='investment_pdf'),
]