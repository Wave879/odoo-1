from odoo import http
from odoo.http import request
from werkzeug.wsgi import wrap_file
import io


class EzFontController(http.Controller):

    @http.route('/ez_font/get_css', type='http', auth='public', csrf=False)
    def get_ez_font_css(self):
        """Generate and return dynamic CSS for active font"""
        try:
            EzFontSettings = request.env['ez.font.settings'].sudo()
            active_font = EzFontSettings.search([('is_active', '=', True)], limit=1)
            
            if active_font:
                css = active_font.generate_css()
                return request.make_response(css, [('Content-Type', 'text/css; charset=utf-8')])
            
            return request.make_response('', [('Content-Type', 'text/css; charset=utf-8')])
        except Exception as e:
            return request.make_response(f'/* Error: {str(e)} */', [('Content-Type', 'text/css; charset=utf-8')])

    @http.route('/ez_font/get_active_font', type='json', auth='public')
    def get_active_font_info(self):
        """Return active font information as JSON"""
        try:
            EzFontSettings = request.env['ez.font.settings'].sudo()
            active_font = EzFontSettings.search([('is_active', '=', True)], limit=1)
            
            if active_font:
                return {
                    'status': 'success',
                    'font_name': active_font.font_name,
                    'google_font_url': active_font.google_font_url,
                    'css_selectors': active_font.css_selectors,
                }
            
            return {'status': 'no_font'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

