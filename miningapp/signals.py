from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile, Account


@receiver(post_save, sender=User)
def build_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Account.objects.create(user=instance)
        
@receiver(post_save, sender=User)       
def save_profile(sender, instance, created, **kwargs):
    instance.account.save()
    instance.profile.save()

'''
@receiver(post_save, sender=Investment)
def build_investment(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        a_runInvestmentProcess = sync_to_async(runInvestmentProcess, thread_sensitive=False)
        asyncio.create_task(loop.run_until_complete(a_runInvestmentProcess(instance)))
    print("completed.... running tasks via backgound")
'''

