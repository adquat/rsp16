# -*- coding: utf-8 -*-
{
    'name': "Adquat RSP",

    'summary': """
        Personalisations diverses pour RSP""",

    'description': """
        Personalisations diverses pour RSP
    """,

    'author': "Adquat",
    'website': "http://www.adquat.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'project',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'project',
                'hr',
                'report_xlsx',
                'base_geolocalize',
                'sms',
                'documents_project',
    ],

    # always loaded
    'data': [
        'data/ir.model.access.csv',
        'data/project_data.xml',
        'views/mail_template.xml',
        'views/fdi_view.xml',
        'views/sav_view.xml',
        'views/project_view.xml',
        'views/document_view.xml',
        'views/partner_view.xml',
        'report/report.xml',
    ],
    'license': 'LGPL-3',
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
}