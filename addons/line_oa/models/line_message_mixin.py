# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    from linebot.exceptions import LineBotApiError
except ImportError:
    LineBotApiError = Exception


class LineMessageMixin(models.AbstractModel):
    _name = 'line.message.mixin'
    _description = 'Mixin สำหรับส่งข้อความ LINE'

    def _get_active_line_config(self, template=None, config_id=None):
        """ดึงการตั้งค่า LINE OA ที่ active
        
        Priority:
        1. ถ้ามี config_id ให้ใช้ตัวนั้น
        2. ถ้า template มี line_config_id ให้เลือก config ตัวแรก (active)
        3. ถ้าไม่มี ให้ search หา config ที่ active
        """
        # Priority 1: ถ้า user ระบุ config_id มาให้ใช้ตัวนั้น
        if config_id:
            config = self.env['line.oa.config'].browse(config_id)
            if config.exists():
                return config
        
        # Priority 2: ถ้ามี template ให้เลือก config ตัวแรกที่ active
        if template and template.line_config_id:
            active_config = template.line_config_id.filtered(lambda x: x.is_active)
            if active_config:
                return active_config[0]
        
        # Priority 3: ถ้าไม่มี ให้ search หา config ที่ active
        config = self.env['line.oa.config'].search([
            ('is_active', '=', True),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not config:
            raise UserError(_('ไม่พบการตั้งค่า LINE OA ที่ใช้งานอยู่\nกรุณาตั้งค่า LINE OA ก่อนใช้งาน'))
        
        return config

    def _create_message_log(self, template_id, send_method, **kwargs):
        """สร้างบันทึกการส่งข้อความ"""
        config = self._get_active_line_config()
        
        log_vals = {
            'template_id': template_id,
            'send_method': send_method,
            'config_id': config.id,
            'state': 'draft',
        }
        
        # เพิ่มข้อมูลผู้รับ
        if 'user_id' in kwargs:
            log_vals['user_id_line'] = kwargs['user_id']
        if 'user_ids' in kwargs:
            log_vals['user_ids_line'] = ','.join(kwargs['user_ids'])
        if 'reply_token' in kwargs:
            log_vals['reply_token'] = kwargs['reply_token']
        if 'message_content' in kwargs:
            log_vals['message_content'] = kwargs['message_content']
        
        return self.env['line.message.log'].create(log_vals)

    def _update_log_success(self, log, response_data=None):
        """อัพเดทบันทึกเมื่อส่งสำเร็จ"""
        log.write({
            'state': 'sent',
            'sent_date': fields.Datetime.now(),
            'response_data': str(response_data) if response_data else None,
        })

    def _update_log_failed(self, log, error_message):
        """อัพเดทบันทึกเมื่อส่งล้มเหลว"""
        log.write({
            'state': 'failed',
            'error_message': error_message,
        })

    def line_send_push_message(self, user_id, template_id, config_id=None, **kwargs):
        """
        ส่งข้อความแบบ Push (ส่งถึงผู้ใช้คนเดียว)
        
        Args:
            user_id (str): LINE User ID ของผู้รับ
            template_id (int): ID ของเทมเพลทข้อความ
            config_id (int, optional): ID ของ LINE OA Config (ถ้าไม่ระบุจะใช้ default)
        
        Returns:
            dict: ผลลัพธ์การส่ง
        """
        template = self.env['line.message.template'].browse(template_id)
        
        if not template.exists():
            raise UserError(_('ไม่พบเทมเพลทที่ระบุ'))
        
        # ดึง config จาก template หรือจาก parameter
        config = self._get_active_line_config(template=template, config_id=config_id)
        
        # สร้าง log
        log = self._create_message_log(
            template_id=template.id,
            send_method='push',
            user_id=user_id,
            message_content=template.text_content if template.message_type == 'text' else template.name
        )
        
        try:
            log.write({'state': 'sending'})
            
            # สร้าง message object
            message = template.get_message_object()
            
            # ส่งข้อความ
            line_bot_api = config.get_line_bot_api()
            
            # Log สำหรับ debug
            _logger.info(f"Sending LINE message - Config: {config.name}, User: {user_id}, Template: {template.name}, Message type: {template.message_type}")
            _logger.info(f"Channel Token: {config.channel_access_token[:20]}...")
            _logger.info(f"Message object: {message}")
            
            response = line_bot_api.push_message(user_id, message)
            
            # อัพเดท log
            self._update_log_success(log, response)
            
            return {
                'success': True,
                'log_id': log.id,
                'message': _('ส่งข้อความสำเร็จ'),
            }
            
        except LineBotApiError as e:
            error_msg = f"LINE API Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('การส่งข้อความล้มเหลว!\n%s') % error_msg)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('เกิดข้อผิดพลาด!\n%s') % error_msg)

    def line_send_multicast_message(self, user_ids, template_id, config_id=None, **kwargs):
        """
        ส่งข้อความแบบ Multicast (ส่งถึงหลายคน สูงสุด 500 คน)
        
        Args:
            user_ids (list): รายการ LINE User IDs ของผู้รับ
            template_id (int): ID ของเทมเพลทข้อความ
            config_id (int, optional): ID ของ LINE OA Config (ถ้าไม่ระบุจะใช้ default)
        
        Returns:
            dict: ผลลัพธ์การส่ง
        """
        if not isinstance(user_ids, list):
            raise UserError(_('user_ids ต้องเป็น list'))
        
        if len(user_ids) > 500:
            raise UserError(_('สามารถส่งถึงได้สูงสุด 500 คนต่อครั้ง'))
        
        template = self.env['line.message.template'].browse(template_id)
        config = self._get_active_line_config(template=template, config_id=config_id)
        
        if not template.exists():
            raise UserError(_('ไม่พบเทมเพลทที่ระบุ'))
        
        # สร้าง log
        log = self._create_message_log(
            template_id=template.id,
            send_method='multicast',
            user_ids=user_ids,
            message_content=template.text_content if template.message_type == 'text' else template.name
        )
        
        try:
            log.write({'state': 'sending'})
            
            # สร้าง message object
            message = template.get_message_object()
            
            # ส่งข้อความ
            line_bot_api = config.get_line_bot_api()
            response = line_bot_api.multicast(user_ids, message)
            
            # อัพเดท log
            self._update_log_success(log, response)
            
            return {
                'success': True,
                'log_id': log.id,
                'message': _('ส่งข้อความสำเร็จถึง %d คน') % len(user_ids),
            }
            
        except LineBotApiError as e:
            error_msg = f"LINE API Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('การส่งข้อความล้มเหลว!\n%s') % error_msg)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('เกิดข้อผิดพลาด!\n%s') % error_msg)

    def line_send_broadcast_message(self, template_id, config_id=None, **kwargs):
        """
        ส่งข้อความแบบ Broadcast (ส่งถึงผู้ติดตามทั้งหมด)
        
        Args:
            template_id (int): ID ของเทมเพลทข้อความ
            config_id (int, optional): ID ของ LINE OA Config (ถ้าไม่ระบุจะใช้ default)
        
        Returns:
            dict: ผลลัพธ์การส่ง
        """
        template = self.env['line.message.template'].browse(template_id)
        config = self._get_active_line_config(template=template, config_id=config_id)
        
        if not template.exists():
            raise UserError(_('ไม่พบเทมเพลทที่ระบุ'))
        
        # สร้าง log
        log = self._create_message_log(
            template_id=template.id,
            send_method='broadcast',
            message_content=template.text_content if template.message_type == 'text' else template.name
        )
        
        try:
            log.write({'state': 'sending'})
            
            # สร้าง message object
            message = template.get_message_object()
            
            # ส่งข้อความ
            line_bot_api = config.get_line_bot_api()
            response = line_bot_api.broadcast(message)
            
            # อัพเดท log
            self._update_log_success(log, response)
            
            return {
                'success': True,
                'log_id': log.id,
                'message': _('ส่งข้อความ Broadcast สำเร็จ'),
            }
            
        except LineBotApiError as e:
            error_msg = f"LINE API Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('การส่งข้อความล้มเหลว!\n%s') % error_msg)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('เกิดข้อผิดพลาด!\n%s') % error_msg)

    def line_send_reply_message(self, reply_token, template_id, config_id=None, **kwargs):
        """
        ส่งข้อความแบบ Reply (ตอบกลับข้อความจาก webhook)
        
        Args:
            reply_token (str): Reply token จาก webhook
            template_id (int): ID ของเทมเพลทข้อความ
            config_id (int, optional): ID ของ LINE OA Config (ถ้าไม่ระบุจะใช้ default)
        
        Returns:
            dict: ผลลัพธ์การส่ง
        """
        template = self.env['line.message.template'].browse(template_id)
        config = self._get_active_line_config(template=template, config_id=config_id)
        
        if not template.exists():
            raise UserError(_('ไม่พบเทมเพลทที่ระบุ'))
        
        # สร้าง log
        log = self._create_message_log(
            template_id=template.id,
            send_method='reply',
            reply_token=reply_token,
            message_content=template.text_content if template.message_type == 'text' else template.name
        )
        
        try:
            log.write({'state': 'sending'})
            
            # สร้าง message object
            message = template.get_message_object()
            
            # ส่งข้อความ
            line_bot_api = config.get_line_bot_api()
            response = line_bot_api.reply_message(reply_token, message)
            
            # อัพเดท log
            self._update_log_success(log, response)
            
            return {
                'success': True,
                'log_id': log.id,
                'message': _('ตอบกลับข้อความสำเร็จ'),
            }
            
        except LineBotApiError as e:
            error_msg = f"LINE API Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('การตอบกลับข้อความล้มเหลว!\n%s') % error_msg)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            _logger.error(error_msg)
            self._update_log_failed(log, error_msg)
            raise UserError(_('เกิดข้อผิดพลาด!\n%s') % error_msg)
