# -*- coding: utf-8 -*-

from odoo import models
from tools import is_ncf


class MarcosApiTools(models.Model):
    _inherit = 'marcos.api.tools'

    def is_ncf(self, value, type):
        return is_ncf(value, type)

    def invoice_ncf_validation(self, invoice):
        if not invoice.journal_id.ncf_remote_validation:
            return True

        elif not invoice.journal_id.purchase_type in ['exterior', 'import',
                                                      'others'] and invoice.journal_id.type == "purchase":

            if invoice.id:
                inv_in_draft = self.env["account.invoice"].search_count([('id', '!=', invoice.id),
                                                                         ('partner_id', '=', invoice.partner_id.id),
                                                                         ('move_name', '=', invoice.move_name),
                                                                         ('state', 'in', ('draft', 'cancel'))])
            else:
                inv_in_draft = self.env["account.invoice"].search_count([('partner_id', '=', invoice.partner_id.id),
                                                                         ('move_name', '=', invoice.move_name),
                                                                         ('state', 'in', ('draft', 'cancel'))])

            if inv_in_draft:
                return (200, u"Ncf duplicado", u"El número de comprobante fiscal digitado para este proveedor \n"
                                               u"ya se encuentra en una factura en borrador o cancelada.")

            inv_exist = self.env["account.invoice"].search_count(
                [('partner_id', '=', invoice.partner_id.id), ('number', '=', invoice.move_name),
                 ('state', 'in', ('open', 'paid'))])
            if inv_exist:
                return (300, u"Ncf duplicado", u"Este número de comprobante ya fue registrado para este proveedor!")

            if not is_ncf(invoice.move_name,invoice.type):
                return (500, u"Ncf invalido", u"El numero de comprobante fiscal no es valido! "
                                              u"no paso la validacion en DGII, Verifique que el NCF y el RNC del "
                                              u"proveedor esten correctamente digitados, si es de proveedor informal o de "
                                              u"gasto menor vefifique si debe solicitar nuevos numero.")

        return True

