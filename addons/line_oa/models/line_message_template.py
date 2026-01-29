# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)


class LineMessageTemplate(models.Model):
    _name = 'line.message.template'
    _description = 'เทมเพลทข้อความ LINE'
    _order = 'sequence, name'

    name = fields.Char(
        string='ชื่อเทมเพลท',
        required=True,
        help='ชื่อเรียกเทมเพลท'
    )
    line_config_id = fields.Many2many(
        'line.oa.config',
        string='LINE OA Configuration',
        help='เลือกการตั้งค่า LINE OA สำหรับเทมเพลทนี้'
    )
    project_service_id = fields.Many2one(
        'project.service',
        string='โครงการ/บริการ',
        help='เลือกโครงการ/บริการ (Project/Service) ที่ใช้งานเทมเพลทนี้'
    )
    sequence = fields.Integer(
        string='ลำดับ',
        default=10
    )
    message_type = fields.Selection([
        ('text', 'ข้อความธรรมดา (Text)'),
        ('image', 'รูปภาพ (Image)'),
        ('video', 'วิดีโอ (Video)'),
        ('audio', 'เสียง (Audio)'),
        ('sticker', 'สติกเกอร์ (Sticker)'),
        ('location', 'ตำแหน่งที่ตั้ง (Location)'),
        ('template_buttons', 'เทมเพลท - ปุ่ม (Template Buttons)'),
        ('template_confirm', 'เทมเพลท - ยืนยัน (Template Confirm)'),
        ('template_carousel', 'เทมเพลท - Carousel'),
        ('flex', 'Flex Message'),
        ('imagemap', 'Rich Message (Image Map)'),
    ], string='ประเภทข้อความ', required=True, default='text')
    
    description = fields.Text(
        string='คำอธิบาย',
        help='คำอธิบายเทมเพลท'
    )
    active = fields.Boolean(
        string='ใช้งาน',
        default=True
    )
    
    # Text Message Fields
    text_content = fields.Text(
        string='ข้อความ',
        help='เนื้อหาข้อความ (สูงสุด 5,000 ตัวอักษร)'
    )
    
    # Image Message Fields
    image_url = fields.Char(
        string='URL รูปภาพ',
        help='URL รูปภาพต้นฉบับ (HTTPS, JPG/PNG, สูงสุด 10MB)'
    )
    preview_image_url = fields.Char(
        string='URL รูปภาพ Preview',
        help='URL รูปภาพแสดงตัวอย่าง (HTTPS, JPG/PNG, สูงสุด 1MB)'
    )
    
    # Video Message Fields
    video_url = fields.Char(
        string='URL วิดีโอ',
        help='URL วิดีโอต้นฉบับ (HTTPS, MP4, สูงสุด 200MB)'
    )
    video_preview_url = fields.Char(
        string='URL รูปภาพ Preview วิดีโอ',
        help='URL รูปภาพแสดงตัวอย่างวิดีโอ'
    )
    
    # Audio Message Fields
    audio_url = fields.Char(
        string='URL เสียง',
        help='URL ไฟล์เสียง (HTTPS, M4A, สูงสุด 200MB)'
    )
    audio_duration = fields.Integer(
        string='ระยะเวลาเสียง (ms)',
        help='ระยะเวลาเสียงเป็นมิลลิวินาที'
    )
    
    # Sticker Message Fields
    sticker_package_id = fields.Char(
        string='Package ID สติกเกอร์',
        help='Package ID ของสติกเกอร์ LINE'
    )
    sticker_id = fields.Char(
        string='Sticker ID',
        help='Sticker ID ของสติกเกอร์ LINE'
    )
    
    # Location Message Fields
    location_title = fields.Char(
        string='ชื่อสถานที่',
        help='ชื่อสถานที่'
    )
    location_address = fields.Char(
        string='ที่อยู่',
        help='ที่อยู่สถานที่'
    )
    location_latitude = fields.Float(
        string='ละติจูด',
        digits=(10, 7),
        help='ละติจูดของสถานที่'
    )
    location_longitude = fields.Float(
        string='ลองจิจูด',
        digits=(10, 7),
        help='ลองจิจูดของสถานที่'
    )
    
    # Template & Flex Message Fields (JSON)
    template_json = fields.Text(
        string='Template JSON',
        help='JSON สำหรับ Template Message, Flex Message หรือ Image Map'
    )
    
    # Quick Reply
    has_quick_reply = fields.Boolean(
        string='มี Quick Reply',
        default=False
    )
    quick_reply_json = fields.Text(
        string='Quick Reply JSON',
        help='JSON สำหรับ Quick Reply items'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='บริษัท',
        default=lambda self: self.env.company
    )

    @api.constrains('text_content')
    def _check_text_length(self):
        """ตรวจสอบความยาวข้อความ"""
        for record in self:
            if record.message_type == 'text' and record.text_content:
                if len(record.text_content) > 5000:
                    raise ValidationError(_('ข้อความยาวเกิน 5,000 ตัวอักษร'))

    @api.constrains('template_json')
    def _check_json_valid(self):
        """ตรวจสอบความถูกต้องของ JSON"""
        for record in self:
            if record.template_json:
                try:
                    json.loads(record.template_json)
                except json.JSONDecodeError as e:
                    raise ValidationError(_('JSON ไม่ถูกต้อง: %s') % str(e))

    @api.constrains('quick_reply_json')
    def _check_quick_reply_json_valid(self):
        """ตรวจสอบความถูกต้องของ Quick Reply JSON"""
        for record in self:
            if record.has_quick_reply and record.quick_reply_json:
                try:
                    json.loads(record.quick_reply_json)
                except json.JSONDecodeError as e:
                    raise ValidationError(_('Quick Reply JSON ไม่ถูกต้อง: %s') % str(e))

    def action_send_test(self):
        """ส่งข้อความทดสอบ"""
        self.ensure_one()
        
        # เปิด wizard สำหรับกรอก User ID
        return {
            'name': _('ส่งข้อความทดสอบ'),
            'type': 'ir.actions.act_window',
            'res_model': 'line.message.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                'default_send_method': 'push',
            }
        }

    def get_message_object(self):
        """สร้าง message object สำหรับส่งผ่าน LINE API"""
        self.ensure_one()
        
        try:
            from linebot.models import (
                TextSendMessage, ImageSendMessage, VideoSendMessage,
                AudioSendMessage, LocationSendMessage, StickerSendMessage,
                TemplateSendMessage, FlexSendMessage, ImagemapSendMessage,
                QuickReply, QuickReplyButton
            )
        except ImportError:
            raise UserError(_('ไม่พบ LINE Bot SDK\nกรุณาติดตั้งด้วยคำสั่ง: pip install line-bot-sdk'))
        
        message = None
        
        # สร้าง message object ตามประเภท
        if self.message_type == 'text':
            message = TextSendMessage(text=self.text_content or '')
            
        elif self.message_type == 'image':
            message = ImageSendMessage(
                original_content_url=self.image_url,
                preview_image_url=self.preview_image_url or self.image_url
            )
            
        elif self.message_type == 'video':
            message = VideoSendMessage(
                original_content_url=self.video_url,
                preview_image_url=self.video_preview_url
            )
            
        elif self.message_type == 'audio':
            message = AudioSendMessage(
                original_content_url=self.audio_url,
                duration=self.audio_duration or 1000
            )
            
        elif self.message_type == 'sticker':
            message = StickerSendMessage(
                package_id=self.sticker_package_id,
                sticker_id=self.sticker_id
            )
            
        elif self.message_type == 'location':
            message = LocationSendMessage(
                title=self.location_title or '',
                address=self.location_address or '',
                latitude=self.location_latitude,
                longitude=self.location_longitude
            )
            
        elif self.message_type in ['template_buttons', 'template_confirm', 'template_carousel']:
            if not self.template_json:
                raise UserError(_('กรุณากรอก Template JSON'))
            template_data = json.loads(self.template_json)
            message = TemplateSendMessage.new_from_json_dict(template_data)
            
        elif self.message_type == 'flex':
            if not self.template_json:
                raise UserError(_('กรุณากรอก Flex Message JSON'))
            flex_data = json.loads(self.template_json)
            message = FlexSendMessage.new_from_json_dict(flex_data)
            
        elif self.message_type == 'imagemap':
            if not self.template_json:
                raise UserError(_('กรุณากรอก Image Map JSON'))
            imagemap_data = json.loads(self.template_json)
            message = ImagemapSendMessage.new_from_json_dict(imagemap_data)
        
        # เพิ่ม Quick Reply ถ้ามี
        if self.has_quick_reply and self.quick_reply_json and message:
            quick_reply_data = json.loads(self.quick_reply_json)
            message.quick_reply = QuickReply.new_from_json_dict(quick_reply_data)
        
        return message

    def action_send_project(self):
        """ส่งข้อความไปยัง LINE ID ของโครงการ"""
        self.ensure_one()
        
        if not self.project_service_id:
            raise UserError(_('ไม่พบโครงการ/บริการ (Project/Service) ที่เลือก'))
        
        project = self.project_service_id
        
        if not project.line_user_id:
            raise UserError(_('โครงการ "%s" ไม่มี LINE User ID') % project.project_name)
        
        # เปิด wizard และตั้งค่า user_id ของโครงการ
        return {
            'name': _('ส่งข้อความไปยังโครงการ'),
            'type': 'ir.actions.act_window',
            'res_model': 'line.message.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                'default_user_id': project.line_user_id,
                'default_send_method': 'push',
            }
        }
