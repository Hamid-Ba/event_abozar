from django.db.models.signals import post_save
from django.dispatch import receiver

# from wallet.models.wallet import Wallet

from .models import User


# @receiver(post_save, sender=User, dispatch_uid="user_register")
# def after_user_registration(sender, instance, created, **kwargs):
#     """Create Wallet For User after Registration"""
#     if created:
#         wallet = Wallet.objects.create(user=instance)
#         wallet.charge(50000)
#         if not instance.is_staff:
#             Rancher.objects.get_or_create(user=instance)
