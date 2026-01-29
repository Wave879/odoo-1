# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    from linebot import LineBotApi
    from linebot.models import TextSendMessage
    from linebot.exceptions import LineBotApiError
except ImportError:
    _logger.warning('LINE Bot SDK not installed. Please install: pip install line-bot-sdk')
    LineBotApi = None
    LineBotApiError = Exception


class LineMessageSendWizard(models.TransientModel):
    _name = 'line.message.send.wizard'
    _description = 'Wizard ส่งข้อความ LINE ทดสอบ'
    
    line_config_id = fields.Many2one(
        'line.oa.config',
        string='LINE OA Configuration',
        required=False,
        help='เลือก LINE OA Configuration ที่ใช้ส่ง (ถ้าไม่เลือก จะใช้ config ที่ template ระบุ)'
    )
    template_id = fields.Many2one(
        'line.message.template',
        string='เทมเพลท',
        required=True
    )
    send_method = fields.Selection([
        ('push', 'Push Message (ส่งถึงผู้ใช้คนเดียว)'),
        ('multicast', 'Multicast (ส่งถึงหลายคน)'),
    ], string='วิธีการส่ง', default='push', required=True)
    
    line_user_id = fields.Many2one(
        'line.user',
        string='เลือก LINE User (เคยส่ง)',
        help='เลือกจากรายชื่อที่เคยส่งไป'
    )
    user_id = fields.Char(
        string='LINE User ID',
        help='LINE User ID ของผู้รับ (เช่น U1234567890abcdef...)'
    )
    user_ids = fields.Text(
        string='LINE User IDs (หลายคน)',
        help='LINE User IDs คั่นด้วยเครื่องหมายจุลภาค (,) หรือขึ้นบรรทัดใหม่'
    )
    @api.onchange('line_user_id')
    def _onchange_line_user_id(self):
        """เมื่อเลือก LINE user ให้เติม user_id โดยอัตโนมัติ"""
        if self.line_user_id:
            self.user_id = self.line_user_id.line_user_id
    
    @api.onchange('send_method')
    def _onchange_send_method(self):
        """เปลี่ยนฟิลด์ที่แสดงตาม send_method"""
        if self.send_method == 'push':
            self.user_ids = False
        else:
            self.user_id = False
    
    def action_send(self):
        """ส่งข้อความทดสอบ"""
        self.ensure_one()
        
        print("\\n\\n" + "="*60)
        print("🔥 [26/Jan/2026] START action_send() - LINE MESSAGE WIZARD")
        print("="*60)
        _logger.warning("🔥 [26/Jan/2026] START action_send() - LINE MESSAGE WIZARD")
        
        print(f"Template ID: {self.template_id.id}, Name: {self.template_id.name}")
        print(f"Send method: {self.send_method}")
        print(f"User ID (push): {self.user_id}")
        print(f"User IDs (multicast): {self.user_ids}")
        
        _logger.warning(f"Template: {self.template_id.name}, Send method: {self.send_method}")
        _logger.warning(f"User ID: {self.user_id}, User IDs: {self.user_ids}")
        
        if not LineBotApi:
            raise UserError(_('ไม่พบ LINE Bot SDK\nกรุณาติดตั้งด้วยคำสั่ง: pip install line-bot-sdk'))
        
        # ดึงการตั้งค่า LINE OA
        # Priority: user choice → template's config → active config
        print(f"Manual line_config_id selected: {self.line_config_id}")
        print(f"Template's line_config_id: {self.template_id.line_config_id}")
        
        line_config = self.line_config_id or self.template_id.line_config_id
        
        print(f"Final selected config: {line_config}")
        _logger.warning(f"Final selected config object: {line_config}, Type: {type(line_config)}")
        
        # ตรวจสอบว่า config ถูก activate ไหม
        if line_config:
            if not line_config.is_active:
                raise UserError(_('Configuration "%s" ถูกปิดการใช้งาน\nกรุณาเปิดใช้งานก่อนส่ง') % line_config.name)
        else:
            # ถ้าไม่มี config ที่ระบุ ให้ค้นหา active config
            line_config = self.env['line.oa.config'].search([
                ('is_active', '=', True)
            ], limit=1)
        
        if not line_config:
            raise UserError(_('ไม่พบการตั้งค่า LINE OA ที่เปิดใช้งาน\nกรุณาเลือก Configuration ในเทมเพลทหรือเปิดใช้งาน Configuration'))
        
        print(f"✅ Using config: {line_config.name}, is_active: {line_config.is_active}, ID: {line_config.id}")
        _logger.warning(f"✅ Using config: {line_config.name}, is_active: {line_config.is_active}, ID: {line_config.id}")
        
        # ตรวจสอบ User ID
        if self.send_method == 'push' and not self.user_id:
            raise UserError(_('กรุณากรอก LINE User ID'))
        elif self.send_method == 'multicast' and not self.user_ids:
            raise UserError(_('กรุณากรอก LINE User IDs'))
        
        # สร้าง message object
        message = self.template_id.get_message_object()
        
        print(f"🚀 About to call LINE API with:")
        print(f"  - Config: {line_config.name}")
        print(f"  - Method: {self.send_method}")
        print(f"  - User: {self.user_id if self.send_method == 'push' else 'multicast'}")
        
        try:
            line_bot_api = line_config.get_line_bot_api()
            
            if self.send_method == 'push':
                # ส่งถึงผู้ใช้คนเดียว
                print(f"📤 Pushing to {self.user_id}")
                _logger.warning(f"📤 Pushing to {self.user_id}")
                line_bot_api.push_message(self.user_id, message)
                print(f"✅ Push successful!")
                
                # บันทึก LINE User ที่เคยส่ง
                self.env['line.user'].get_or_create_line_user(self.user_id)
                
                # บันทึก log
                self.env['line.message.log'].create({
                    'config_id': line_config.id,
                    'user_id_line': self.user_id,
                    'send_method': 'push',
                    'message_content': self._get_message_content(),
                    'state': 'sent',
                    'template_id': self.template_id.id,
                    'sent_date': fields.Datetime.now()
                })
                
                success_message = _('ส่งข้อความสำเร็จ!\nส่งถึง: %s') % self.user_id
                
            else:
                # ส่งถึงหลายคน
                user_id_list = self._parse_user_ids(self.user_ids)
                
                if not user_id_list:
                    raise UserError(_('ไม่พบ User ID ที่ถูกต้อง'))
                
                # LINE API รองรับสูงสุด 500 คนต่อครั้ง
                if len(user_id_list) > 500:
                    raise UserError(_('สามารถส่งได้สูงสุด 500 คนต่อครั้ง\nปัจจุบันมี %s คน') % len(user_id_list))
                
                line_bot_api.multicast(user_id_list, message)
                
                # บันทึก log สำหรับแต่ละคน
                for user_id in user_id_list:
                    self.env['line.message.log'].create({
                        'config_id': line_config.id,
                        'user_id_line': user_id,
                        'send_method': 'multicast',
                        'message_content': self._get_message_content(),
                        'state': 'sent',
                        'template_id': self.template_id.id,
                        'sent_date': fields.Datetime.now()
                    })
                
                success_message = _('ส่งข้อความสำเร็จ!\nส่งถึง %s คน') % len(user_id_list)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('✅ สำเร็จ'),
                    'message': success_message,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except LineBotApiError as e:
            error_msg = str(e)
            
            print(f"❌ LINE API ERROR: {error_msg}")
            print(f"Config used: {line_config.name if line_config else 'NONE'}")
            print(f"Config is_active: {line_config.is_active if line_config else 'N/A'}")
            
            _logger.error(f"❌ LINE API ERROR on config '{line_config.name if line_config else 'NONE'}': {error_msg}")
            _logger.error(f"Config details - ID: {line_config.id}, is_active: {line_config.is_active}, Channel: {line_config.channel_access_token[:20] if line_config.channel_access_token else 'NONE'}...")
            
            # บันทึก error log
            if self.send_method == 'push':
                self.env['line.message.log'].create({
                    'config_id': line_config.id,
                    'user_id_line': self.user_id,
                    'send_method': 'push',
                    'message_content': self._get_message_content(),
                    'state': 'failed',
                    'error_message': error_msg,
                    'template_id': self.template_id.id
                })
            
            raise UserError(_('❌ เกิดข้อผิดพลาดจาก LINE API:\n%s') % error_msg)
            
        except Exception as e:
            error_msg = str(e)
            
            # บันทึก error log
            if self.send_method == 'push':
                self.env['line.message.log'].create({
                    'config_id': line_config.id,
                    'user_id_line': self.user_id,
                    'send_method': 'push',
                    'message_content': self._get_message_content(),
                    'state': 'failed',
                    'error_message': error_msg,
                    'template_id': self.template_id.id
                })
            
            raise UserError(_('❌ เกิดข้อผิดพลาด:\n%s') % error_msg)
    
    def _parse_user_ids(self, user_ids_text):
        """แปลง text เป็น list ของ user IDs"""
        if not user_ids_text:
            return []
        
        # แยกด้วย comma หรือ newline
        user_ids = []
        for line in user_ids_text.replace(',', '\n').split('\n'):
            user_id = line.strip()
            if user_id:
                user_ids.append(user_id)
        
        return user_ids
    
    def _get_message_content(self):
        """ดึงเนื้อหาข้อความสำหรับบันทึก log"""
        if self.template_id.message_type == 'text':
            return self.template_id.text_content
        elif self.template_id.message_type == 'sticker':
            return f"Sticker: {self.template_id.sticker_package_id}/{self.template_id.sticker_id}"
        elif self.template_id.message_type == 'image':
            return f"Image: {self.template_id.image_url}"
        else:
            return f"{self.template_id.message_type.upper()} Message"

    def action_send_project(self):
        """ส่งข้อความไปยัง LINE ID ของโครงการ"""
        self.ensure_one()
        
        # ตรวจสอบว่ามีการเลือก project service ไหม
        if not self.template_id.project_service_id:
            raise UserError(_('ไม่พบโครงการ/บริการ (Project/Service) ที่เลือก\nกรุณาเลือกโครงการในเทมเพลท'))
        
        project = self.template_id.project_service_id
        
        # ตรวจสอบว่ามี LINE User ID ไหม
        if not project.line_user_id:
            raise UserError(_('โครงการ "%s" ไม่มี LINE User ID\nกรุณาเพิ่ม LINE User ID ในข้อมูลโครงการ') % project.project_name)
        
        # ส่งข้อความไปที่ LINE ID ของโครงการ
        self.user_id = project.line_user_id
        self.send_method = 'push'
        
        # เรียก action_send เพื่อส่งข้อความ
        return self.action_send()
