# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import models,fields ,exceptions, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    vencimiento_ncf = fields.Date('Vencimiento de NCF')

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice,self).invoice_validate()
        if not self.vencimiento_ncf:
            self.vencimiento_ncf = self.journal_id.sequence_id.vencimiento_ncf
        else:
            pass

        return res
