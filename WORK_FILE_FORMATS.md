# Work File Upload - Supported Formats

## ✅ YES, PDF files ARE ACCEPTED!

PDF is the **first** format in the list of allowed file extensions for Work creation.

## Supported File Formats

The Work creation API (`POST /api/festival/works/`) accepts the following file formats:

### 📄 **Document Formats**
- `.pdf` ✅ **PDF (Portable Document Format)**
- `.doc` - Microsoft Word (old format)
- `.docx` - Microsoft Word (new format)
- `.txt` - Plain text
- `.rtf` - Rich Text Format

### 🖼️ **Image Formats**
- `.jpg` / `.jpeg` - JPEG images
- `.png` - PNG images
- `.gif` - GIF images
- `.bmp` - Bitmap images

### 🎬 **Video Formats**
- `.mp4` - MP4 video
- `.avi` - AVI video
- `.mov` - QuickTime video
- `.mkv` - Matroska video
- `.wmv` - Windows Media Video

### 🎵 **Audio Formats**
- `.mp3` - MP3 audio
- `.wav` - WAV audio
- `.aac` - AAC audio
- `.flac` - FLAC audio

### 📦 **Archive Formats**
- `.zip` - ZIP archive
- `.rar` - RAR archive
- `.7z` - 7-Zip archive

## File Size Limit

**Maximum file size: 110 MB (115,343,360 bytes)**

## Validation Details

The file validation is performed in `WorkCreateSerializer.validate_file()` method:

```python
def validate_file(self, value):
    """Validate uploaded file"""
    if not value:
        raise serializers.ValidationError("فایل اثر الزامی است.")

    # Check file size (max 110MB)
    if value.size > 110 * 1024 * 1024:
        raise serializers.ValidationError("حجم فایل نباید بیش از ۱۱۰ مگابایت باشد.")

    # Check file extension
    allowed_extensions = [
        ".pdf",    # <-- PDF is HERE! ✅
        ".doc",
        ".docx",
        # ... rest of extensions
    ]

    file_name = value.name.lower()
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        raise serializers.ValidationError(
            "فرمت فایل مجاز نیست. فرمت‌های مجاز: " + ", ".join(allowed_extensions)
        )

    return value
```

## Testing

PDF file upload is extensively tested in the test suite:

```bash
# Run Work API tests
python manage.py test festival.tests.test_api::WorkAPITest
```

The tests use PDF files like:
- `test_file.pdf`
- `work1.pdf`
- `work2.pdf`
- `detail_test.pdf`
- etc.

## Example API Request

```bash
# Upload a PDF file
curl -X POST http://localhost:8000/api/festival/works/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "festival_registration=1" \
  -F "title=مستند خبری" \
  -F "description=یک مستند خبری درباره رویدادهای اخیر" \
  -F "file=@document.pdf"
```

## Python Example

```python
from django.core.files.uploadedfile import SimpleUploadedFile

# Create a PDF file object
pdf_file = SimpleUploadedFile(
    "report.pdf",
    b"%PDF-1.4\nPDF content here...",
    content_type="application/pdf"
)

# Send to API
response = client.post('/api/festival/works/', {
    'festival_registration': registration_id,
    'title': 'گزارش خبری',
    'description': 'توضیحات',
    'file': pdf_file
})
```

## Frontend Example (JavaScript)

```javascript
// HTML form with file input
const formData = new FormData();
formData.append('festival_registration', registrationId);
formData.append('title', 'عنوان اثر');
formData.append('description', 'توضیحات اثر');
formData.append('file', pdfFileInput.files[0]); // PDF file from input

// Send to API
fetch('/api/festival/works/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

## Summary

✅ **PDF files are FULLY SUPPORTED** for Work file uploads  
✅ Maximum size: **110 MB**  
✅ Validated at serializer level  
✅ Extensively tested  
✅ Production ready  

No changes needed - PDF support is already implemented and working! 🎉
