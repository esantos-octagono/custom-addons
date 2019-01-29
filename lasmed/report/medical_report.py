# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class MedicalReport(models.Model):
    _name = "medical.report"
    _description = "Reporte de Medicos"
    _auto = False
    _rec_name = 'date'

    date = fields.Date('Fecha')
    partner_id = fields.Many2one('res.partner','Cliente')
    praticant = fields.Many2one('medical.practitioner','Medico')
    ars = fields.Many2one('medical.insurance.company')
    currency_id = fields.Many2one('res.currency','Moneda')
    invoice_id = fields.Many2one('account.invoice','Factura')
    product_id = fields.Many2one('product.product','Servicio')
    cobertura = fields.Monetary('Cobertura')
    monto = fields.Monetary('Monto')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW {} as (
        SELECT
            ail.id,
            ai.partner_id,
            ai.ars,
            ai.date,
            ail.praticant,
            ai.currency_id,
            ai.id as invoice_id,
            ail.product_id,
            ai.cober as cobertura,
            ail.price_subtotal as monto
        from account_invoice_line ail
        inner join account_invoice ai on ail.invoice_id = ai.id
        WHERE ai.is_settle = FALSE and ai.type ='out_invoice'

        )""".format(self._table))




