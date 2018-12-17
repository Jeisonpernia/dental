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

    @api.model
    def create(self, values):
        line = super(TreatmentInvoice, self).create(values)
        msg = "<b> Created New Payment Lines:</b><ul>"
        if values.get('description'):
            msg += "<li>" + _("Treatment") + ": %s<br/>" % (line.description.name)
        if values.get('note'):
            msg += "<li>" + _("Description") + ": %s  <br/>" % (line.note)
        if values.get('amount'):
            msg += "<li>" + _("Amount") + ": %s  <br/>" % (line.amount)
        msg += "</ul>"
        line.appointment_id.message_post(body=msg)
        return line

    @api.multi
    def write(self, values):
        appoints = self.mapped('appointment_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appointment_id == apps)
            msg = "<b> Updated Payment Lines :</b><ul>"
            for line in order_lines:
                if values.get('description'):
                    msg += "<li>" + _("Treatment") + ": %s -> %s <br/>" % (
                    line.description.name, self.env['product.product'].browse(values['description']).name,)
                if values.get('note'):
                    msg += "<li>" + _("Description") + ": %s -> %s <br/>" % (line.note, values['note'],)
                if values.get('amount'):
                    msg += "<li>" + _("Amount") + ": %s -> %s <br/>" % (line.amount, values['amount'],)
            msg += "</ul>"
            apps.message_post(body=msg)
        result = super(TreatmentInvoice, self).write(values)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            msg = "<b> Deleted Payment Lines with Values:</b><ul>"
            if rec.description:
                msg += "<li>" + _("Treatment") + ": %s <br/>" % (rec.description.name,)
            if rec.note:
                msg += "<li>" + _("Description") + ": %s  <br/>" % (rec.note,)
            if rec.amount:
                msg += "<li>" + _("Amount") + ": %s  <br/>" % (rec.amount,)
            msg += "</ul>"
            rec.appointment_id.message_post(body=msg)
            line = super(TreatmentInvoice, rec).unlink()
        return line
