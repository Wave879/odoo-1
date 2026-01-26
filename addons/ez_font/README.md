# Ez Font Module

**โมดูล Ez Font - ระบบจัดการฟอนต์แบบไดนามิก**

## คำอธิบาย

โมดูล Ez Font ให้คุณสามารถดาวน์โหลดและเปลี่ยนฟอนต์ของระบบ (ทั้ง Backend และ Frontend) แบบไดนามิกโดยไม่ต้องแก้ไขไฟล์อื่น ๆ หรือไฟล์ core

## คุณสมบัติ

✅ **จัดการฟอนต์จากแหล่ง Google Fonts**
- ใช้ Google Font URL ได้หลายอย่าง
- รองรับการเปลี่ยนฟอนต์แบบไดนามิก

✅ **ใช้งานบน Backend และ Frontend**
- ใช้ฟอนต์เดียวกันทั่วทั้งระบบ
- ควบคุมได้ผ่าน CSS Selectors

✅ **ไม่ต้องรีสตาร์ทเซิร์ฟเวอร์**
- เปลี่ยนฟอนต์ได้ทันที
- ไม่ต้องตั้งค่าใหม่

✅ **ไม่แก้ไฟล์ Core**
- ใช้ Controller เพื่อ inject CSS แบบไดนามิก
- ไม่ส่งผลต่อโมดูลอื่น ๆ

## การติดตั้ง

1. คัดลอกโมดูล `ez_font` ไปยัง `D:\odoo\odoo\addons\`

2. ไปที่ Applications → เลือก Developer Mode

3. ค้นหาและติดตั้ง "Ez Font"

4. หรือใช้ Terminal:
   ```
   ./odoo-bin -d <database_name> -i ez_font --restart
   ```

## วิธีใช้

### 1. เข้าสู่เมนู

```
Settings → Administration → ตั้งค่าฟอนต์
```

### 2. สร้างฟอนต์ใหม่

- คลิก "Create"
- กรอกข้อมูล:
  - **ชื่อฟอนต์**: ชื่อที่ต้องการ (เช่น "Prompt", "IBM Plex Sans")
  - **Google Font URL**: ลิงก์ Google Fonts (เช่น `https://fonts.googleapis.com/css2?family=Prompt`)
  - **CSS Selectors** (ตัวเลือก): `.o_web_client, body`

### 3. ใช้งานฟอนต์

- คลิก "ใช้งานฟอนต์นี้"
- ฟอนต์จะเปลี่ยนทันที

### 4. ยกเลิกใช้งาน

- คลิก "ยกเลิกใช้งาน" ที่ฟอนต์ที่ใช้งาน

## ตัวอย่าง Google Fonts

| ฟอนต์ | URL |
|------|-----|
| Prompt (ไทย) | `https://fonts.googleapis.com/css2?family=Prompt` |
| IBM Plex Sans | `https://fonts.googleapis.com/css2?family=IBM+Plex+Sans` |
| Noto Sans Thai | `https://fonts.googleapis.com/css2?family=Noto+Sans+Thai` |
| Kanit | `https://fonts.googleapis.com/css2?family=Kanit` |
| Roboto | `https://fonts.googleapis.com/css2?family=Roboto` |

## โครงสร้างไฟล์

```
ez_font/
├── __init__.py                    # Package initialization
├── __manifest__.py                # Module metadata
├── models/
│   ├── __init__.py
│   └── ez_font.py                # Model: ez.font.settings
├── controllers/
│   ├── __init__.py
│   └── main.py                   # Controllers for CSS injection
├── views/
│   ├── ez_font_view.xml          # Tree, Form, Search views & Menu
│   └── templates.xml             # Asset templates
├── security/
│   └── ir.model.access.csv       # Access control
└── static/src/css/
    ├── ez_font_backend.css       # Backend CSS assets
    └── ez_font_frontend.css      # Frontend CSS assets
```

## API Endpoints

### 1. ดึง CSS แบบไดนามิก
```
GET /ez_font/get_css
```
ส่งกลับ CSS ของฟอนต์ที่ใช้งานอยู่

### 2. ดึงข้อมูลฟอนต์แบบ JSON
```
POST /ez_font/get_active_font
```
ส่งกลับข้อมูลฟอนต์ที่ใช้งาน (format: JSON)

## Technical Details

### Model: ez.font.settings

| ฟิลด์ | ประเภท | คำอธิบาย |
|------|--------|---------|
| font_name | Char | ชื่อฟอนต์ (บังคับ) |
| google_font_url | Char | ลิงก์ Google Fonts (บังคับ) |
| css_selectors | Text | CSS Selectors ที่ต้องการใช้ |
| is_active | Boolean | ฟอนต์ที่ใช้งาน (เพียงหนึ่งตัว) |
| description | Text | คำอธิบายเพิ่มเติม |
| created_date | Datetime | วันที่สร้าง |
| modified_date | Datetime | วันที่แก้ไข |

### Constraints
- สามารถเลือกฟอนต์ที่ใช้งานได้เพียงหนึ่งตัวเท่านั้น
- การเปิดใช้งานฟอนต์ใหม่จะปิดใช้งานฟอนต์เดิมโดยอัตโนมัติ

## CSS Injection Strategy

โมดูลใช้วิธี HTTP GET endpoint `/ez_font/get_css` ซึ่ง:
1. ค้นหาฟอนต์ที่ใช้งาน
2. สร้าง CSS บนพื้นฐานของข้อมูลตัวอักษร
3. ส่งกลับ CSS ผ่าน Content-Type: text/css

วิธีนี้ช่วยให้สามารถเปลี่ยนฟอนต์โดยไม่ต้องรีสตาร์ทเซิร์ฟเวอร์

## Requirements

- Odoo 16.0+
- Python 3.8+
- Modules: base, web

## License

LGPL-3

## Author

Odoo Developer

## ข้อมูลเพิ่มเติม

### CSS Classes ที่ใช้บ่อย

```
.o_web_client          # Odoo web interface
.o_web_settings_domain # Settings area
.o_content             # Main content area
body                   # Document body
```

### ค่าเริ่มต้น CSS Selectors

```
body, .o_web_client
```

### ตัวอย่างการใช้

**ตัวอย่าง 1: ใช้ Prompt กับ Thai Interface**
- ชื่อฟอนต์: Prompt
- Google Font URL: `https://fonts.googleapis.com/css2?family=Prompt`
- CSS Selectors: `body, .o_web_client`

**ตัวอย่าง 2: ใช้ IBM Plex กับเฉพาะการตั้งค่า**
- ชื่อฟอนต์: IBM Plex Sans
- Google Font URL: `https://fonts.googleapis.com/css2?family=IBM+Plex+Sans`
- CSS Selectors: `.o_web_settings_domain`

## Troubleshooting

### ฟอนต์ไม่เปลี่ยน
1. ตรวจสอบว่าฟอนต์ถูกตั้งค่าเป็น "ใช้งาน"
2. ลองรีโหลดหน้าเว็บ (F5 หรือ Ctrl+R)
3. ล้างแคช Browser

### URL Google Fonts ไม่ถูกต้อง
1. ไปที่ https://fonts.google.com
2. เลือกฟอนต์ที่ต้องการ
3. คัดลอก URL จาก Link tab

### ปัญหา CSS Specificity
- เพิ่มเติม CSS Selectors (ห่อด้วยเครื่องหมายจุลภาค)
- ใช้ `!important` ในการประกาศของโมดูล

## Support

สำหรับคำถามหรือปัญหา โปรดติดต่อผู้พัฒนา
