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

    'depends': ['base','sale','product', 'account','medical','medical_insurance'],

    'data': [
        "security/ir.model.access.csv",
        "views/account_invoice_form.xml",
        "views/sale_order_form.xml",
        "views/res_partner.xml",
        "views/product_form_view.xml",
        "wizard/wizard_cobers.xml",
        "report/ars_report.xml"

    ],
    'demo': [],
}
