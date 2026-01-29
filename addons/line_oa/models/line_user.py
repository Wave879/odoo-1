# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class LineUser(models.Model):
    _name = 'line.user'
    _description = 'LINE User - รายชื่อผู้ใช้ที่เคยส่ง'
    _order = 'last_sent_date desc'
    _rec_name = 'line_user_id'

    line_user_id = fields.Char(
        string='LINE User ID',
        required=True,
        unique=True,
        help='LINE User ID'
    )
    display_name = fields.Char(
        string='ชื่อ',
        help='ชื่อเรียก (ถ้ามี)'
    )
    first_sent_date = fields.Datetime(
        string='ส่งครั้งแรก',
        default=fields.Datetime.now,
        readonly=True
    )
    last_sent_date = fields.Datetime(
        string='ส่งครั้งล่าสุด',
        default=fields.Datetime.now
    )
    send_count = fields.Integer(
        string='จำนวนครั้งที่ส่ง',
        default=1
    )
    notes = fields.Text(
        string='หมายเหตุ'
    )
    company_id = fields.Many2one(
        'res.company',
        string='บริษัท',
        default=lambda self: self.env.company
    )

    @api.model
    def get_or_create_line_user(self, line_user_id, display_name=''):
        """ดึงหรือสร้าง LINE User record"""
        user = self.search([
            ('line_user_id', '=', line_user_id),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if user:
            # อัพเดทข้อมูลการส่ง
            user.write({
                'last_sent_date': fields.Datetime.now(),
                'send_count': user.send_count + 1,
                'display_name': display_name or user.display_name,
            })
        else:
            # สร้างใหม่
            user = self.create({
                'line_user_id': line_user_id,
                'display_name': display_name,
                'first_sent_date': fields.Datetime.now(),
                'last_sent_date': fields.Datetime.now(),
                'send_count': 1,
            })

        return user
