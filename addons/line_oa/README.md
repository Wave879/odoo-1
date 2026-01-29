# LINE OA Notification Module

## คำอธิบาย

โมดูลสำหรับส่งข้อความแจ้งเตือนผ่าน LINE Official Account (OA) รองรับการส่งข้อความหลากหลายรูปแบบและวิธีการส่ง

## ฟีเจอร์

### รูปแบบข้อความที่รองรับ (10 ประเภท)

1. **Text Message** - ข้อความธรรมดา
2. **Image Message** - รูปภาพ
3. **Video Message** - วิดีโอ
4. **Audio Message** - เสียง
5. **Sticker Message** - สติกเกอร์ LINE
6. **Location Message** - ตำแหน่งที่ตั้ง
7. **Template Message** - เทมเพลทพร้อมปุ่ม
   - Buttons Template
   - Confirm Template
   - Carousel Template
8. **Flex Message** - ข้อความแบบ Flex (JSON)
9. **Rich Message (Image Map)** - รูปภาพที่คลิกได้
10. **Quick Reply** - ปุ่มตอบกลับด่วน

### วิธีการส่งข้อความ (4 วิธี)

1. **Reply Message** - ตอบกลับข้อความจาก webhook
2. **Push Message** - ส่งถึงผู้ใช้คนเดียว
3. **Multicast Message** - ส่งถึงหลายคน (สูงสุด 500 คน)
4. **Broadcast Message** - ส่งถึงผู้ติดตามทั้งหมด

## การติดตั้ง

### 1. ติดตั้ง Python Package

```bash
pip install --user line-bot-sdk
```

### 2. ติดตั้งโมดูลใน Odoo

```bash
python odoo-bin -c odoo.conf -i line_oa_notify --stop-after-init
```

## การตั้งค่า

### 1. สร้าง LINE Official Account

1. ไปที่ [LINE Developers Console](https://developers.line.biz/console/)
2. สร้าง Provider และ Channel (Messaging API)
3. คัดลอก **Channel Access Token** และ **Channel Secret**

### 2. ตั้งค่าใน Odoo

1. เข้าเมนู **LINE OA > การตั้งค่า**
2. สร้างการตั้งค่าใหม่
3. กรอก Channel Access Token และ Channel Secret
4. กดปุ่ม **ทดสอบการเชื่อมต่อ**

## การใช้งาน

### สร้างเทมเพลทข้อความ

1. เข้าเมนู **LINE OA > เทมเพลทข้อความ**
2. สร้างเทมเพลทใหม่
3. เลือกประเภทข้อความ
4. กรอกข้อมูลตามประเภทที่เลือก
5. กดปุ่ม **ส่งทดสอบ** เพื่อทดสอบ

### ส่งข้อความผ่าน Python Code

```python
# ส่งแบบ Push (ส่งถึงคนเดียว)
self.env['line.message.mixin'].line_send_push_message(
    user_id='U1234567890abcdef',
    template_id=template.id
)

# ส่งแบบ Multicast (ส่งหลายคน)
self.env['line.message.mixin'].line_send_multicast_message(
    user_ids=['U111', 'U222', 'U333'],
    template_id=template.id
)

# ส่งแบบ Broadcast (ส่งทุกคน)
self.env['line.message.mixin'].line_send_broadcast_message(
    template_id=template.id
)

# ส่งแบบ Reply (ตอบกลับ)
self.env['line.message.mixin'].line_send_reply_message(
    reply_token='reply_token_from_webhook',
    template_id=template.id
)
```

### ดูบันทึกการส่ง

เข้าเมนู **LINE OA > บันทึกการส่ง** เพื่อดูประวัติการส่งข้อความทั้งหมด

## ตัวอย่างการใช้งาน

### ตัวอย่าง Template Buttons

```json
{
  "type": "template",
  "altText": "เมนูหลัก",
  "template": {
    "type": "buttons",
    "text": "กรุณาเลือกเมนู",
    "actions": [
      {
        "type": "message",
        "label": "ดูสินค้า",
        "text": "ดูสินค้า"
      },
      {
        "type": "message",
        "label": "ติดต่อเรา",
        "text": "ติดต่อเรา"
      }
    ]
  }
}
```

### ตัวอย่าง Flex Message

```json
{
  "type": "flex",
  "altText": "ข้อมูลสินค้า",
  "contents": {
    "type": "bubble",
    "body": {
      "type": "box",
      "layout": "vertical",
      "contents": [
        {
          "type": "text",
          "text": "สินค้าแนะนำ",
          "weight": "bold",
          "size": "xl"
        },
        {
          "type": "text",
          "text": "ราคาพิเศษ 999 บาท",
          "size": "sm",
          "color": "#999999"
        }
      ]
    }
  }
}
```

## ข้อมูลเพิ่มเติม

- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [Flex Message Simulator](https://developers.line.biz/flex-simulator/)
- [LINE Sticker List](https://developers.line.biz/en/docs/messaging-api/sticker-list/)

## License

LGPL-3
