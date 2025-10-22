import re

# Read the file
with open("festival/tests/test_api.py", "r") as f:
    content = f.read()

# Define replacements for FestivalRegistration.objects.create() calls
replacements = [
    (r'festival_format="news_report"', "festival_format=self.format_news"),
    (r'festival_format="interview"', "festival_format=self.format_interview"),
    (r'festival_format="documentary"', "festival_format=self.format_doc"),
    (r'festival_topic="year_slogan"', "festival_topic=self.topic_slogan"),
    (r'festival_topic="jihad_explanation"', "festival_topic=self.topic_jihad"),
    (
        r'festival_topic="media_industry"',
        'festival_topic=FestivalTopic.objects.get(code="media_industry")',
    ),
    (r'special_section="progress_narrative"', "special_section=self.section_progress"),
]

# Apply all replacements
for pattern, replacement in replacements:
    content = content.replace(pattern, replacement)

# Write back
with open("festival/tests/test_api.py", "w") as f:
    f.write(content)

print("Fixed all festival_format, festival_topic, and special_section assignments")
