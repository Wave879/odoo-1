# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class LineMessageLog(models.Model):
    _name = 'line.message.log'
    _description = 'บันทึกการส่งข้อความ LINE'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    display_name = fields.Char(
        string='ชื่อ',
        compute='_compute_display_name',
        store=True
    )
    template_id = fields.Many2one(
        'line.message.template',
        string='เทมเพลท',
        ondelete='set null'
    )
    message_type = fields.Selection(
        related='template_id.message_type',
        string='ประเภทข้อความ',
        store=True
    )
    send_method = fields.Selection([
        ('reply', 'Reply Message (ตอบกลับ)'),
        ('push', 'Push Message (ส่งถึงคนเดียว)'),
        ('multicast', 'Multicast Message (ส่งหลายคน)'),
        ('broadcast', 'Broadcast Message (ส่งทุกคน)'),
    ], string='วิธีการส่ง', required=True)
    
    # ผู้รับ
    recipient_type = fields.Selection([
        ('single', 'ผู้ใช้คนเดียว'),
        ('multiple', 'หลายคน'),
        ('all', 'ทุกคน'),
    ], string='ประเภทผู้รับ', compute='_compute_recipient_type', store=True)
    
    user_id_line = fields.Char(
        string='LINE User ID',
        help='LINE User ID ของผู้รับ (สำหรับ Push)'
    )
    user_ids_line = fields.Text(
        string='LINE User IDs',
        help='LINE User IDs ของผู้รับหลายคน (สำหรับ Multicast, คั่นด้วยเครื่องหมายจุลภาค)'
    )
    reply_token = fields.Char(
        string='Reply Token',
        help='Reply Token สำหรับตอบกลับข้อความ'
    )
    
    # สถานะ
    state = fields.Selection([
        ('draft', 'ร่าง'),
        ('sending', 'กำลังส่ง'),
        ('sent', 'ส่งสำเร็จ'),
        ('failed', 'ส่งล้มเหลว'),
    ], string='สถานะ', default='draft', required=True)
    
    # ผลลัพธ์
    sent_date = fields.Datetime(
        string='วันที่ส่ง',
        readonly=True
    )
    response_data = fields.Text(
        string='ข้อมูลตอบกลับ',
        readonly=True,
        help='ข้อมูลตอบกลับจาก LINE API'
    )
    error_message = fields.Text(
        string='ข้อความ Error',
        readonly=True
    )
    
    # ข้อมูลเพิ่มเติม
    message_content = fields.Text(
        string='เนื้อหาข้อความ',
        help='สำเนาเนื้อหาข้อความที่ส่ง'
    )
    config_id = fields.Many2one(
        'line.oa.config',
        string='การตั้งค่า LINE OA',
        ondelete='set null'
    )
    company_id = fields.Many2one(
        'res.company',
        string='บริษัท',
        default=lambda self: self.env.company
    )

    @api.depends('template_id', 'send_method', 'create_date')
    def _compute_display_name(self):
        for record in self:
            template_name = record.template_id.name if record.template_id else 'ไม่ระบุ'
            method_name = dict(record._fields['send_method'].selection).get(record.send_method, '')
            date_str = fields.Datetime.to_string(record.create_date) if record.create_date else ''
            record.display_name = f"{template_name} - {method_name} ({date_str})"

    @api.depends('send_method', 'user_id_line', 'user_ids_line')
    def _compute_recipient_type(self):
        for record in self:
            if record.send_method == 'broadcast':
                record.recipient_type = 'all'
            elif record.send_method == 'multicast':
                record.recipient_type = 'multiple'
            else:
                record.recipient_type = 'single'

    def action_view_details(self):
        """ดูรายละเอียดการส่ง"""
        self.ensure_one()
        return {
            'name': _('รายละเอียดการส่งข้อความ'),
            'type': 'ir.actions.act_window',
            'res_model': 'line.message.log',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
