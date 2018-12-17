from odoo import api, fields, models, tools, _


class ClinicalFindings(models.Model):
    _name = "complaint.finding"

    patient_id = fields.Many2one('medical.patient', 'Patient Details', required=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment ID', required=True)
    finding = fields.Text('Clinical Finding')
    complaint = fields.Text('Chief complaint')

    @api.model
    def create(self, values):
        line = super(ClinicalFindings, self).create(values)
        msg = "<b> Created New Complaints and Findings:</b><ul>"
        if values.get('complaint'):
            msg += "<li>" + _("Complaint") + ": %s<br/>" % (line.complaint)
        if values.get('finding'):
            msg += "<li>" + _("Findings") + ": %s  <br/>" % (line.finding)
        msg += "</ul>"
        line.appt_id.message_post(body=msg)
        return line

    @api.multi
    def write(self, values):
        appoints = self.mapped('appt_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appt_id == apps)
            msg = "<b> Updated Complaints and Findings :</b><ul>"
            for line in order_lines:
                if values.get('complaint'):
                    msg += "<li>" + _("Complaint") + ": %s -> %s <br/>" % (line.complaint, values['complaint'],)
                if values.get('finding'):
                    msg += "<li>" + _("Findings") + ": %s -> %s <br/>" % (line.finding, values['finding'],)
            msg += "</ul>"
            apps.message_post(body=msg)
        result = super(ClinicalFindings, self).write(values)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            msg = "<b> Deleted Complaints and Findings with Values:</b><ul>"
            if rec.complaint:
                msg += "<li>" + _("Complaint") + ": %s <br/>" % (rec.complaint,)
            if rec.finding:
                msg += "<li>" + _("Findings") + ": %s  <br/>" % (rec.finding,)
            msg += "</ul>"
            rec.appt_id.message_post(body=msg)
            line = super(ClinicalFindings, rec).unlink()
        return line