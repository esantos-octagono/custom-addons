import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

class account_journal(models.Model):
    _inherit = 'account.journal'

    fiscal = fields.Boolean(default=True,string="Fiscal")
