# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    ars = fields.Many2one(comodel_name='medical.insurance.company',string="ARS")
    afiliacion = fields.Many2one(comodel_name='medical.insurance.plan',string=u'Afiliación')
    tipo_seguro = fields.Char(related='afiliacion.insurance_affiliation')
    auth_num = fields.Char(string=u'# Autorización')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice.line'

    cober = fields.Monetary("Cobertura")