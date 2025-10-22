# Education Model Media Implementation

## Overview
Added video and document upload capabilities to the Education model with complete admin interface, API integration, and comprehensive test coverage.

## Changes Implemented

### 1. Model Updates (`content/models/education.py`)

#### New Fields
- **video**: FileField for uploading educational videos
  - Accepted formats: `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`
  - Max size: 500 MB
  - Upload path: `education/videos/`
  - **Random filename generation**: Files are saved with UUID-based random names for security
  
- **document**: FileField for uploading educational documents
  - Accepted formats: `.pdf`, `.ppt`, `.pptx`
  - Max size: 50 MB
  - Upload path: `education/documents/`
  - **Random filename generation**: Files are saved with UUID-based random names for security

#### Helper Properties
- `has_video`: Boolean property checking if video file exists
- `has_document`: Boolean property checking if document file exists
- `video_filename`: Returns the video filename (UUID hex + extension)
- `document_filename`: Returns the document filename (UUID hex + extension)

#### Upload Path Functions
- `education_video_upload_path()`: Generates random UUID-based filename for videos
  - Format: `content/education/videos/<32-char-uuid-hex>.<ext>`
  - Example: `content/education/videos/a1b2c3d4e5f6...1234.mp4`
  
- `education_document_upload_path()`: Generates random UUID-based filename for documents
  - Format: `content/education/documents/<32-char-uuid-hex>.<ext>`
  - Example: `content/education/documents/f6e5d4c3b2a1...5678.pdf`

#### Security Benefits
- **Prevents filename collisions**: UUID ensures unique filenames
- **Hides original filenames**: Uploaded files don't expose user-provided names
- **Prevents path traversal**: Random names eliminate directory traversal risks
- **Maintains file extensions**: Original extensions preserved for proper mime-type handling

### 2. Database Migration (`content/migrations/0003_education_document_education_video.py`)
- Created and applied successfully
- Adds nullable FileField columns for video and document

### 3. Admin Interface (`content/admin/education.py`)

#### Updated Features
- **New fieldset**: "فایل‌های آموزشی" (Educational Files) containing video and document fields
- **Media status display**: `display_media_status()` method shows badges for uploaded files
  - 🎬 Green badge for video files
  - 📄 Blue badge for document files
- **Enhanced list_display**: Added `display_media_status` column
- **Persian help texts**: Comprehensive guidance for file formats and size limits

### 4. Serializers (`content/serializers.py`)

#### EducationSerializer Updates
- Added `video` and `document` FileField fields
- **Video validation**:
  - File size limit: 500 MB
  - Format validation: mp4, avi, mov, mkv, wmv
  - Persian error messages
- **Document validation**:
  - File size limit: 50 MB
  - Format validation: pdf, ppt, pptx
  - Persian error messages

#### EducationListSerializer Updates
- Added media-related fields:
  - `has_video`: Boolean flag
  - `has_document`: Boolean flag
  - `video_url`: Full URL to video file (or null)
  - `document_url`: Full URL to document file (or null)
- Supports request context for absolute URLs

### 5. API Views (`content/views/education.py`)
- Existing views already support file uploads through DRF's default handling
- List and detail endpoints properly expose media fields
- No changes needed (views inherit from base classes that handle multipart/form-data)

### 6. Tests

#### Model Tests (`content/tests/test_models.py`)
Added 8 new tests for Education model:
1. `test_education_video_field_optional`: Verifies video is optional
2. `test_education_document_field_optional`: Verifies document is optional
3. `test_education_has_video_property`: Tests has_video property
4. `test_education_has_document_property`: Tests has_document property
5. `test_education_video_filename_property`: Tests video_filename property
6. `test_education_document_filename_property`: Tests document_filename property
7. `test_education_with_both_video_and_document`: Tests both files together

#### API Tests (`content/tests/test_api.py`)
Added 6 new tests for Education API:
1. `test_education_list_includes_media_fields`: Verifies media fields in list response
2. `test_education_detail_includes_media_fields`: Verifies media fields in detail response
3. `test_education_with_video_file`: Tests education with video upload
4. `test_education_with_document_file`: Tests education with document upload
5. `test_education_with_both_video_and_document`: Tests both files in API response

### Test Results
```
✅ All 57 content app tests passing
✅ 12 Education model tests (including 8 new + 1 uniqueness test)
✅ 9 Education API tests (including 5 new)
✅ 10 Serializer validation tests
✅ System check: No issues
```

## API Response Examples

### Education List Response
```json
{
  "total_items": 1,
  "total_pages": 1,
  "current_page": 1,
  "results": [
    {
      "id": 1,
      "title": "آموزش تولید محتوا",
      "publish_date": "2024-01-15",
      "tags": ["آموزش", "رسانه"],
      "image": "http://example.com/media/education/images/tutorial.jpg",
      "has_video": true,
      "has_document": true,
      "video_url": "http://example.com/media/education/videos/tutorial.mp4",
      "document_url": "http://example.com/media/education/documents/slides.pdf"
    }
  ]
}
```

### Education Detail Response
```json
{
  "id": 1,
  "title": "آموزش تولید محتوا",
  "description": "دوره جامع تولید محتوای رسانه‌ای",
  "image": "http://example.com/media/education/images/tutorial.jpg",
  "publish_date": "2024-01-15",
  "tags": ["آموزش", "رسانه"],
  "video": "http://example.com/media/education/videos/tutorial.mp4",
  "document": "http://example.com/media/education/documents/slides.pdf",
  "created_at": "2024-01-10T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z"
}
```

## Admin Interface Features

### File Upload
1. Navigate to Education section in admin
2. Create or edit education content
3. Upload video and/or document in "فایل‌های آموزشی" fieldset
4. Help texts guide format and size requirements

### List View
- Media status badges show which files are uploaded
- Green 🎬 badge indicates video present
- Blue 📄 badge indicates document present
- "بدون فایل" shows when no media files

### File Management
- Files stored in organized structure:
  - Videos: `media/education/videos/`
  - Documents: `media/education/documents/`
- **Random UUID-based filenames** for security and uniqueness
- Original file extensions preserved
- Example stored filename: `a1b2c3d4e5f6789012345678901234567890.mp4`
- Prevents filename collisions and path traversal attacks

## Usage Guidelines

### For Content Managers
1. Use admin interface to upload video and document files
2. Supported video formats: MP4 (recommended), AVI, MOV, MKV, WMV
3. Supported document formats: PDF (recommended), PPT, PPTX
4. Keep video files under 500 MB for optimal performance
5. Keep document files under 50 MB

### For API Consumers
1. Check `has_video` and `has_document` flags in list view
2. Use full URLs from `video_url` and `document_url` for direct access
3. Download files using GET requests to the URLs
4. Handle cases where URLs may be null (no file uploaded)

## File Validation

### Video Files
- **Size**: Maximum 500 MB (524,288,000 bytes)
- **Formats**: .mp4, .avi, .mov, .mkv, .wmv
- **Error Messages**: Persian language, shows current file size

### Document Files
- **Size**: Maximum 50 MB (52,428,800 bytes)
- **Formats**: .pdf, .ppt, .pptx
- **Error Messages**: Persian language, shows current file size

## Migration Notes
- Migration `0003_education_document_education_video` adds both fields as nullable
- Existing Education records remain valid (fields default to empty)
- No data loss or downtime during migration
- Backward compatible with existing API consumers

## Dependencies
- Django 4.2.23
- Django REST Framework
- No additional packages required (uses built-in FileField)

## Future Enhancements (Suggestions)
1. Video transcoding for consistent formats
2. Thumbnail generation for video preview
3. Document preview/viewer integration
4. File size optimization/compression
5. Progress indicators for large uploads
6. Streaming support for video playback
