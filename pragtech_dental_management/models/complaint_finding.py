from odoo import api, fields, models, tools, _


class ClinicalFindings(models.Model):
    _name = "complaint.finding"

    patient_id = fields.Many2one('medical.patient', 'Patient Details', required=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment ID', required=True)
    finding = fields.Text('Clinical Finding')
    complaint = fields.Text('Chief complaint')
