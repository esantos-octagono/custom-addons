# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    ars = fields.Many2one(comodel_name='medical.insurance.company',string="ARS")
    afiliacion = fields.Many2one(comodel_name='medical.insurance.plan',string=u'Afiliación')
    tipo_seguro = fields.Selection([
        ('state', 'Estado'),
        ('labor_union', 'Sindicato / Sindical'),
        ('private', 'Privado'),
    ],
        help=u'¿A qué tipo de entidad se proporciona este seguro?',
        related='afiliacion.insurance_affiliation',
        string= 'Tipo Seguro'
    )
    auth_num = fields.Char(string=u'# Autorización')
    cober = fields.Monetary("Cobertura")

    @api.onchange('cober')
    def _onchange_cober(self):
        if self.cober <= self.amount_total:
            self.amount_total = self.amount_total - self.cober
        else:
            raise ValidationError("La cobertura debe ser menor o igual al total de la factura, confirme el monto con el suplidor")

    @api.multi
    def action_invoice_open(self):
        cober_prod = self.env['product.template'].search([('default_code', '=', 'insurance_cober')])
        prod = self.env['product.product'].search([('product_tmpl_id', '=', cober_prod.id)])
        if self.cober > 0:
            self.invoice_line_ids = [(0, 0, {'name': prod.name, 'product_id': prod.id, 'account_id': prod.property_account_income_id ,'price_unit': 0 - self.cober})]
        if self.amount_total == 0.0:
            self.journal_id = self.env['account.journal'].search([('code', '=', 'noncf')]).id
        else:
            pass

        return super(AccountInvoice, self).action_invoice_open()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine,self)._onchange_product_id()
        ars = self.env.context.get("ars_id", None)
        if ars:
            ppla = None

            if self.product_id:
                ppla = self.env['product.price.list.ars'].search([('product_tmpl_id','=',self.product_id.product_tmpl_id.id),('ars','=',ars)])

            if ppla:
                self.price_unit = ppla.price

        return res

