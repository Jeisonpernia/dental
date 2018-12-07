from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import time
from datetime import date
import base64


class TreatmentInvoice(models.Model):
    _name = "treatment.invoice"

    appointment_id = fields.Many2one("medical.appointment", "Appointment", required=True)
    treatment_id = fields.Many2one("medical.teeth.treatment", "Treatment")
    description = fields.Many2one('product.product', 'Treatment', required=True, domain=[('is_treatment', '=', True)])
    note = fields.Char("Description")
    amount = fields.Float("Amount", required=True)

    @api.onchange('treatment_id')
    def onchange_treatment_id(self):
        if self.treatment_id:
            self.description = self.treatment_id.description

    @api.onchange('description')
    def onchange_description(self):
        if self.description:
            self.amount = self.description.lst_price
