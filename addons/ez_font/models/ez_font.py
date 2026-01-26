from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EzFontSettings(models.Model):
    _name = 'ez.font.settings'
    _description = 'Ez Font Settings'
    _rec_name = 'font_name'

    font_name = fields.Char(
        string='ชื่อฟอนต์',
        required=True,
        help='ชื่อฟอนต์ที่จะใช้'
    )
    
    google_font_url = fields.Char(
        string='Google Font URL',
        required=True,
        help='ลิงก์ Google Fonts เช่น: https://fonts.googleapis.com/css2?family=Prompt'
    )
    
    css_selectors = fields.Text(
        string='CSS Selectors',
        default='body, .o_web_client',
        help='ตัวเลือก CSS ที่ต้องการใช้ฟอนต์นี้ (คั่นด้วยเครื่องหมายจุลภาค)'
    )
    
    is_active = fields.Boolean(
        string='ใช้งาน',
        default=False,
        help='เปิดใช้งานฟอนต์นี้'
    )
    
    description = fields.Text(
        string='คำอธิบาย',
        help='คำอธิบายเพิ่มเติมเกี่ยวกับฟอนต์นี้'
    )
    
    created_date = fields.Datetime(
        string='วันที่สร้าง',
        default=fields.Datetime.now,
        readonly=True
    )
    
    modified_date = fields.Datetime(
        string='วันที่แก้ไข',
        default=fields.Datetime.now,
        readonly=True
    )

    @api.constrains('is_active')
    def _check_only_one_active(self):
        """Ensure only one font is active at a time"""
        active_fonts = self.search([('is_active', '=', True)])
        if len(active_fonts) > 1:
            raise ValidationError('สามารถเลือกฟอนต์ที่ใช้งานได้เพียงหนึ่งฟอนต์เท่านั้น')

    @api.model
    def get_active_font(self):
        """Get the currently active font"""
        active_font = self.search([('is_active', '=', True)], limit=1)
        if active_font:
            return {
                'font_name': active_font.font_name,
                'google_font_url': active_font.google_font_url,
                'css_selectors': active_font.css_selectors,
            }
        return None

    def generate_css(self):
        """Generate CSS for the active font"""
        if not self.is_active:
            return ''
        
        css_selectors = self.css_selectors or 'body, .o_web_client'
        css = f"""
@import url('{self.google_font_url}');

{css_selectors} {{
    font-family: '{self.font_name}' !important;
}}
        """
        return css.strip()

    @api.model
    def get_active_font_css(self):
        """Get CSS for all active fonts"""
        active_font = self.search([('is_active', '=', True)], limit=1)
        if active_font:
            return active_font.generate_css()
        return ''

    def action_apply_font(self):
        """Apply this font and deactivate others"""
        # Deactivate all other fonts
        self.search([('id', '!=', self.id), ('is_active', '=', True)]).write({'is_active': False})
        # Activate this font
        self.is_active = True
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'สำเร็จ',
                'message': f'ฟอนต์ {self.font_name} ถูกใช้งาน',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_deactivate_font(self):
        """Deactivate this font"""
        self.is_active = False
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'สำเร็จ',
                'message': f'ฟอนต์ {self.font_name} ถูกยกเลิกใช้งาน',
                'type': 'success',
                'sticky': False,
            }
        }
