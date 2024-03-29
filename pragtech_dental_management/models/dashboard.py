from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import time


class MedicalDashboard(models.Model):
    _name = "medical.dashboard"

    @api.multi
    def get_patients(self):
        patient_ids = self.env['medical.patient'].search([])
        return {
            'name': _('Patient Details'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'medical.patient',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', patient_ids.ids)]
        }

    @api.multi
    def get_doctors(self):
        patient_ids = self.env['medical.physician'].search([])
        return {
            'name': _('Doctors'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'medical.physician',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', patient_ids.ids)]
        }


    @api.multi
    def get_appointments(self):
        appointment_ids = self.env['medical.appointment'].search([])
        tree_view_id = self.env.ref('pragtech_dental_management.medical_appointment_tree2').id
        form_view_id = self.env.ref('pragtech_dental_management.medical_appointment_view').id
        return {
            'name': _('Appointments'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'medical.appointment',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', appointment_ids.ids)],
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'context': {'search_default_today': 1}
        }

    @api.multi
    def get_registration(self):
        return {
            'name': _('Patient Registration'),
            'view_id': self.env.ref('pragtech_dental_management.view_registration_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'patient.registration',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def get_questionnaire(self):
        return {
            'name': _('Patient Details'),
            'view_id': self.env.ref('pragtech_dental_management.view_pos_details_wizard2').id,
            'type': 'ir.actions.act_window',
            'res_model': 'sign.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def get_feedback(self):
        return {
            'name': _('Feedback Form'),
            'type': 'ir.actions.act_window',
            'res_model': 'patient.feedback.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def get_complaint(self):
        return {
            'name': _('Complaint Form'),
            'type': 'ir.actions.act_window',
            'res_model': 'patient.complaint.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

