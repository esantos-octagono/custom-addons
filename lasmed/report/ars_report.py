# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class ArsReport(models.Model):
    _name = "ars.report"
    _description = "Reporte de Ars"
    _auto = False
    _rec_name = 'date'

    date = fields.Date('Fecha')
    afil = fields.Char(u'Afiliación')
    partner_id = fields.Many2one('res.partner','Cliente')
    auth = fields.Char(u'NO. Autorización')
    ars = fields.Many2one('medical.insurance.company')
    currency_id = fields.Many2one('res.currency','Moneda')
    monto = fields.Monetary('Monto')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW {} as (
        SELECT
            ai.date,
            ai.id,  
            ai.ars,
            ai.afiliacion as  afil,
            ai.partner_id,
            ai.currency_id,
            ai.auth_num as auth,
            ai.cober as monto
        from account_invoice ai
        WHERE ai.is_settle = FALSE
        )""".format(self._table))





