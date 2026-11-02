"""
Festival Admin Configuration
تنظیمات مدیریت جشنواره رسانه ای ابوذر
"""
from .festival import FestivalAdmin
from .judging import JudgeProfileAdmin, ReviewAdmin
from .festival_registration import FestivalRegistrationAdmin
from .work import WorkAdmin
from .categories import (
    FestivalFormatAdmin,
    FestivalTopicAdmin,
    FestivalSpecialSectionAdmin,
)

__all__ = [
    "JudgeProfileAdmin",
    "ReviewAdmin",
    "FestivalAdmin",
    "FestivalRegistrationAdmin",
    "WorkAdmin",
    "FestivalFormatAdmin",
    "FestivalTopicAdmin",
    "FestivalSpecialSectionAdmin",
]
