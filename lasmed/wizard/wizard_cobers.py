# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class CobersClose(models.TransientModel):
    _name = "cobers.close"

    @api.multi
    def action_settle(self):
        self.ensure_one()
        ars = self.env['medical.insurance.company'].search([('partner_id', '=', self.partner_id.id)])
        invoice_ids = self.env['account.invoice'].search([('settled', '=', False),('ars', '=', ars.id)])
        invoice_line_ids = []
        cober_prod = self.env['product.template'].search([('default_code', '=', 'insurance_cober')])
        prod = self.env['product.product'].search([('product_tmpl_id', '=', cober_prod.id)])
        for invoice in invoice_ids:
            invoice.settled = True
            invoice_line_ids.append((0, 0, {
                'product_id': prod.id,
                'name': prod.name,
                'price_unit': invoice.cober,
                'account_id': prod.property_account_income_id.id
            }))

        account_invoice_obj = self.env['account.invoice']
        shop_ncf_config = self.env['shop.ncf.config'].search([])
        vals = {
            'partner_id': self.partner_id.id,
            'type':'out_invoice',
            'sale_fiscal_type': 'final',
            'journal_id': self.journal.id,
            'shop_ncf_config': shop_ncf_config.id,
            'invoice_line_ids': invoice_line_ids,
        }
        invoice_id = account_invoice_obj.create(vals)

        if invoice_id:
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            action['domain'] = [['id', '=', invoice_id.id]]
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoice_id.id
            return action
        else:
            return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def settle_invoices(self):
        print("TESTINNNNNNaasdajsdljalksdjladlkajslkdjalsjdlasjdlkajsldjalskjdlaksjdlkajsdjalskd")
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        print active_ids
        ars_ids = self.env['medical.insurance.company'].search([])
        invoices = []
        cober_prod = self.env['product.template'].search([('default_code', '=', 'insurance_cober')])
        prod = self.env['product.product'].search([('product_tmpl_id', '=', cober_prod.id)])
        account_invoice_obj = self.env['account.invoice']
        shop_ncf_config = self.env['shop.ncf.config'].search([])
        print(ars_ids)
        for ars in ars_ids:
            invoice_ids = self.env['account.invoice'].browse(active_ids)
            invoice_ids = invoice_ids.filtered(lambda r: (r.ars.id == ars.id) and (not r.settled) and (not r.is_settle))
            invoice_line_ids = []
            cober = 0.0
            for invoice in invoice_ids:
                invoice_cober = invoice.invoice_line_ids.filtered(lambda l: (l.product_id.default_code == 'insurance_cober'))
                cober+=abs(invoice_cober.price_unit)
                invoice.settled = True

            invoice_line_ids.append((0, 0, {
                'product_id': prod.id,
                'name': prod.name,
                'price_unit': cober,
                'account_id': prod.property_account_income_id.id
            }))
            vals = {
                'partner_id': ars.partner_id.id,
                'type': 'out_invoice',
                'sale_fiscal_type': ars.partner_id.sale_fiscal_type,
                # 'shop_ncf_config': shop_ncf_config.id,
                'invoice_line_ids': invoice_line_ids,
                'is_settle': True,
            }
            if (cober > 0 ):
                invoice_id = account_invoice_obj.create(vals)
            else:
                invoice_id = None

            if invoice_id:
                invoices.append(invoice_id.id)
        if invoices:
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            action['domain'] = [['id', 'in', invoices]]
            action['views'] = [(self.env.ref('account.invoice_tree').id, 'tree'),(self.env.ref('account.invoice_form').id, 'form')]
            return action



