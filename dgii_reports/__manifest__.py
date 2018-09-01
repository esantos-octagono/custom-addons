# -*- coding: utf-8 -*-

{
    'name': 'Dgii Reports',
    'author': 'Asegurado',
    'category': 'Accounting',
    'depends': [
        'account',
        'marcos_api_tools',
        'ncf_manager',
    ],
    'data': [
        'views/account_journal.xml',
        'views/account_invoice_form.xml'
    ],
    'installable': True,
}
