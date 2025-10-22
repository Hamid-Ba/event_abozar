# Festival Category List APIs

## Overview
این APIها برای دریافت لیست دسته‌بندی‌های جشنواره رسانه‌ای ابوذر طراحی شده‌اند. شامل قالب‌ها، محورها و بخش‌های ویژه جشنواره.

These APIs provide access to festival category data including formats, topics, and special sections.

## Endpoints

### 1. Festival Formats List
**Endpoint:** `GET /api/festival/formats/`

**Description:** دریافت لیست قالب‌های جشنواره (گزارش خبری، مصاحبه، مستند، ...)

**Authentication:** Not required (Public endpoint)

**Query Parameters:**
- `is_active` (optional): 
  - `true` (default) - فقط قالب‌های فعال
  - `false` - فقط قالب‌های غیرفعال
  - `all` - همه قالب‌ها

**Response Example:**
```json
[
  {
    "id": 1,
    "code": "news_report",
    "name": "گزارش خبری",
    "description": "گزارش‌های خبری و تحلیلی"
  },
  {
    "id": 2,
    "code": "interview",
    "name": "مصاحبه",
    "description": "مصاحبه‌های خبری"
  }
]
```

**Usage Example:**
```bash
# Get all active formats
curl http://localhost:8000/api/festival/formats/

# Get all formats (including inactive)
curl http://localhost:8000/api/festival/formats/?is_active=all

# Get only inactive formats
curl http://localhost:8000/api/festival/formats/?is_active=false
```

---

### 2. Festival Topics List
**Endpoint:** `GET /api/festival/topics/`

**Description:** دریافت لیست محورهای جشنواره (شعار سال، جهاد تبیین، ...)

**Authentication:** Not required (Public endpoint)

**Query Parameters:**
- `is_active` (optional):
  - `true` (default) - فقط محورهای فعال
  - `false` - فقط محورهای غیرفعال
  - `all` - همه محورها

**Response Example:**
```json
[
  {
    "id": 1,
    "code": "year_slogan",
    "name": "شعار سال",
    "description": "محور شعار سال"
  },
  {
    "id": 2,
    "code": "jihad_explanation",
    "name": "جهاد تبیین",
    "description": "محور جهاد تبیین"
  }
]
```

**Usage Example:**
```bash
# Get all active topics
curl http://localhost:8000/api/festival/topics/

# Get all topics
curl http://localhost:8000/api/festival/topics/?is_active=all
```

---

### 3. Festival Special Sections List
**Endpoint:** `GET /api/festival/special-sections/`

**Description:** دریافت لیست بخش‌های ویژه جشنواره (روایت پیشرفت، روایت میدان، ...)

**Authentication:** Not required (Public endpoint)

**Query Parameters:**
- `is_active` (optional):
  - `true` (default) - فقط بخش‌های ویژه فعال
  - `false` - فقط بخش‌های ویژه غیرفعال
  - `all` - همه بخش‌های ویژه

**Response Example:**
```json
[
  {
    "id": 1,
    "code": "progress_narrative",
    "name": "روایت پیشرفت",
    "description": "بخش ویژه روایت پیشرفت"
  },
  {
    "id": 2,
    "code": "field_narrative_12days",
    "name": "روایت میدان در جنگ ۱۲ روزه",
    "description": "بخش ویژه روایت میدان"
  }
]
```

**Usage Example:**
```bash
# Get all active special sections
curl http://localhost:8000/api/festival/special-sections/

# Get all special sections
curl http://localhost:8000/api/festival/special-sections/?is_active=all
```

---

## Common Features

### Ordering
All category lists are ordered by:
1. `display_order` (ascending) - ترتیب نمایش تعریف شده در ادمین
2. `name` (ascending) - نام دسته‌بندی به صورت الفبایی

### Response Structure
All category endpoints return an array of objects with the following fields:
- `id` (integer): شناسه یکتای دسته‌بندی
- `code` (string): کد یکتای دسته‌بندی
- `name` (string): نام فارسی دسته‌بندی
- `description` (string|null): توضیحات دسته‌بندی

### Use Cases

#### 1. Registration Form Dropdowns
Use these APIs to populate dropdown menus in festival registration forms:

```javascript
// Fetch formats for dropdown
fetch('/api/festival/formats/')
  .then(response => response.json())
  .then(formats => {
    formats.forEach(format => {
      // Add option to dropdown
      dropdown.add(new Option(format.name, format.id));
    });
  });
```

#### 2. Filter Options
Use category data to create filter options in list views:

```javascript
// Get topics for filter
const topics = await fetch('/api/festival/topics/').then(r => r.json());

// Create filter UI
topics.forEach(topic => {
  filterContainer.innerHTML += `
    <input type="checkbox" id="topic-${topic.id}" value="${topic.id}">
    <label for="topic-${topic.id}">${topic.name}</label>
  `;
});
```

#### 3. Display Category Names
When displaying registration or work data, use category objects instead of just IDs:

```javascript
// Registration data includes nested category objects
const registration = {
  "id": 123,
  "full_name": "علی احمدی",
  "festival_format": {
    "id": 1,
    "code": "news_report",
    "name": "گزارش خبری",
    "description": "..."
  },
  "festival_topic": {
    "id": 5,
    "code": "year_slogan",
    "name": "شعار سال",
    "description": "..."
  }
}

// Display format name directly
console.log(registration.festival_format.name); // "گزارش خبری"
```

---

## Testing

Run the test suite:
```bash
python manage.py test festival.tests.test_category_list_api
```

All tests should pass with 15 successful test cases covering:
- ✅ Active filtering (default behavior)
- ✅ Inactive filtering
- ✅ All items (no filtering)
- ✅ Correct ordering
- ✅ Response structure
- ✅ Public access (no authentication required)
- ✅ Empty results handling

---

## Notes

1. **Public Access**: These endpoints are publicly accessible and don't require authentication
2. **Caching**: Consider implementing caching for these endpoints as category data changes infrequently
3. **Performance**: All queries are optimized with proper ordering and filtering at database level
4. **Admin Management**: Categories can be managed through Django admin at `/admin/festival/`
