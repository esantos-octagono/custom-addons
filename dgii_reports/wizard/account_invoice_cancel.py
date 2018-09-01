# -*- coding: utf-8 -*-

from odoo import models, api, _, fields
from odoo.exceptions import UserError


class AccountInvoiceCancel(models.TransientModel):
    _inherit = "account.invoice.cancel"

    anulation_type = fields.Selection([
        ("01", u"01 - DETERIORO DE FACTURA PRE-IMPRESA"),
        ("02", u"02 - ERRORES DE IMPRESIÓN (FACTURA PRE-IMPRESA)"),
        ("03", u"03 - IMPRESIÓN DEFECTUOSA"),
        ("04", u"04 - CORRECCIÓN DE LA INFORMACION"),
        ("05", u"05 - CAMBIO DE PRODUCTOS"),
        ("06", u"06 - DEVOLUCIÓN DE PRODUCTOS"),
        ("07", u"07 - OMISIÓN DE PRODUCTOS"),
        ("08", u"08 - ERRORES EN SECUENCIAS DE NCF"),
        ("09", u"09 - POR CESE DE OPERACIONES"),
        ("10", u"10 - PÉRDIDA O HURTO DE TALONARIO(S)")
    ], string=u"Tipo de anulación", required=True)

