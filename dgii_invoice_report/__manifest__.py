{
    'name': "Plantilla de facturas",
    'description': "Plantilla para facturas",
    'version': "1.0",
    'author': "Edwin de los Santos",
    'depends': ['ncf_manager','report'],
    'data': [
        'reports/account_invoice_report.xml',
        'views/reports.xml'
    ],
    'installable': True,
}