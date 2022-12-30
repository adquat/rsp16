# -*- coding: utf-8 -*-
{
    'name': "Adquat RSP",

    'summary': """
        Personalisations diverses pour RSP""",

    'description': """
        Personnalisations diverses pour RSP
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
                # 'report_xlsx',
                'base_geolocalize',
                'sms',
                'documents_project',
                'partner_firstname',
    ],

    # always loaded
    'data': [
        'report/report.xml',
        'data/sms_template.xml',
        'data/mail_template.xml',
        'data/project_data.xml',
        'data/ir.model.access.csv',
        'views/fdi_view.xml',
        'views/sav_view.xml',
        'views/document_view.xml',
        'views/project_view.xml',
        'views/partner_view.xml',
        'wizard/wizard_view.xml',
    ],
    'license': 'LGPL-3',
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
}