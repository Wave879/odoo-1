{
    'name': 'LINE OA Notification',
    'version': '1.0',
    'summary': 'ระบบแจ้งเตือนผ่าน LINE Official Account',
    'description': """
        ระบบแจ้งเตือนและส่งข้อความผ่าน LINE Official Account
        
        รองรับรูปแบบข้อความ:
        - ข้อความธรรมดา (Text Message)
        - รูปภาพ (Image Message)
        - วิดีโอ (Video Message)
        - เสียง (Audio Message)
        - สติกเกอร์ (Sticker Message)
        - ตำแหน่งที่ตั้ง (Location Message)
        - เทมเพลท (Template Message: Buttons, Confirm, Carousel)
        - Flex Message
        - Rich Message
        - Quick Reply
        
        รูปแบบการส่ง:
        - Reply Message (ตอบกลับข้อความ)
        - Push Message (ส่งถึงผู้ใช้คนเดียว)
        - Multicast Message (ส่งถึงหลายคน)
        - Broadcast Message (ส่งถึงผู้ติดตามทั้งหมด)
    """,
    'category': 'Tools',
    'author': "Betimes Solution Co., Ltd.",
    'website': "https://www.betimes.biz/",
    'depends': ['base', 'web'],
    'data': [
        'security/line_oa_security.xml',
        'security/ir.model.access.csv',
        'views/line_oa_config_views.xml',
        'views/line_message_template_views.xml',
        'views/line_message_log_views.xml',
        'views/line_message_send_wizard_views.xml',
        'views/project_service_views.xml',
        'views/line_oa_menu.xml',
        'data/message_type_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['linebot'],
    },
}
