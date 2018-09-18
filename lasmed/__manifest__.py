{
    'name': "Facturacion de servicios por ars",

    'summary': """
    """,

    'description': """
    """,

    'author': "OCTAGONO SRL - Write by Edwin de los Santos",
    'website': "http://octagono.com.do",

    'category': 'Account',
    'version': '10.0',

    'depends': ['base','product', 'account','medical','medical_insurance'],

    'data': [
        "views/account_invoice_form.xml",
        "views/product_form_view.xml",
        "wizard/wizard_cobers.xml",
        "report/ars_report.xml"

    ],
    'demo': [],
}
