# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    appointment_ids = fields.One2many(comodel_name="appointment",inverse_name="patient_id",string="Registros Medicos")