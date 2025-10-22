import os
import re

test_files = [
    "festival/tests/test_user_statistics_api.py",
    "festival/tests/test_statistics_api.py",
    "festival/tests/test_models.py",
]

# Define replacements
replacements = [
    ('festival_format="news_report"', "festival_format=self.format_news"),
    ('festival_format="interview"', "festival_format=self.format_interview"),
    ('festival_format="documentary"', "festival_format=self.format_doc"),
    (
        'festival_format="photo"',
        'festival_format=FestivalFormat.objects.get(code="photo")',
    ),
    ('festival_topic="year_slogan"', "festival_topic=self.topic_slogan"),
    ('festival_topic="jihad_explanation"', "festival_topic=self.topic_jihad"),
    (
        'festival_topic="media_industry"',
        'festival_topic=FestivalTopic.objects.get(code="media_industry")',
    ),
    (
        'festival_topic="family_society"',
        'festival_topic=FestivalTopic.objects.get(code="family_society")',
    ),
    (
        'festival_topic="revolution_achievements"',
        'festival_topic=FestivalTopic.objects.get(code="revolution_achievements")',
    ),
    ('special_section="progress_narrative"', "special_section=self.section_progress"),
    ('special_section="field_narrative_12days"', "special_section=self.section_field"),
]

# First, make sure imports are correct
import_block_old = """from festival.models import FestivalRegistration"""
import_block_new = """from festival.models import (
    FestivalRegistration,
    FestivalFormat,
    FestivalTopic,
    FestivalSpecialSection,
)"""

for file_path in test_files:
    if not os.path.exists(file_path):
        continue

    with open(file_path, "r") as f:
        content = f.read()

    # Fix imports
    if "from festival.models import FestivalRegistration" in content:
        if "FestivalFormat" not in content:
            content = content.replace(import_block_old, import_block_new)

    # Apply all replacements
    for pattern, replacement in replacements:
        content = content.replace(pattern, replacement)

    with open(file_path, "w") as f:
        f.write(content)

    print(f"Fixed {file_path}")

print("Done!")
