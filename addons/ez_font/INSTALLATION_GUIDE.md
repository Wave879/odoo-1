# 🎨 Ez Font Module - Installation & Setup Guide

## 📋 Quick Summary

**Module Name**: Ez Font
**Version**: 16.0.1.0.0
**Location**: `D:\odoo\odoo\addons\ez_font`
**Purpose**: Dynamic font management for Odoo Backend and Frontend without server restart

---

## ✅ Installation Steps

### Step 1: Verify Module Location
```
D:\odoo\odoo\addons\ez_font\
```

### Step 2: Install Module

**Option A: Using Odoo UI (Recommended)**
1. Open your Odoo instance
2. Go to **Apps** (Applications)
3. Click **"Settings"** → enable **"Developer Mode"**
4. Click **"Update Apps List"** (or manually search)
5. Search for **"Ez Font"**
6. Click **Install**

**Option B: Using Command Line**
```bash
cd D:\odoo
python odoo-bin -d <your_database> -i ez_font --restart
```

**Option C: Without Restart**
```bash
python odoo-bin -d <your_database> -i ez_font
```

### Step 3: Verify Installation
1. Go to **Settings** → **Administration**
2. You should see **"ตั้งค่าฟอนต์"** (Ez Font Settings) menu
3. Click to access the font management page

---

## 📁 Module File Structure

```
ez_font/
│
├── __init__.py                          # Import models and controllers
├── __manifest__.py                      # Module metadata (name, version, dependencies)
├── README.md                            # Documentation
│
├── models/
│   ├── __init__.py                      # Import ez_font model
│   └── ez_font.py                       # Model: ez.font.settings
│
├── controllers/
│   ├── __init__.py                      # Import main controller
│   └── main.py                          # HTTP routes for CSS injection
│
├── views/
│   ├── ez_font_view.xml                 # UI views (Tree, Form, Search, Menu)
│   └── templates.xml                    # Asset templates for CSS injection
│
├── security/
│   └── ir.model.access.csv              # Model access control
│
└── static/src/css/
    ├── ez_font_backend.css              # Backend CSS assets
    └── ez_font_frontend.css             # Frontend CSS assets
```

---

## 🚀 How to Use

### 1. Access the Module
```
Settings → Administration → ตั้งค่าฟอนต์
```
or
```
Menu Search: "ตั้งค่าฟอนต์"
```

### 2. Create a New Font Entry

**Click "Create" button** and fill in the form:

| Field | Example | Required |
|-------|---------|----------|
| ชื่อฟอนต์ (Font Name) | `Prompt` | ✅ Yes |
| Google Font URL | `https://fonts.googleapis.com/css2?family=Prompt` | ✅ Yes |
| CSS Selectors | `body, .o_web_client` | ❌ Optional |
| ใช้งาน (Active) | ☐ (unchecked) | Auto |
| คำอธิบาย (Description) | `Thai font for interface` | ❌ Optional |

### 3. Activate a Font

**Method 1: Using Button**
- Open any font record
- Click **"ใช้งานฟอนต์นี้"** (Apply Font)
- Notification will appear

**Method 2: Using Checkbox**
- Open font record
- Check the **"ใช้งาน"** (Active) checkbox
- Click Save

### 4. Deactivate a Font

**In the Font Record:**
- Click **"ยกเลิกใช้งาน"** (Deactivate)

**Or uncheck** the Active checkbox and save.

### 5. Change Font

Simply activate a different font - only one can be active at a time.

---

## 🎯 Google Fonts Examples

### Thai Fonts
```
ชื่อฟอนต์: Prompt
URL: https://fonts.googleapis.com/css2?family=Prompt

ชื่อฟอนต์: Kanit
URL: https://fonts.googleapis.com/css2?family=Kanit

ชื่อฟอนต์: Noto Sans Thai
URL: https://fonts.googleapis.com/css2?family=Noto+Sans+Thai
```

### International Fonts
```
ชื่อฟอนต์: IBM Plex Sans
URL: https://fonts.googleapis.com/css2?family=IBM+Plex+Sans

ชื่อฟอนต์: Roboto
URL: https://fonts.googleapis.com/css2?family=Roboto

ชื่อฟอนต์: Lato
URL: https://fonts.googleapis.com/css2?family=Lato
```

---

## 🔧 Technical Details

### Model Fields

**ez.font.settings**

| Field Name | Type | Description | Default |
|-----------|------|-------------|---------|
| font_name | Char | Name of the font | - |
| google_font_url | Char | Google Fonts URL | - |
| css_selectors | Text | CSS selectors to apply font | `body, .o_web_client` |
| is_active | Boolean | Active/Inactive status | False |
| description | Text | Additional notes | - |
| created_date | Datetime | Creation timestamp | Current |
| modified_date | Datetime | Last modified | Current |

### Key Constraints

- ✅ Only ONE font can be active at a time
- ✅ Activating a new font auto-deactivates the previous one
- ✅ No server restart needed
- ✅ CSS is generated dynamically per request

### API Endpoints

```
GET /ez_font/get_css
↳ Returns: Active font CSS (Content-Type: text/css)

POST /ez_font/get_active_font
↳ Returns: Active font info as JSON
{
    "status": "success",
    "font_name": "Prompt",
    "google_font_url": "...",
    "css_selectors": "..."
}
```

### CSS Generation

When activated, the module generates:

```css
@import url('https://fonts.googleapis.com/css2?family=Prompt');

body, .o_web_client {
    font-family: 'Prompt' !important;
}
```

---

## 🔒 Security & Permissions

### Access Levels

- **Regular Users**: Can read and modify fonts
- **System Users**: Full access to all font settings
- **Admin Users**: Can create, read, write, and delete fonts

### Model Permissions

```csv
# From: security/ir.model.access.csv
access_ez_font_settings_user    → Regular users
access_ez_font_settings_system  → System administrators
```

---

## ⚙️ Configuration

### Change CSS Selectors

Default applies to: `body, .o_web_client`

**To apply to different areas:**

| Selector | Affects |
|----------|---------|
| `body` | Entire page |
| `.o_web_client` | Odoo interface |
| `.o_web_settings_domain` | Settings area only |
| `.o_content` | Main content |
| `.o_form_view` | Form views |
| `.o_list_view` | List views |

**Example:**
```
.o_web_client, .o_form_view, .o_list_view
```

---

## 🐛 Troubleshooting

### Issue: Font doesn't change after activation

**Solution:**
1. Hard refresh: **Ctrl + Shift + R** (Windows/Linux) or **Cmd + Shift + R** (Mac)
2. Clear browser cache
3. Log out and log back in
4. Check if "ใช้งาน" checkbox is marked

### Issue: "Only one font can be active"

**Solution:**
This is intentional. The system only allows one active font. If you need to change:
1. Click on the current active font
2. Click "ยกเลิกใช้งาน" OR uncheck "ใช้งาน"
3. Then activate the new font

### Issue: CSS not loading

**Solution:**
1. Check the Google Font URL format
2. Test URL in browser: `https://fonts.googleapis.com/css2?family=FontName`
3. Ensure no typos in font name
4. Check browser console for errors (F12)

### Issue: Font looks different than expected

**Solution:**
1. Some fonts may not support all characters
2. Try a different font from Google Fonts
3. Check CSS Selectors are correct
4. Clear cache and refresh again

### Issue: Module not appearing after installation

**Solution:**
1. Enable Developer Mode: Settings → Developer Mode
2. Click "Update Apps List"
3. Search for "Ez Font" again
4. Make sure module location is: `D:\odoo\odoo\addons\ez_font`

---

## 📊 Database Queries

### Check Active Font (SQL)
```sql
SELECT * FROM ez_font_settings WHERE is_active = true LIMIT 1;
```

### Get All Fonts (SQL)
```sql
SELECT font_name, google_font_url, is_active FROM ez_font_settings ORDER BY created_date DESC;
```

---

## 🔄 No Restart Required!

Unlike traditional CSS modifications, Ez Font:
- ✅ Changes fonts instantly
- ✅ No server restart needed
- ✅ No file modifications
- ✅ No dependency on other modules
- ✅ Database-driven configuration

---

## 📝 Notes

1. **Thai Language Support**: All menus and labels are in Thai language
2. **No Core Modifications**: Module doesn't touch Odoo core files
3. **Backward Compatible**: Can be safely uninstalled
4. **Multiple Instances**: Each Odoo instance can have different fonts
5. **Database-Specific**: Font settings are per database

---

## ❓ FAQ

**Q: Can I use custom fonts not from Google Fonts?**
A: Yes, modify the Google Font URL field to point to your font CDN.

**Q: Will this affect other modules?**
A: No, Ez Font operates independently and doesn't modify other addons.

**Q: Can I apply different fonts to different areas?**
A: Yes, use CSS Selectors to target specific areas (`.o_form_view`, `.o_list_view`, etc.)

**Q: Do I need to restart Odoo?**
A: No, changes apply immediately.

**Q: What if I uninstall the module?**
A: Font settings remain in database (can be purged manually if needed).

---

## 📞 Support & Contact

For issues or questions, contact the module developer.

**Module Version**: 16.0.1.0.0
**License**: LGPL-3
**Status**: Production Ready ✅

---

**Created**: January 23, 2026
**Last Updated**: January 23, 2026
