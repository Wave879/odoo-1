# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

try:
    from linebot import LineBotApi
    from linebot.exceptions import LineBotApiError
except ImportError:
    _logger.warning('LINE Bot SDK not installed. Please install: pip install line-bot-sdk')
    LineBotApi = None
    LineBotApiError = Exception


class LineOAConfig(models.Model):
    _name = 'line.oa.config'
    _description = 'การตั้งค่า LINE Official Account'
    _rec_name = 'name'

    name = fields.Char(
        string='ชื่อการตั้งค่า',
        required=True,
        help='ชื่อเรียกสำหรับการตั้งค่านี้'
    )
    channel_access_token = fields.Char(
        string='Channel Access Token',
        required=True,
        help='Token สำหรับเข้าถึง LINE Messaging API'
    )
    channel_secret = fields.Char(
        string='Channel Secret',
        required=True,
        help='Secret key สำหรับยืนยันตัวตน'
    )
    webhook_url = fields.Char(
        string='Webhook URL',
        compute='_compute_webhook_url',
        help='URL สำหรับรับ webhook จาก LINE'
    )
    is_active = fields.Boolean(
        string='ใช้งาน',
        default=True,
        help='เปิด/ปิดการใช้งานการตั้งค่านี้'
    )
    connection_status = fields.Selection([
        ('not_tested', 'ยังไม่ได้ทดสอบ'),
        ('success', 'เชื่อมต่อสำเร็จ'),
        ('failed', 'เชื่อมต่อล้มเหลว'),
    ], string='สถานะการเชื่อมต่อ', default='not_tested', readonly=True)
    last_test_date = fields.Datetime(
        string='ทดสอบล่าสุดเมื่อ',
        readonly=True
    )
    error_message = fields.Text(
        string='ข้อความ Error',
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='บริษัท',
        default=lambda self: self.env.company
    )

    @api.depends('company_id')
    def _compute_webhook_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.webhook_url = f"{base_url}/line_oa/webhook"

    @api.model_create_multi
    def create(self, vals_list):
        """เมื่อสร้าง config ใหม่ที่เปิดใช้งาน ให้ปิด config อื่นในบริษัทเดียวกัน"""
        records = super().create(vals_list)
        for record in records:
            if record.is_active:
                self.env['line.oa.config'].search([
                    ('company_id', '=', record.company_id.id),
                    ('is_active', '=', True),
                    ('id', '!=', record.id)
                ]).write({'is_active': False})
        return records

    def write(self, vals):
        """เมื่อแก้ไข is_active เป็น True ให้ปิด config อื่นในบริษัทเดียวกัน"""
        result = super().write(vals)
        if vals.get('is_active'):
            for record in self:
                self.env['line.oa.config'].search([
                    ('company_id', '=', record.company_id.id),
                    ('is_active', '=', True),
                    ('id', '!=', record.id)
                ]).write({'is_active': False})
        return result

    def action_test_connection(self):
        """ทดสอบการเชื่อมต่อกับ LINE API"""
        self.ensure_one()
        
        if not LineBotApi:
            raise UserError(_('ไม่พบ LINE Bot SDK\nกรุณาติดตั้งด้วยคำสั่ง: pip install line-bot-sdk'))
        
        try:
            line_bot_api = LineBotApi(self.channel_access_token)
            # ทดสอบด้วยการดึงข้อมูล quota
            quota = line_bot_api.get_message_quota()
            
            self.write({
                'connection_status': 'success',
                'last_test_date': fields.Datetime.now(),
                'error_message': False,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('สำเร็จ!'),
                    'message': _('เชื่อมต่อกับ LINE OA สำเร็จ\nQuota ที่เหลือ: %s') % quota.value,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except LineBotApiError as e:
            error_msg = f"LINE API Error: {str(e)}"
            self.write({
                'connection_status': 'failed',
                'last_test_date': fields.Datetime.now(),
                'error_message': error_msg,
            })
            raise UserError(_('การเชื่อมต่อล้มเหลว!\n%s') % error_msg)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.write({
                'connection_status': 'failed',
                'last_test_date': fields.Datetime.now(),
                'error_message': error_msg,
            })
            raise UserError(_('เกิดข้อผิดพลาด!\n%s') % error_msg)

    def get_line_bot_api(self):
        """สร้าง LINE Bot API instance"""
        self.ensure_one()
        
        if not LineBotApi:
            raise UserError(_('ไม่พบ LINE Bot SDK\nกรุณาติดตั้งด้วยคำสั่ง: pip install line-bot-sdk'))
        
        if not self.is_active:
            raise UserError(_('การตั้งค่านี้ถูกปิดการใช้งาน'))
        
        return LineBotApi(self.channel_access_token)
