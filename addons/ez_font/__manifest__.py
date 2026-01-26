{
    'name': 'Ez Font',
    'version': '16.0.1.0.0',
    'category': 'Tools',
    'summary': 'Dynamic Font Management for Backend and Frontend',
    'description': """
        Ez Font Module allows users to download and change system fonts dynamically
        without modifying any existing addons or core files.
        
        Features:
        - Manage custom fonts from Google Fonts
        - Apply fonts to both backend and frontend
        - Dynamic CSS injection
        - No server restart required
    """,
    'author': 'Odoo Developer',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/ez_font_view.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ez_font/static/src/js/ez_font.js',
        ],
        'web.assets_frontend': [
            'ez_font/static/src/js/ez_font.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
