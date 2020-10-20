# -*- coding: utf-8 -*-
{
    'name': "Attendances_auto",

    'summary': """
        Automatic Check-in and Checkout """,

    'description': """
Check-in & Checkout
====================
Now you can automatically check in and out for your business. The administrator can create all holidays of the year
so that project does not create a check-in and check-out for this day.
""",

    'author': "Simão Duarte",
    'website': "http://www.odoogap.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/attendances_views.xml',
        'views/cron.xml',
        'views/public_holidays_views.xml',
        'views/res_config_settings_views.xml',
        'data/defaults.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
