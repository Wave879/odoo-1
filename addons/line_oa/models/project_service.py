# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectService(models.Model):
    _name = 'project.service'
    _description = 'Project/Service'
    _rec_name = 'project_name'

    project_code = fields.Char(
        string='Project Code',
        required=True,
        unique=True,
        help='รหัส Project ที่ไม่ซ้ำกัน'
    )
    project_name = fields.Char(
        string='Project Name',
        required=True,
        help='ชื่อ Project'
    )
    project_token_line = fields.Char(
        string='Project Token Line',
        help='Token Line สำหรับ Project นี้'
    )
    channel_secret = fields.Char(
        string='Channel Secret',
        help='Channel Secret'
    )
    channel_access_token = fields.Char(
        string='Channel Access Token',
        help='Channel Access Token'
    )
    message_type = fields.Selection([
        ('push', 'Push Message (ส่งถึงผู้ใช้คนเดียว)'),
        ('multicast', 'Multicast (ส่งถึงหลายคน)'),
    ], string='ส่งเสริด?', default='push', help='ประเภทของการส่งข้อความ')
    line_user_id = fields.Char(
        string='LINE User ID',
        help='ID ของผู้ใช้ LINE'
    )
    message_type = fields.Selection([
        ('push', 'Push Message (ส่งถึงผู้ใช้คนเดียว)'),
        ('multicast', 'Multicast (ส่งถึงหลายคน)'),
    ], string='วิธีการส่ง', default='push', help='ประเภทของการส่งข้อความ')
    project_sync_id = fields.Char(
        string='Project Sync ID',
        help='ID สำหรับ Sync'
    )
    project_pm = fields.Char(
        string='Project PM',
        help='ชื่อ Project Manager'
    )
    project_description = fields.Text(
        string='Project Description',
        help='คำอธิบาย Project'
    )
    project_sub_ids = fields.One2many(
        'project.service.sub',
        'project_id',
        string='Sub Services',
        help='บริการย่อยของ Project นี้'
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help='เปิด/ปิดการใช้งาน Project นี้'
    )
    image = fields.Binary(
        string='รูปภาพ',
        help='รูปภาพโลโก้หรือรูปประกอบของ Project'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )


class ProjectServiceSub(models.Model):
    _name = 'project.service.sub'
    _description = 'Project Sub Service'
    _rec_name = 'sub_service_name'

    project_id = fields.Many2one(
        'project.service',
        string='Project',
        required=True,
        ondelete='cascade'
    )
    project_sub_code = fields.Char(
        string='Project Sub Code',
        required=True,
        help='รหัส Sub Service'
    )
    sub_service_name = fields.Char(
        string='Sub Service Name',
        required=True,
        help='ชื่อ Sub Service'
    )
    project_pm = fields.Char(
        string='Project PM',
        help='ชื่อ Project Manager'
    )
    project_description = fields.Text(
        string='Project Description',
        help='คำอธิบาย Sub Service'
    )
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help='เปิด/ปิดการใช้งาน Sub Service นี้'
    )
