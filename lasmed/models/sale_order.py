# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount = fields.Monetary("Descuento")

    @api.onchange('discount', 'order_line')
    def _onchange_amount_total(self):
        amount = self.amount_untaxed + self.amount_tax
        if self.discount < 0.0:
            raise ValidationError("El descuento debe ser positivo")
            self.discount = False
        elif self.discount > self.amount_total:
            raise ValidationError("El descuento debe ser menor o igual al monto total")
            self.discount = False
        else:
            print self.discount
            self.amount_total = amount - self.discount

    def action_confirm(self):
        disc_prod = self.env['product.template'].search([('default_code', '=', 'discount')])
        disc_prod = self.env['product.product'].search([('product_tmpl_id', '=', disc_prod.id)])

        if self.amount_total == 0.0:
            self.journal_id = self.env['account.journal'].search([('code', '=', 'noncf')]).id
        else:
            if self.discount:
                for rec in self.order_line:
                    if rec.product_id.id == disc_prod.id:
                        rec.unlink()

                self.order_line = [(0, 0, {'name': disc_prod.name, 'product_id': disc_prod.id,
                                                 'account_id': disc_prod.property_account_income_id,
                                                 'price_unit': 0 - self.discount})]

        return super(SaleOrder, self).action_confirm()

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'discount': self.discount,
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals