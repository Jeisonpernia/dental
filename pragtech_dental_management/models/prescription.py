from odoo import api, fields, models, tools, _


class PrescriptionLine(models.Model):
    _name = "prescription.line"

    prescription_date = fields.Datetime('Prescription Date', default=fields.Datetime.now)
    patient_id = fields.Many2one('medical.patient', 'Patient Details', required=True)
    appt_id = fields.Many2one('medical.appointment', 'Appointment', required=True)
    doctor = fields.Many2one('medical.physician', 'Doctor', required=True)
    medicine_id = fields.Many2one('medical.medicine.prag', 'Medicine', required=True, ondelete="cascade")
    dose = fields.Float('Dose', help="Amount of medication (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('medical.dose.unit', 'Dose Unit', help="Unit of measure for the medication to be taken")
    form = fields.Many2one('medical.drug.form', 'Form', help="Drug form, such as tablet or gel")
    qty = fields.Integer('x', default=1, help="Quantity of units (eg, 2 capsules) of the medicament")
    common_dosage = fields.Many2one('medical.medication.dosage', 'Frequency',
                                    help="Common / standard dosage frequency for this medicament")
    duration = fields.Integer('Duration',
                              help="Time in between doses the patient must wait (ie, for 1 pill each 8 hours, put here 8 and select 'hours' in the unit field")
    duration_period = fields.Selection([
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('wr', 'when required'),
    ], 'Duration Unit', default='days', )
    note = fields.Char('Description')


class PrescriptionReport(models.AbstractModel):
    _name = 'report.pragtech_dental_management.prescription_report_pdff'

    @api.model
    def get_sale_details(self, ids=False):
        """ Serialise the appt of the day information

        params: date_start, date_stop string representing the datetime of order
        """

        appt = self.env['medical.appointment'].search([('id', '=', ids)])
        record = {}
        patient = "[" + appt.patient.patient_id + "] : " + appt.patient_name
        record['appt'] = appt.name
        record['patient'] = patient
        # record['patient'] = appt.patient_name or ''
        record['doctor'] = appt.doctor.name.name
        record['date'] = appt.appointment_sdate[:10]
        prescriptions = []
        for pres in appt.prescription_ids:
            frequency = ""
            if pres.common_dosage:
                frequency = pres.common_dosage.name
            duration = ""
            if pres.duration:
                duration = str(pres.duration)
            if pres.duration_period:
                duration = duration + " " + str(pres.duration_period)
            pres_data = {
                'medicine_id': pres.medicine_id.name,
                'common_dosage': frequency,
                'duration': duration,
                'note': pres.note or "",
            }
            prescriptions.append(pres_data)
        record['pres_lines'] = prescriptions
        return record

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_sale_details(data['ids'][0]))
        return data
