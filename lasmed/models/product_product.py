# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    product_price_line = fields.One2many('product.price.list.ars', 'product_tmpl_id', string="Lineas de Precios por ARS")


class ProductPriceListArs(models.Model):
    _name = 'product.price.list.ars'
    _description = 'Lista de Precios'
    _rec_name = 'description'

    _sql_constraints = [('price_list_ars_uniq', 'unique (product_tmpl_id,ars)',
                         'No esta permitido registrar un suplidor varias veces!')]

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Moneda",
        default = lambda self: self.env['res.currency'].search([('symbol','=','RD$')])[0]
    )
    price = fields.Monetary(string="Precio")
    description = fields.Char('Descripcion')
    product_tmpl_id = fields.Many2one('product.template')
    ars = fields.Many2one(comodel_name='medical.insurance.company', string="ARS", required=True)


