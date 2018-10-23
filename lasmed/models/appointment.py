# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class Appoinment(models.Model):
    _name = "appointment"
    _rec_name = "description"

    description = fields.Char(name="Descripción")
    patient_id = fields.Many2one(name="Paciente", comodel_name="medical.patient")
    weight = fields.Float(name="Peso")
    date = fields.Date("Fecha")
    uom_id = fields.Many2one(name="Unidad de Medida", comodel_name="product.uom")
    symptoms = fields.Text(name="Síntomas")
    image = fields.Binary(name="Imagen")
