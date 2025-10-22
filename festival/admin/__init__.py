"""
Festival Admin Configuration
تنظیمات مدیریت جشنواره رسانه ای ابوذر
"""
from .festival_registration import FestivalRegistrationAdmin
from .work import WorkAdmin
from .categories import (
    FestivalFormatAdmin,
    FestivalTopicAdmin,
    FestivalSpecialSectionAdmin,
)

__all__ = [
    "FestivalRegistrationAdmin",
    "WorkAdmin",
    "FestivalFormatAdmin",
    "FestivalTopicAdmin",
    "FestivalSpecialSectionAdmin",
]
