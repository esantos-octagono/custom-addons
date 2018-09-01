# -*- coding: utf-8 -*-

from odoo import models
from tools import is_ncf


class AccontInvoice(models.Model):
    _inherit = 'account.invoice'

    def is_ncf(self, value, type):
        return is_ncf(value, type)

