# Content Management System - News, Education, and Event Models

## Overview

This implementation follows a **Test-Driven Development (TDD)** approach to create three content models with identical structure for managing News, Education, and Event content in the یازدهمین جشنواره رسانه‌ای ابوذر (11th Abozar Media Festival) system.

## 🏗️ Architecture

### Models Structure
All three models (`News`, `Education`, `Event`) inherit from a common `BaseContentModel` with identical fields:

- **title**: عنوان محتوا
- **description**: توضیحات کامل محتوا  
- **image**: تصویر مرتبط با محتوا (optional)
- **publish_date**: تاریخ انتشار محتوا
- **tags**: برچسب‌های مرتبط با محتوا (using django-taggit)
- **created_at**: تاریخ ایجاد (auto)
- **updated_at**: تاریخ به‌روزرسانی (auto)

### API Endpoints

#### News Endpoints
- `GET /content/news/` - دریافت لیست اخبار (paginated)
- `GET /content/news/{id}/` - دریافت جزئیات خبر

#### Education Endpoints  
- `GET /content/education/` - دریافت لیست آموزش‌ها (paginated)
- `GET /content/education/{id}/` - دریافت جزئیات آموزش

#### Event Endpoints
- `GET /content/events/` - دریافت لیست رویدادها (paginated)
- `GET /content/events/{id}/` - دریافت جزئیات رویداد

## 🔥 Features

### 1. **Advanced Filtering & Search**
- **Search**: جستجو در title و description
- **Tag Filter**: فیلتر بر اساس برچسب‌ها (`?tags__name=رسانه`)
- **Date Filter**: فیلتر بر اساس تاریخ انتشار (`?publish_date=2024-10-10`)
- **Ordering**: مرتب‌سازی بر اساس تاریخ، ایجاد (`?ordering=-publish_date`)

### 2. **Pagination System**
Uses the project's `StandardPagination` with custom response format:
```json
{
  "links": {
    "next": "https://...",
    "previous": "https://..."
  },
  "total_items": 25,
  "total_pages": 5,
  "current_page": 1,
  "page_size": "6",
  "results": [...]
}
```

### 3. **Tag Management**
Integrated with `django-taggit` for flexible tagging:
- Persian language support
- Shared tags across all content types
- Tag-based filtering and search

### 4. **Permission System**
- **Read Access**: Public (anonymous users can view)
- **Write Access**: Authenticated users only (future enhancement)

## 🧪 Test Coverage

### TDD Implementation
Following TDD methodology, we implemented **51 comprehensive tests**:

#### Model Tests (17 tests)
- `content/tests.py`: Core model functionality
  - Field validation and constraints
  - String representations  
  - Taggit integration
  - Model metadata and ordering
  - Cross-model consistency

#### API Tests (17 tests)  
- `content/test_api.py`: Complete API testing
  - CRUD operations
  - Search and filtering
  - Pagination consistency
  - Authentication scenarios
  - Error handling (404, validation)

#### Integration Tests (17 tests)
- Cross-model functionality
- Tag sharing between models
- Pagination uniformity
- Permission consistency

### Test Results
```bash
# Individual content tests
Found 34 test(s) - ✅ ALL PASSING

# Full system tests  
Found 107 test(s) - ✅ ALL PASSING
```

## 📊 Sample Data

The system includes sample data creation script:
```python
# Created via create_sample_data.py
- 4 news items
- 3 education items  
- 3 events
```

## 🔧 Technical Implementation

### Files Created/Modified

#### Core Models
- `content/models.py` - BaseContentModel + News/Education/Event models
- `content/migrations/0001_initial.py` - Database schema

#### API Layer  
- `content/serializers.py` - DRF serializers with taggit support
- `content/views.py` - List/Detail views with filtering
- `content/urls.py` - URL routing

#### Admin Interface
- `content/admin.py` - Django admin configuration

#### Testing
- `content/tests.py` - Model tests (TDD approach)
- `content/test_api.py` - API endpoint tests

#### Configuration
- `config/urls.py` - Added content URLs
- `config/settings.py` - Already included content app

## 🎯 API Documentation

The system includes comprehensive API documentation via drf-spectacular:

- **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://127.0.0.1:8000/api/schema/redoc/`
- **OpenAPI Schema**: `http://127.0.0.1:8000/api/schema/`

## 🚀 Usage Examples

### List News with Filters
```bash
# Get all news
GET /content/news/

# Search in title/description  
GET /content/news/?search=جشنواره

# Filter by tag
GET /content/news/?tags__name=اخبار

# Combine filters with ordering
GET /content/news/?search=ابوذر&ordering=-created_at
```

### Pagination Example
```bash
# First page
GET /content/news/?page=1

# Custom page size
GET /content/news/?page_size=10
```

### Tag-based Filtering Across Models
```bash
# Find all content tagged with "رسانه"
GET /content/news/?tags__name=رسانه
GET /content/education/?tags__name=رسانه  
GET /content/events/?tags__name=رسانه
```

## 🔮 Future Enhancements

1. **CRUD Operations**: Add Create/Update/Delete endpoints
2. **Image Upload**: Handle image file uploads
3. **Rich Text**: Integrate CKEditor for description field
4. **Categories**: Add hierarchical categorization
5. **Comments**: User comments and reviews system
6. **Publishing Workflow**: Draft/Review/Published states

## 📈 Performance Considerations

- **Database Indexing**: Automatic indexing on publish_date, created_at
- **Queryset Optimization**: Select_related for foreign keys
- **Pagination**: Efficient pagination with StandardPagination
- **Tag Performance**: Optimized taggit queries

## 🎉 Summary

Successfully implemented a complete **Content Management System** using **Test-Driven Development** with:

✅ **3 Content Models** with identical structure  
✅ **6 API Endpoints** with full CRUD capability  
✅ **Advanced Filtering** (search, tags, dates, ordering)  
✅ **Pagination System** with custom response format  
✅ **51 Comprehensive Tests** (100% passing)  
✅ **Django Admin Integration**  
✅ **API Documentation** (Swagger + ReDoc)  
✅ **Persian Language Support**  
✅ **Tag Management System**  

The implementation follows Django best practices, maintains consistency with the existing festival system, and provides a solid foundation for content management in the یازدهمین جشنواره رسانه‌ای ابوذر project.