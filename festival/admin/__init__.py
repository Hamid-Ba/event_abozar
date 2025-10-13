"""
Festival Admin Configuration
تنظیمات مدیریت جشنواره رسانه ای ابوذر
"""
from .festival_registration import FestivalRegistrationAdmin
from .work import WorkAdmin

__all__ = ["FestivalRegistrationAdmin", "WorkAdmin"]
