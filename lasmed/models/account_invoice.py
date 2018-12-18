# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    praticant = fields.Many2one('medical.practitioner', u"Referido por:")
    ars = fields.Many2one(comodel_name='medical.insurance.company',string="ARS")
    afiliacion = fields.Char(string=u'Afiliación')
    tipo_seguro = fields.Selection([
        ('insured', 'Asegurado'),
        ('private', 'Privado'),
    ],
        string = 'Tipo Seguro'
    )
    auth_num = fields.Char(string=u'# Autorización')
    cober = fields.Monetary("Cobertura")
    discount = fields.Monetary("Descuento")
    cober_diference = fields.Monetary("Total a pagar", compute="_onchange_cober", store=True)
    settled = fields.Boolean(string="Liquidada", default=False)
    is_settle = fields.Boolean(string="Es liquidacion", default=False)

    @api.multi
    def compute_amount_cober_total(self):
        invoices = self.env['account.invoice'].search([])
        for rec in invoices:
            amount = 0.0
            for line in rec.invoice_line_ids:
                if line.product_id.code == "insurance_cober":
                    pass
                else:
                    amount += line.price_unit

            rec.amount_cober_total = amount

    amount_cober_total = fields.Monetary("Total", store=True, compute='compute_amount_cober_total')

    @api.depends('cober','state','discount')
    @api.multi
    def _onchange_cober(self):

        if self.cober <= self.amount_total and self.state == "draft":
            self.cober_diference = self.amount_total - self.cober - self.discount
        elif self.state =="open":
            self.cober_diference = self.amount_total
        elif self.cober <= self.amount_untaxed and self.state == "draft":
            pass
        elif self.state in ['paid','cancel']:
            pass
        elif self.cober > self.amount_total and len(self.payment_ids) == 0 and self.amount_total !=0:
            if self.anulation_type:
                pass
            else:
                raise ValidationError("La cobertura debe ser menor o igual al total de la factura, confirme el monto con el suplidor")

    @api.onchange('amount_untaxed','discount','invoice_line_ids')
    def _onchange_amount_total(self):
        amount = self.amount_untaxed + self.amount_tax
        if self.discount < 0.0:
            raise ValidationError("El descuento debe ser positivo")
            self.discount = False
        elif self.discount + self.cober > self.amount_total:
            raise ValidationError("El descuento debe ser menor o igual al monto a pagar")
            self.discount = False
        else:
            print "Descuento: "+ str(self.discount)
            self.cober_diference = self.amount_total - self.cober - self.discount
            print "Total a Pagar: "+ str(self.cober_diference)

    @api.multi
    def action_invoice_open(self):
        cober_prod = self.env['product.template'].search([('default_code', '=', 'insurance_cober')])
        prod = self.env['product.product'].search([('product_tmpl_id', '=', cober_prod.id)])
        disc_prod = self.env['product.template'].search([('default_code', '=', 'discount')])
        disc_prod = self.env['product.product'].search([('product_tmpl_id', '=', disc_prod.id)])

        if self.cober > 0:
            for rec in self.invoice_line_ids:
                if rec.product_id.id == prod.id:
                    rec.unlink()
            self.invoice_line_ids = [(0, 0, {'name': prod.name, 'product_id': prod.id, 'account_id': prod.property_account_income_id ,'price_unit': 0 - self.cober})]

        if self.amount_total == 0.0:
            self.journal_id = self.env['account.journal'].search([('code', '=', 'noncf')]).id
        else:
            if self.discount:
                if self.discount:
                    for rec in self.invoice_line_ids:
                        if rec.product_id.id == disc_prod.id:
                            rec.unlink()
                self.invoice_line_ids = [(0, 0, {'name': disc_prod.name, 'product_id': disc_prod.id,
                                                 'account_id': disc_prod.property_account_income_id,
                                                 'price_unit': 0 - self.discount})]

        return super(AccountInvoice, self).action_invoice_open()




class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    praticant = fields.Many2one('medical.practitioner', u"Médico")

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

