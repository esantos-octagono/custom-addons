import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ir_sequence(models.Model):
    _inherit = 'ir.sequence'

    limite = fields.Integer('Limite secuencia')
    vencimiento_ncf = fields.Date('Vencimiento Secuencia')

    def _next_do(self):
        half = self.number_next_actual == int(self.limite/2)
        half_and_quarter = self.number_next_actual == int(self.limite - (self.limite/4))

        if (half or half_and_quarter) and (self.limite != 0):
            template = self.env['mail.template'].search([('name', '=', 'ncf_status')], limit=1)
            numbers_remaining = self.limite - self.number_next_actual
            if template:
                template['body_html'] = 'Solo quedan: {0} NCF disponibles para la secuencia: {1}, tener pendiente la solicitud de los mismos'.format(numbers_remaining,self.name)
                template.send_mail(self.id, True)
            else:
                _logger.warning('Favor revisar que exista una platilla con nombre: "ncf_status".')

        if self.limite != 0 and self.limite < self.number_next_actual:
            raise ValidationError('Ha llegado al limite de secuencia asignada a este documento')
        else:
            return super(ir_sequence, self)._next_do()