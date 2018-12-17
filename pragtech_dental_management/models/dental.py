# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models, _
# from mock import DEFAULT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import hashlib
import time
from odoo.exceptions import Warning
import json
from ast import literal_eval
import base64


class ClaimManagement(models.Model):
    _name = "dental.insurance.claim.management"

    claim_date = fields.Date(string='Claim Date')
    name = fields.Many2one('res.partner', string='Patient', domain="[('is_patient', '=', True)]")
    insurance_company = fields.Many2one('res.partner', string='Insurance Company',
                                        domain="[('is_insurance_company', '=', True)]")
    insurance_policy_card = fields.Char(string='Insurance Policy Card')
    treatment_done = fields.Boolean(string='Treatment Done')


class InsurancePlan(models.Model):
    _name = "medical.insurance.plan"

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for insurance in self:
            name = insurance.code + ' ' + insurance.name.name
            result.append((insurance.id, name))
        return result

    is_default = fields.Boolean(string='Default Plan',
                                help='Check if this is the default plan when assigning this insurance company to a patient')
    name = fields.Many2one('product.product', string='Plan', required=True,
                           domain="[('type', '=', 'service'), ('is_insurance_plan', '=', True)]",
                           help='Insurance company plan')
    company_id = fields.Many2one('res.partner', string='Insurance Company', required=True,
                                 domain="[('is_insurance_company', '=', '1')]")
    notes = fields.Text('Extra info')
    code = fields.Char(size=64, required=True, index=True)


class MedicalInsurance(models.Model):
    _name = "medical.insurance"
    _rec_name = 'company_id'
    #     @api.multi
    #     @api.depends('number', 'company_id')
    #     def name_get(self):
    #         result = []
    #         for insurance in self:
    #             name = insurance.company_id.name +  ':' + insurance.number
    #             result.append((insurance.id, name))
    #         return result

    name = fields.Many2one('res.partner', 'Owner', required=True)
    number = fields.Char('Number', size=64, required=True)
    company_id = fields.Many2one('res.partner', 'Insurance Company', domain="[('is_insurance_company', '=', '1')]",
                                 required=True)
    member_since = fields.Date('Member since')
    member_exp = fields.Date('Expiration date')
    category = fields.Char('Category', size=64, help="Insurance company plan / category")
    type = fields.Selection([('state', 'State'), ('labour_union', 'Labour Union / Syndical'), ('private', 'Private'), ],
                            'Insurance Type')
    notes = fields.Text('Extra Info')
    plan_id = fields.Many2one('medical.insurance.plan', 'Plan', help='Insurance company plan')


class Partner(models.Model):
    _inherit = "res.partner"

    date = fields.Date('Partner since', help="Date of activation of the partner or patient")
    alias = fields.Char('alias', size=64)
    ref = fields.Char('ID Number')
    is_person = fields.Boolean('Person', help="Check if the partner is a person.")
    is_patient = fields.Boolean('Patient', help="Check if the partner is a patient")
    is_doctor = fields.Boolean('Doctor', help="Check if the partner is a doctor")
    is_institution = fields.Boolean('Institution', help="Check if the partner is a Medical Center")
    is_insurance_company = fields.Boolean('Insurance Company', help="Check if the partner is a Insurance Company")
    is_pharmacy = fields.Boolean('Pharmacy', help="Check if the partner is a Pharmacy")
    middle_name = fields.Char('Middle Name', size=128, help="Middle Name")
    lastname = fields.Char('Last Name', size=128, help="Last Name")
    insurance_ids = fields.One2many('medical.insurance', 'name', "Insurance")
    treatment_ids = fields.Many2many('product.product', 'treatment_insurance_company_relation', 'treatment_id',
                                     'insurance_company_id', 'Treatment')

    amt_paid_by_patient = fields.Float('Co-payment(%)')
    amt_paid_by_insurance = fields.Float('Amount by Insurance(%)')
    discount_amt = fields.Float('Treatment Group Discount(%)')

    nationality_id = fields.Char('Qatar Nationality ID')
    registration_fee_amount = fields.Float('Registration fee')
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], 'State', default='draft')
    registration_inv_id = fields.Many2one('account.invoice', 'Registration Invoice')
    registration_invoice = fields.Boolean('Registration Invoice ?', _defult=0)

    _sql_constraints = [
        ('ref_uniq', 'unique (ref)', 'The partner or patient code must be unique')
    ]

    @api.onchange('amt_paid_by_patient', 'discount_amt')
    @api.depends('amt_paid_by_patient', 'amt_paid_by_insurance', 'discount_amt')
    def onchange_amt(self):
        if 100 - (self.amt_paid_by_patient + self.discount_amt) < 0:
            raise Warning('Please enter valid amount')
        self.amt_paid_by_insurance = 100 - (self.amt_paid_by_patient + self.discount_amt)

    @api.model
    def create(self, vals):
        if vals.get('is_insurance_company') == True and vals.get('amt_paid_by_insurance') + vals.get(
                'amt_paid_by_patient') + vals.get('discount_amt') != 100:
            raise Warning('Cumulative percentage should be 100')
        return super(Partner, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(Partner, self).write(vals)
        if self.is_insurance_company and self.amt_paid_by_insurance + self.amt_paid_by_patient + self.discount_amt != 100:
            raise Warning('Cumulative percentage should be 100')
        return res

    @api.multi
    @api.depends('name', 'lastname')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name or ''
            if partner.middle_name:
                name += ' ' + partner.middle_name
            if partner.lastname:
                name = partner.lastname + ', ' + name
            result.append((partner.id, name))
        return result

    @api.multi
    def get_user_name(self):
        return self.name


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    action_perform = fields.Selection([('action', 'Action'), ('missing', 'Missing'), ('composite', 'Composite')],
                                      'Action perform', default='action')
    is_medicament = fields.Boolean('Medicament', help="Check if the product is a medicament")
    is_insurance_plan = fields.Boolean('Insurance Plan', help='Check if the product is an insurance plan')
    is_treatment = fields.Boolean('Treatment', help="Check if the product is a Treatment")
    is_planned_visit = fields.Boolean('Planned Visit')
    duration = fields.Selection(
        [('three_months', 'Three Months'), ('six_months', 'Six Months'), ('one_year', 'One Year')], 'Duration')

    insurance_company_ids = fields.Many2many('res.partner', 'treatment_insurance_company_relation',
                                             'insurance_company_id', 'treatment_id', 'Insurance Company')

    @api.multi
    def get_treatment_charge(self):
        return self.lst_price


class MedicamentCategory(models.Model):
    _description = 'Medicament Categories'
    _name = "medicament.category"
    _order = 'parent_id,id'

    @api.multi
    @api.depends('name', 'parent_id')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name
            if partner.parent_id:
                name = partner.parent_id.name + ' / ' + name
            result.append((partner.id, name))
        return result

    @api.model
    def _name_get_fnc(self):
        res = self._name_get_fnc()
        return res

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create a recursive category.'))

    name = fields.Char('Category Name', required=True, size=128)
    parent_id = fields.Many2one('medicament.category', 'Parent Category', index=True)
    complete_name = fields.Char(compute='_name_get_fnc', string="Name")
    child_ids = fields.One2many('medicament.category', 'parent_id', 'Children Category')


class MedicalMedicament(models.Model):
    _description = 'Medicament'
    _name = "medical.medicament"

    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name.name
            result.append((partner.id, name))
        return result

    name = fields.Many2one('product.product', 'Name', required=True, domain=[('is_medicament', '=', "1")],
                           help="Commercial Name")
    category = fields.Many2one('medicament.category', 'Category')
    active_component = fields.Char('Active component', size=128, help="Active Component")
    therapeutic_action = fields.Char('Therapeutic effect', size=128, help="Therapeutic action")
    composition = fields.Text('Composition', help="Components")
    indications = fields.Text('Indication', help="Indications")
    dosage = fields.Text('Dosage Instructions', help="Dosage / Indications")
    overdosage = fields.Text('Overdosage', help="Overdosage")
    pregnancy_warning = fields.Boolean('Pregnancy Warning',
                                       help="Check when the drug can not be taken during pregnancy or lactancy")
    pregnancy = fields.Text('Pregnancy and Lactancy', help="Warnings for Pregnant Women")
    presentation = fields.Text('Presentation', help="Packaging")
    adverse_reaction = fields.Text('Adverse Reactions')
    storage = fields.Text('Storage Conditions')
    price = fields.Float(related='name.lst_price', string='Price')
    qty_available = fields.Float(related='name.qty_available', string='Quantity Available')
    notes = fields.Text('Extra Info')
    pregnancy_category = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('X', 'X'),
        ('N', 'N'),
    ], 'Pregnancy Category',
        help='** FDA Pregancy Categories ***\n'
             'CATEGORY A :Adequate and well-controlled human studies have failed'
             ' to demonstrate a risk to the fetus in the first trimester of'
             ' pregnancy (and there is no evidence of risk in later'
             ' trimesters).\n\n'
             'CATEGORY B : Animal reproduction studies have failed todemonstrate a'
             ' risk to the fetus and there are no adequate and well-controlled'
             ' studies in pregnant women OR Animal studies have shown an adverse'
             ' effect, but adequate and well-controlled studies in pregnant women'
             ' have failed to demonstrate a risk to the fetus in any'
             ' trimester.\n\n'
             'CATEGORY C : Animal reproduction studies have shown an adverse'
             ' effect on the fetus and there are no adequate and well-controlled'
             ' studies in humans, but potential benefits may warrant use of the'
             ' drug in pregnant women despite potential risks. \n\n '
             'CATEGORY D : There is positive evidence of human fetal  risk based'
             ' on adverse reaction data from investigational or marketing'
             ' experience or studies in humans, but potential benefits may warrant'
             ' use of the drug in pregnant women despite potential risks.\n\n'
             'CATEGORY X : Studies in animals or humans have demonstrated fetal'
             ' abnormalities and/or there is positive evidence of human fetal risk'
             ' based on adverse reaction data from investigational or marketing'
             ' experience, and the risks involved in use of the drug in pregnant'
             ' women clearly outweigh potential benefits.\n\n'
             'CATEGORY N : Not yet classified')


class MedicalSpeciality(models.Model):
    _name = "medical.speciality"

    name = fields.Char('Description', size=128, required=True, help="ie, Addiction Psychiatry")
    code = fields.Char('Code', size=128, help="ie, ADP")

    _sql_constraints = [
        ('code_uniq', 'unique (name)', 'The Specialty code must be unique')]


class MedicalPhysician(models.Model):
    _name = "medical.physician"
    _description = "Information about the doctor"

    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name.name
            result.append((partner.id, name))
        return result

    name = fields.Many2one('res.partner', 'Physician', required=True,
                           domain=[('is_doctor', '=', "1"), ('is_person', '=', "1")],
                           help="Physician's Name, from the partner list")
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', "1")],
                                  help="Institution where she/he works")
    code = fields.Char('ID', size=128, help="MD License ID")
    speciality = fields.Many2one('medical.speciality', 'Specialty', required=True, help="Specialty Code")
    license_code = fields.Char(string="Licence No", required=False, track_visibility='onchange')
    info = fields.Text('Extra info')
    user_id = fields.Many2one('res.users', related='name.user_id', string='Physician User', store=True)


class MedicalOccupation(models.Model):
    _name = "medical.occupation"
    _description = "Occupation / Job"

    name = fields.Char('Occupation', size=128, required=True)
    code = fields.Char('Code', size=64)

    _sql_constraints = [
        ('occupation_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def get_image(self, a):
        #         if 'image' in a.keys():
        if 'image' in list(a.keys()):
            return True
        else:
            return False

    @api.multi
    def get_type(self, record1):
        categ_type = record1['type']
        categ_ids = self.env['product.category'].search([('name', '=', categ_type)])
        if categ_ids['type'] == 'view':
            return False
        return True

    @api.multi
    def check_next_image(self, main_record, sub_record):
        if len(main_record['image']) > sub_record:
            return 1
        else:
            return 0

    @api.multi
    def image_url_new(self, record1):
        """Returns a local url that points to the image field of a given browse record."""
        lst = []
        size = None
        field = 'datas'
        record = self.env['ir.attachment'].browse(self.ids)
        cnt = 0
        for r in record:
            if r.store_fname:
                cnt = cnt + 1
                model = r._name
                sudo_record = r.sudo()
                id = '%s_%s' % (r.id, hashlib.sha1(
                    (sudo_record.write_date or sudo_record.create_date or '').encode('utf-8')).hexdigest()[0:7])
                if cnt == 1:
                    size = '' if size is None else '/%s' % size
                else:
                    size = '' if size is None else '%s' % size
                lst.append('/website/image/%s/%s/%s%s' % (model, id, field, size))
        return lst


# PATIENT GENERAL INFORMATION

class MedicalPatient(models.Model):
    _name = "medical.patient"
    _description = "Patient related information"

    @api.multi
    def is_warning_needed(self, treatment):
        if self.current_insurance:
            allowded_treatments = [line.id for line in self.current_insurance.company_id.treatment_ids]
            if not treatment in allowded_treatments:
                return True
        return False

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|', '|', '|', '|', '|', ('name', operator, name), ('patient_id', operator, name),
                                ('mobile', operator, name), ('other_mobile', operator, name),
                                ('lastname', operator, name), ('middle_name', operator, name)])
        if not recs:
            recs = self.search([('name', operator, name)])
        return recs.name_get()

    @api.multi
    @api.onchange('dob')
    def onchange_dob(self):
        c_date = datetime.today().strftime('%Y-%m-%d')
        if self.dob:
            if not (self.dob <= c_date):
                raise UserError(_('Birthdate cannot be After Current Date.'))
        return {}

    # Get the patient age in the following format : "YEARS MONTHS DAYS"
    # It will calculate the age of the patient while the patient is alive. When the patient dies, it will show the age at time of death.

    @api.multi
    def _patient_age(self):
        def compute_age_from_dates(patient_dob, patient_deceased, patient_dod):
            now = datetime.now()
            if (patient_dob):
                dob = datetime.strptime(patient_dob, '%Y-%m-%d')
                if patient_deceased:
                    dod = datetime.strptime(patient_dod, '%Y-%m-%d %H:%M:%S')
                    delta = relativedelta(dod, dob)
                    deceased = " (deceased)"
                else:
                    delta = relativedelta(now, dob)
                    deceased = ''
                years_months_days = str(delta.years) + "y " + str(delta.months) + "m " + str(
                    delta.days) + "d" + deceased
            else:
                years_months_days = "No DoB !"

            return years_months_days

        self.age = compute_age_from_dates(self.dob, self.deceased, self.dod)

    @api.multi
    def _medical_alert(self):
        for patient_data in self:
            medical_alert = ''
            patient_data.critical_info = medical_alert

    name_tag = fields.Selection([('Mr.', 'Mr.'),
                                 ('Mrs.', 'Mrs.'),
                                 ('Miss', 'Miss'),
                                 ('Ms.', 'Ms.'),
                                 ('Other', 'Other')], 'Name Tag')
    address = fields.Text("Address")
    emergency_name = fields.Char('Name')
    emergency_relation = fields.Char('Relation')
    emergency_phone = fields.Char('Phone')
    patient_name = fields.Char(_("Patient Name"))
    register_signature = fields.Binary(string='Signature')
    name = fields.Many2one('res.partner', 'Patient Partner', required=False, readonly=True,
                           domain=[('is_patient', '=', True), ('is_person', '=', True)], help="Patient Name")
    qid = fields.Char("QID")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female'), ], 'Gender')
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)
    invoice_ids = fields.Many2many("account.invoice", string='Invoices', compute="_get_invoiced", readonly=True,
                                   copy=False)
    payment_count = fields.Integer(string='# of Payments', compute='_get_payments', readonly=True)
    payment_ids = fields.Many2many("account.payment", string='Payments', compute="_get_payments", readonly=True,
                                   copy=False)
    operation_summary_ids = fields.One2many('operation.summary', 'patient_id', 'Operation Summary', readonly=True)
    finding_ids = fields.One2many("complaint.finding", 'patient_id', "Complaints and findings")
    prescriptions = fields.One2many("prescription.line", 'patient_id', "Prescriptions")
    feedbacks = fields.One2many("patient.feedback", 'patient_id', "Feedbacks")
    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language')
    register_date = fields.Date('Registration Date')
    amount_due = fields.Char('Outstanding Amount', compute='_get_invoiced')

    patient_id = fields.Char('Patient ID', size=64,
                             help="Patient Identifier provided by the Health Center. Is not the patient id from the partner form",
                             default=lambda self: _('New'))
    ssn = fields.Char('SSN', size=128, help="Patient Unique Identification Number")
    lastname = fields.Char(related='name.lastname', string='Lastname')
    middle_name = fields.Char(related='name.middle_name', string='Middle Name')
    identifier = fields.Char(string='SSN', related='name.ref', help="Social Security Number or National ID")
    current_insurance = fields.Many2one('medical.insurance', "Insurance", domain="[('name','=',name)]",
                                        help="Insurance information. You may choose from the different insurances belonging to the patient")
    sec_insurance = fields.Many2one('medical.insurance', "Insurance", domain="[('name','=',name)]",
                                    help="Insurance information. You may choose from the different insurances belonging to the patient")
    dob = fields.Date('Date of Birth')
    age = fields.Char(compute='_patient_age', string='Patient Age',
                      help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field")
    marital_status = fields.Selection(
        [('s', 'Single'), ('m', 'Married'), ('w', 'Widowed'), ('d', 'Divorced'), ('x', 'Separated'), ],
        'Marital Status')
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ], 'Blood Type')
    rh = fields.Selection([('+', '+'), ('-', '-'), ], 'Rh')
    user_id = fields.Many2one('res.users', related='name.user_id', string='Doctor',
                              help="Physician that logs in the local Medical system (HIS), on the health center. It doesn't necesarily has do be the same as the Primary Care doctor",
                              store=True)
    medications = fields.One2many('medical.patient.medication', 'name', 'Medications')
    diseases_ids = fields.One2many('medical.patient.disease', 'name', 'Diseases')
    critical_info = fields.Text(compute='_medical_alert', string='Medical Alert',
                                help="Write any important information on the patient's disease, surgeries, allergies, ...")
    medical_history = fields.Text('Medical History')
    critical_info_fun = fields.Text(compute='_medical_alert', string='Medical Alert',
                                    help="Write any important information on the patient's disease, surgeries, allergies, ...")
    medical_history_fun = fields.Text('Medical History')
    general_info = fields.Text('General Information', help="General information about the patient")
    deceased = fields.Boolean('Deceased', help="Mark if the patient has died")
    dod = fields.Datetime('Date of Death')
    apt_id = fields.Many2many('medical.appointment', 'pat_apt_rel', 'patient', 'apid', 'Appointments')
    attachment_ids = fields.One2many('ir.attachment', 'patient_id', 'attachments')
    photo = fields.Binary(related='name.image', string='Picture', store=True)
    report_date = fields.Date("Report Date:", default=fields.Datetime.now)
    occupation_id = fields.Many2one('medical.occupation', 'Occupation')
    primary_doctor_id = fields.Many2one('medical.physician', 'Primary Doctor', )
    referring_doctor_id = fields.Many2one('medical.physician', 'Referring  Doctor', )
    note = fields.Text('Notes', help="Notes and To-Do")
    mobile = fields.Char('Mobile', related='name.mobile')
    other_mobile = fields.Char('Other Mobile')
    teeth_treatment_ids = fields.One2many('medical.teeth.treatment', 'patient_id', 'Operations', readonly=True)
    nationality_id = fields.Many2one('patient.nationality', 'Nationality')
    patient_complaint_ids = fields.One2many('patient.complaint', 'patient_id')
    q1 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Is your health good?')
    q2 = fields.Boolean('Anemia')
    q3 = fields.Boolean('Arthritis, Rheumatism')
    q4 = fields.Boolean('Artificial Joints, Pins')
    q5 = fields.Boolean('Asthma')
    q6 = fields.Boolean('Back pain')
    q7 = fields.Boolean('Cortisone Treatment')
    q8 = fields.Boolean('Cough, Persistent')
    q9 = fields.Boolean('Diabetes')
    q10 = fields.Boolean('Epilepsy')
    q11 = fields.Boolean('Fainting')
    q12 = fields.Boolean('Glaucoma')
    q13 = fields.Boolean('Headaches or Migraine')
    q14 = fields.Boolean('Hemophilia')
    q15 = fields.Boolean('Heart Disease')
    q16 = fields.Boolean('Heart Valve problems')
    q17 = fields.Boolean('Heart Surgery')
    q18 = fields.Boolean('Hepatitis')
    q19 = fields.Boolean('High Blood Pressure')
    q20 = fields.Boolean('HIV')
    q21 = fields.Boolean('Jaw Pain')
    q22 = fields.Boolean('Kidney Disease')
    q23 = fields.Boolean('Pacemaker')
    q24 = fields.Boolean('Prolonged bleeding')
    q25 = fields.Boolean('Respiratory Disease')
    q26 = fields.Boolean('Kidney Problem')
    q27 = fields.Boolean('Liver Problem')
    q28 = fields.Boolean('Thyroid Problem')
    q29 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Serious illness or operations?')
    q30 = fields.Char('When')
    q31 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Other Medical Problems?')
    q32 = fields.Char('Please Specify')
    q33 = fields.Boolean('Latex')
    q34 = fields.Boolean('Local Anesthetic')
    q35 = fields.Boolean('Penicillin')
    q36 = fields.Boolean('Sulfa')
    q37 = fields.Boolean('Aspirin')
    q38 = fields.Boolean('Brufen')
    q39 = fields.Boolean('Iodine')
    q40 = fields.Boolean('NONE')
    q41 = fields.Char('Any other allergies')
    q42 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Do you smoke?')
    q43 = fields.Integer(' # of cigarette/day')
    q44 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you pregnant?')
    q45 = fields.Char('Month')
    q46 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you having discomfort at this time?')
    q47 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you ever had any serious trouble?')
    q48 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Are you taking any anticoagulants (blood thinner) ? ')
    q49 = fields.Date('Date of Last Dental Visit?')
    q50 = fields.Char('Brushing')
    q51 = fields.Char('Flossing')
    q52 = fields.Char('Mouthwash')
    q53 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you been treated for gum disease?')
    q54 = fields.Selection([('YES', 'YES'), ('NO', 'NO')], 'Have you had any dental radiographs?')
    q55 = fields.Char('When and where')
    q56 = fields.Char('What is the main reason for seeking dental care?')
    q57 = fields.Boolean('Bleeding or sore gums')
    q58 = fields.Boolean('Biting Cheeks/lips')
    q59 = fields.Boolean('Broken filling')
    q60 = fields.Boolean('Clenching/grinding')
    q61 = fields.Boolean('Clicking/Locked Jaw')
    q62 = fields.Boolean('Difficult to open/close')
    q63 = fields.Boolean('Frequent blisters (lips/mouth)')
    q64 = fields.Boolean('Food impaction')
    q65 = fields.Boolean('Food collection in between teeth')
    q66 = fields.Boolean('Root Canal Treatment')
    q67 = fields.Boolean('Loose teeth')
    q68 = fields.Boolean('Swelling or Lumps in mouth')
    q69 = fields.Boolean('Ortho Treatment (braces)')
    q70 = fields.Boolean('Sensitive to hot')
    q71 = fields.Boolean('Sensitive to cold')
    q72 = fields.Boolean('Sensitive to sweet')
    q73 = fields.Boolean('Sensitive to bite')
    q74 = fields.Boolean('Shifting in bite')
    q75 = fields.Boolean('Unpleasant taste/bad breath')
    q76 = fields.Selection([('YES', 'YES'), ('NO', 'NO')],
                           'Are you pleased with the general appearance of your teeth and smile?')
    q77 = fields.Char('if no why')

    updated_date = fields.Date('Updated Date')
    arebic = fields.Boolean('Arabic')
    registration_fee_amount = fields.Float('Registration fee')
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], 'State', default='draft')
    registration_inv_id = fields.Many2one('account.invoice', 'Registration Invoice')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Patient already exists'),
        ('patient_id_uniq', 'unique (patient_id)', 'The Patient ID already exists'), ]

    @api.onchange('patient_name')
    def onchange_patientname(self):
        for rec in self:
            if rec.patient_name and rec.name:
                rec.name.name = rec.patient_name
                rec.name.write({'name': rec.patient_name})

    @api.depends('name')
    def _get_payments(self):
        for patient in self:
            payment_ids = self.env['account.payment'].search([('partner_id', '=', patient.name.id),
                                                              ('partner_type', '=', 'customer')])
            patient.update({
                'payment_count': len(set(payment_ids.ids)),
                'payment_ids': payment_ids.ids
            })

    @api.multi
    @api.depends('patient_name', 'patient_id')
    def name_get(self):
        result = []
        for partner in self:
            name = ""
            if partner.patient_name:
                name = partner.patient_name
            if partner.patient_id:
                name = '[' + partner.patient_id + ']' + name
            if partner.mobile:
                name = name + " : " + partner.mobile
            result.append((partner.id, name))
        return result

    @api.multi
    def attach_registration(self):
        data = {'ids': self.ids}
        data, data_format = self.env.ref('pragtech_dental_management.report_registration').render([1], data=data)
        att_id = self.env['ir.attachment'].create({
            'name': 'Registration_' + self.updated_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_registration.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def action_view_payment(self):
        payments = self.mapped('payment_ids')
        action = self.env.ref('account.action_account_payments').read()[0]
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = payments.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends('name')
    def _get_invoiced(self):
        for patient in self:
            invoice_ids = self.env['account.invoice'].search([('partner_id', '=', patient.name.id),
                                                              ('type', '=', 'out_invoice')])
            amount_due = 0
            for inv in invoice_ids:
                amount_due += inv.residual_signed
            patient.update({
                'invoice_count': len(set(invoice_ids.ids)),
                'invoice_ids': invoice_ids.ids,
                'amount_due': "{:.2f}".format(amount_due)
            })

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['context'] = {'hide_for_service_bill': True, 'show_for_service_bill': True}
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def get_img(self):
        for rec in self:
            res = {}
            img_lst_ids = []
            imd = self.env['ir.model.data']
            action_view_id = imd.xmlid_to_res_id('action_result_image_view')
            for i in rec.attachment_ids:
                img_lst_ids.append(i.id)
            res['image'] = img_lst_ids

            return {
                'type': 'ir.actions.client',
                'name': 'Patient image',
                'tag': 'result_images',
                'params': {
                    'patient_id': rec.id or False,
                    'model': 'medical.patient',
                    'values': res
                },
            }

    @api.multi
    def create_registration_fee_invoice(self):
        inv_obj = self.env['account.invoice']

        ICPSudo = self.env['ir.config_parameter'].sudo()
        registration_invoice_product_id = literal_eval(
            ICPSudo.get_param('registration_invoice_product_id', default='False'))
        product_obj = self.env['product.product'].browse(registration_invoice_product_id)
        if not registration_invoice_product_id:
            raise Warning('You need to specify Product to be used for Registration Invoice.')
        account_id = None
        if product_obj.property_account_income_id:
            account_id = product_obj.property_account_income_id.id
        else:
            account_id = product_obj.categ_id.property_account_income_categ_id.id

        invoice = inv_obj.create({
            'name': 'REGISTRATION INVOICE',
            'origin': 'Registration' + ' ' + self.patient_id,
            'type': 'out_invoice',
            'reference': False,
            'account_id': self.name.property_account_receivable_id.id,
            'partner_id': self.name.id,
            'is_patient': True,
            'registration_invoice': True,
            #             'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Registration',
                'origin': 'Registration' + ' ' + self.patient_id,
                'account_id': account_id,  # self.name.property_account_receivable_id.id,
                'price_unit': product_obj.lst_price,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': product_obj.uom_id.id,
                'product_id': registration_invoice_product_id,
            })],
            'currency_id': self.name.company_id.currency_id.id,
            'comment': 'Registration Invoice of Patient ' + ' ' + self.name.name,
        })
        for line in self.env['account.invoice.line'].search([('invoice_id', '=', invoice.id)]):
            line._onchange_product_id()
        self.state = 'paid'
        self.registration_inv_id = invoice.id
        invoice.compute_taxes()
        return invoice

    @api.multi
    def view_registartion_invoice(self):
        view_id = self.env.ref('account.invoice_form').id,
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.registration_inv_id.id,
            'views': [(view_id, 'form')],
        }

    @api.multi
    def get_patient_history(self, appt_id):
        return_list = [];
        extra_history = 0;
        total_operation = [];
        return_list.append([])
        if appt_id:
            appt_id_brw = self.env['medical.appointment'].browse(appt_id)
            total_operation = appt_id_brw.operations
            extra_history = len(total_operation)
            for each_patient_operation in self.teeth_treatment_ids:
                if each_patient_operation.description.action_perform == "missing" and each_patient_operation.appt_id.id < appt_id:
                    total_operation += each_patient_operation
        else:
            total_operation = self.teeth_treatment_ids
            extra_history = len(total_operation)
        history_count = 0
        for each_operation in total_operation:
            history_count += 1
            current_tooth_id = each_operation.teeth_id.internal_id
            if each_operation.description:
                desc_brw = self.env['product.product'].browse(each_operation.description.id)
                if desc_brw.action_perform == 'missing':
                    return_list[0].append(current_tooth_id)
                self._cr.execute('select teeth from teeth_code_medical_teeth_treatment_rel where operation = %s' % (
                each_operation.id,))
                multiple_teeth = self._cr.fetchall()
                multiple_teeth_list = [multiple_teeth_each[0] for multiple_teeth_each in multiple_teeth]
                total_multiple_teeth_list = []
                for each_multiple_teeth_list in multiple_teeth_list:
                    each_multiple_teeth_list_brw = self.env['teeth.code'].browse(each_multiple_teeth_list)
                    total_multiple_teeth_list.append(each_multiple_teeth_list_brw.internal_id)
                    multiple_teeth_list = total_multiple_teeth_list
                other_history = 0
                if history_count > extra_history:
                    other_history = 1

                uid = self.env['res.users'].search([('partner_id', '=', each_operation.dentist.name.id)], limit=1).id
                return_list.append({
                    'dignosis': {
                        'id': each_operation.diagnosis_id.id,
                        'code': each_operation.diagnosis_id.code
                    },
                    'dignosis_description': each_operation.diagnosis_description,
                    'other_history': other_history,
                    'created_date': each_operation.create_date,
                    'status': each_operation.state,
                    'multiple_teeth': multiple_teeth_list,
                    'tooth_id': current_tooth_id,
                    'surface': each_operation.detail_description,
                    'dentist': [uid, each_operation.dentist.name.name],
                    'desc': {
                        'name': each_operation.description.name,
                        'id': each_operation.description.id,
                        'action': each_operation.description.action_perform},
                    'amount': each_operation.amount
                })

        return return_list

    def is_valid_user(self, uid):
        related_partner_of_curr_user = self.env['res.users'].browse(uid).partner_id.id
        physician = self.env['medical.physician'].search([('name', '=', related_partner_of_curr_user)], limit=1).id
        if physician:
            return True
        else:
            return False

    @api.multi
    def create_lines(self, treatment_lines, patient_id, appt_id):
        # create objects
        medical_teeth_treatment_obj = self.env['medical.teeth.treatment']
        medical_physician_obj = self.env['medical.physician']
        product_obj = self.env['product.product']
        teeth_code_obj = self.env['teeth.code']
        dignosis_code = dignosis_obj = self.env['diagnosis']
        # delete previous records
        patient = int(patient_id)
        patient_brw = self.env['medical.patient'].browse(patient)
        partner_brw = patient_brw.name
        if appt_id:
            appt = int(appt_id)
            appt_brw = self.env['medical.appointment'].browse(appt)
            if appt_brw.state != 'done':
                pay_lines = self.env['treatment.invoice'].search([('appt_id', '=', appt)])
                pay_lines.unlink()
            prev_appt_operations = medical_teeth_treatment_obj.search([('appt_id', '=', appt)])
            prev_appt_operations.unlink()
        else:
            prev_pat_operations = medical_teeth_treatment_obj.search([('patient_id', '=', int(patient_id))])
            prev_pat_operations.unlink()
        prev_pat_missing_operations = medical_teeth_treatment_obj.search(
            [('patient_id', '=', int(patient_id)), ('state', '=', 'planned')])
        for each_prev_pat_missing_operations in prev_pat_missing_operations:
            if each_prev_pat_missing_operations.description.action_perform == 'missing':
                each_prev_pat_missing_operations.unlink()
        if treatment_lines:
            current_physician = 0;
            for each in treatment_lines:
                if 'teeth_id' not in list(each.keys()):
                    each['teeth_id'] = 'all'
                if each.get('prev_record') == 'false':
                    all_treatment = each.get('values')
                    if all_treatment:
                        for each_trt in all_treatment:

                            vals = {}
                            category_id = int(each_trt.get('categ_id'))
                            vals['description'] = category_id
                            if 1:
                                if (str(each.get('teeth_id')) != 'all'):
                                    actual_teeth_id = teeth_code_obj.search(
                                        [('internal_id', '=', int(each.get('teeth_id')))])
                                    vals['teeth_id'] = actual_teeth_id[0].id
                                vals['patient_id'] = patient
                                desc = ''
                                for each_val in each_trt['values']:
                                    if each_val:
                                        desc += each_val + ' '
                                vals['detail_description'] = desc.rstrip()
                                dentist = each.get('dentist')
                                if not each.get('dentist') == 'false':
                                    if type(each.get('dentist')) == str:
                                        dentist = int(each.get('dentist'))
                                    res_partner_id = self.env['res.partner'].search([('user_id', '=', dentist)],
                                                                                    limit=1)
                                    if res_partner_id:
                                        physician = medical_physician_obj.search([('name', '=', res_partner_id.id)],
                                                                                 limit=1)
                                        if physician:
                                            dentist = physician.id

                                            related_partner_of_curr_user = self.env['res.users'].browse(
                                                int(each.get('dentist'))).partner_id.id
                                            physician = medical_physician_obj.search(
                                                [('name', '=', related_partner_of_curr_user)], limit=1).id
                                            vals['dentist'] = physician
                                            current_physician = 1

                                status = None
                                if each.get('status_name'):
                                    status_name = each.get('status_name')
                                    status = (str(each.get('status_name')))
                                    if status_name == 'in_progress':
                                        status = 'in_progress'
                                    elif status_name == 'Planned' or status_name == 'false':
                                        status = 'planned'

                                else:
                                    status = 'planned'
                                vals['state'] = status

                                p_brw = product_obj.browse(vals['description'])

                                if each.get('dignosis_code') and not each.get('dignosis_code') == 'noclass':
                                    vals['diagnosis_id'] = each.get('dignosis_code')
                                elif 'dignosis_code' in each.keys() and not each['dignosis_code']:
                                    vals['diagnosis_id'] = None

                                if each.get('dignosis_description'):
                                    vals['diagnosis_description'] = each.get('dignosis_description')

                                # update the amount value from chart to db
                                if not each.get('amount'):
                                    vals['amount'] = p_brw.lst_price
                                else:
                                    vals['amount'] = float(each['amount'])
                                if appt_id:
                                    vals['appt_id'] = appt_id

                                treatment_id = medical_teeth_treatment_obj.create(vals)
                                if each.get('multiple_teeth'):
                                    full_mouth = each.get('multiple_teeth');
                                    full_mouth = full_mouth.split('_')
                                    operate_on_tooth = []
                                    for each_teeth_from_full_mouth in full_mouth:
                                        actual_teeth_id = teeth_code_obj.search(
                                            [('internal_id', '=', int(each_teeth_from_full_mouth))])
                                        operate_on_tooth.append(actual_teeth_id.id)
                                    treatment_id.write({'teeth_code_rel': [(6, 0, operate_on_tooth)]})
                                    #                                         cr.execute('insert into teeth_code_medical_teeth_treatment_rel(operation,teeth) values(%s,%s)' % (treatment_id,each_teeth_from_full_mouth))
                                    #             invoice_vals = {}
                                    #             invoice_line_vals = []
                                    #             # Creating invoice lines
                                    #             # get account id for products
                                    #             jr_search = self.env['account.journal'].search([('type', '=', 'sale')])
                                    #             jr_brw = jr_search
                                    #             for each in treatment_lines:
                                    #                 if each.get('prev_record') == 'false':
                                    #                     if str(each.get('status_name')).lower() == 'completed' or str(each.get('status_name')).lower() == 'in_progress':
                                    #                         for each_val in each['values']:
                                    #                             each_line = [0, False]
                                    #                             product_dict = {}
                                    #                             product_dict['product_id'] = int(each_val['categ_id'])
                                    #                             p_brw = product_obj.browse(int(each_val['categ_id']))
                                    #
                                    #
                                    #                             if patient_brw.current_insurance.company_id.id in [comp.id for comp in p_brw.insurance_company_ids]:
                                    #                                 product_dict['amt_paid_by_patient'] = patient_brw.current_insurance.company_id.amt_paid_by_patient
                                    #                                 product_dict['discount_amt'] = patient_brw.current_insurance.company_id.discount_amt
                                    #
                                    #
                                    #
                                    #                             if p_brw.action_perform != 'missing':
                                    #                                 desc = ''
                                    #                                 features = ''
                                    #                                 for each_v in each_val['values']:
                                    #                                     if each_v:
                                    #                                         desc = str(each_v)
                                    #                                         features += desc + ' '
                                    #                                 if (each['teeth_id'] != 'all'):
                                    #                                     actual_teeth_id = teeth_code_obj.search([('internal_id','=',int(each.get('teeth_id')))])
                                    #                                     invoice_name = actual_teeth_id.name_get()
                                    #                                     product_dict['name'] = str(invoice_name[0][1]) + ' ' + features
                                    #                                 else:
                                    #                                     product_dict['name'] = 'Full Mouth'
                                    #                                 product_dict['quantity'] = 1
                                    #                                 product_dict['price_unit'] = p_brw.lst_price
                                    #                                 acc_obj=self.env['account.account'].search([('name','=','Local Sales'),('user_type_id','=','Income')],limit=1)
                                    #                                 for account_id in jr_brw:
                                    #                                     product_dict['account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id
                                    #                                 each_line.append(product_dict)
                                    #                                 invoice_line_vals.append(each_line)
                                    #                 # Creating invoice dictionary
                                    #                             invoice_vals['account_id'] = partner_brw.property_account_receivable_id.id
                                    #                             invoice_vals['partner_id'] = partner_brw.id
                                    #                             if current_physician:
                                    #                                 invoice_vals['dentist'] = physician
                                    #                             invoice_vals['insurance_company'] = patient_brw.current_insurance.company_id.id
                                    #
                                    #                             invoice_vals['invoice_line_ids'] = invoice_line_vals
                                    # #                             invoice_vals['invoice_line_ids'] = invoice_line_vals
                                    #
                                    #         # creating account invoice
                                    #             if invoice_vals:
                                    #                 self.env['account.invoice'].create(invoice_vals)
        else:
            return False

    @api.multi
    def get_back_address(self, active_patient):
        active_patient = str(active_patient)
        action_rec = self.env['ir.actions.act_window'].search([('res_model', '=', 'medical.patient')])
        action_id = str(action_rec.id)
        address = '/web#id=' + active_patient + '&view_type=form&model=medical.patient&action=' + action_id
        return address

    @api.multi
    def get_date(self, date1, lang):
        new_date = ''
        if date1:
            search_id = self.env['res.lang'].search([('code', '=', lang)])
            new_date = datetime.strftime(datetime.strptime(date1, '%Y-%m-%d %H:%M:%S').date(), search_id.date_format)
        return new_date

    @api.multi
    def write(self, vals):
        if 'critical_info' in list(vals.keys()):
            #         if 'critical_info' in vals.keys():
            vals['critical_info_fun'] = vals['critical_info']
        # elif 'critical_info_fun' in vals.keys():
        elif 'critical_info_fun' in list(vals.keys()):
            vals['critical_info'] = vals['critical_info_fun']
        # if 'medical_history' in vals.keys():
        if 'medical_history' in list(vals.keys()):
            vals['medical_history_fun'] = vals['medical_history']
        # elif 'medical_history_fun' in vals.keys():
        elif 'medical_history_fun' in list(vals.keys()):
            vals['medical_history'] = vals['medical_history_fun']
        return super(MedicalPatient, self).write(vals)

    @api.model
    def create(self, vals):
        if 'name' not in list(vals.keys()):
            if 'patient_name' in list(vals.keys()):
                partner_id = self.env['res.partner'].create({'name': vals['patient_name'],
                                                             'is_patient': True,
                                                             'is_person': True,
                                                             })
                vals['name'] = partner_id.id
        if vals.get('critical_info'):
            vals['critical_info_fun'] = vals['critical_info']
        elif vals.get('critical_info_fun'):
            vals['critical_info'] = vals['critical_info_fun']
        if vals.get('medical_history'):
            vals['medical_history_fun'] = vals['medical_history']
        elif vals.get('medical_history_fun'):
            vals['medical_history'] = vals['medical_history_fun']
        c_date = datetime.today().strftime('%Y-%m-%d')
        result = False
        if vals.get('patient_id', 'New') == 'New':
            seq_val = self.env['ir.sequence'].next_by_code('medical.patient') or 'New'
            seq_without_prefix = seq_val[3:]
            company_obj = self.env.user.company_id
            if company_obj.patient_prefix:
                vals['patient_id'] = company_obj.patient_prefix + seq_without_prefix
            else:
                vals['patient_id'] = seq_val
        if 'dob' in list(vals.keys()) and vals['dob']:
            if (vals['dob'] > c_date):
                raise ValidationError(_('Birthdate cannot be After Current Date.'))
        result = super(MedicalPatient, self).create(vals)
        return result

    #     @api.multi
    #     def get_img(self):
    #         for rec in self:
    #             res = {}
    #             img_lst_ids = []
    #             imd = self.env['ir.model.data']
    #             action_view_id = imd.xmlid_to_res_id('action_result_image_view')
    #             for i in rec.attachment_ids:
    #                 img_lst_ids.append(i.id)
    #             res['image'] = img_lst_ids
    #
    #             return {
    #             'type': 'ir.actions.client',
    #             'name': 'Patient image',
    #             'tag': 'result_images',
    #             'params': {
    #                'patient_id':  rec.id  or False,
    #                'model':  'medical.patient',
    #                'values': res
    #             },
    #         }

    @api.multi
    def open_chart(self):
        for rec in self:
            appt_id = ''
            context = dict(self._context or {})
            #             if 'appointment_id_new' in context.keys():
            if 'appointment_id_new' in list(context.keys()):
                appt_id = context['appointment_id_new']
            if context is None:
                context = {}
            imd = self.env['ir.model.data']
            action_view_id = imd.xmlid_to_res_id('action_open_dental_chart')
            teeth_obj = self.env['chart.selection'].search([])
            teeth = teeth_obj[-1]
            return {
                'type': 'ir.actions.client',
                'name': 'Dental Chart',
                'tag': 'dental_chart',
                'params': {
                    'patient_id': rec.id or False,
                    'appt_id': appt_id,
                    'model': 'medical.patient',
                    'type': teeth.type
                },
            }

    digital_signature = fields.Binary(string='Signature')

    @api.multi
    def print_questionnaire(self):
        data = {'ids': self.ids}
        data, data_format = self.env.ref('pragtech_dental_management.report_sign2_pdf').render([1], data=data)
        att_id = self.env['ir.attachment'].create({
            'name': 'Questionnaire_' + self.updated_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': self.name.name + '_Questionnaire.pdf',
            'res_model': 'medical.patient',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def action_approval_wizard(self):
        return {
            'name': _('Sign Form'),
            'type': 'ir.actions.act_window',
            'res_model': 'sign.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': False,
            'context': {
                'default_patient_id': self.id,
            }
        }


class PatientNationality(models.Model):
    _name = "patient.nationality"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')


class MedicalPatientDisease(models.Model):
    _name = "medical.patient.disease"
    _description = "Disease info"
    _order = 'is_active desc, disease_severity desc, is_infectious desc, is_allergy desc, diagnosed_date desc'

    name = fields.Many2one('medical.patient', 'Patient ID', readonly=True)
    disease_severity = fields.Selection([('1_mi', 'Mild'), ('2_mo', 'Moderate'), ('3_sv', 'Severe'), ], 'Severity',
                                        index=True)
    is_on_treatment = fields.Boolean('Currently on Treatment')
    is_infectious = fields.Boolean('Infectious Disease',
                                   help="Check if the patient has an infectious / transmissible disease")
    short_comment = fields.Char('Remarks', size=128,
                                help="Brief, one-line remark of the disease. Longer description will go on the Extra info field")
    doctor = fields.Many2one('medical.physician', 'Physician', help="Physician who treated or diagnosed the patient")
    diagnosed_date = fields.Date('Date of Diagnosis')
    healed_date = fields.Date('Healed')
    is_active = fields.Boolean('Active disease', default=True)
    age = fields.Integer('Age when diagnosed', help='Patient age at the moment of the diagnosis. Can be estimative')
    pregnancy_warning = fields.Boolean('Pregnancy warning')
    weeks_of_pregnancy = fields.Integer('Contracted in pregnancy week #')
    is_allergy = fields.Boolean('Allergic Disease')
    allergy_type = fields.Selection(
        [('da', 'Drug Allergy'), ('fa', 'Food Allergy'), ('ma', 'Misc Allergy'), ('mc', 'Misc Contraindication'), ],
        'Allergy type', index=True)
    pcs_code = fields.Many2one('medical.procedure', 'Code',
                               help="Procedure code, for example, ICD-10-PCS Code 7-character string")
    treatment_description = fields.Char('Treatment Description', size=128)
    date_start_treatment = fields.Date('Start of treatment')
    date_stop_treatment = fields.Date('End of treatment')
    status = fields.Selection(
        [('c', 'chronic'), ('s', 'status quo'), ('h', 'healed'), ('i', 'improving'), ('w', 'worsening'), ],
        'Status of the disease', )
    extra_info = fields.Text('Extra Info')

    _sql_constraints = [
        ('validate_disease_period', "CHECK (diagnosed_date < healed_date )",
         "DIAGNOSED Date must be before HEALED Date !"),
        ('end_treatment_date_before_start', "CHECK (date_start_treatment < date_stop_treatment )",
         "Treatment start Date must be before Treatment end Date !")
    ]


class MedicalDoseUnit(models.Model):
    _name = "medical.dose.unit"

    name = fields.Char('Unit', size=32, required=True, )
    desc = fields.Char('Description', size=64)

    _sql_constraints = [
        ('dose_name_uniq', 'unique(name)', 'The Unit must be unique !'),
    ]


class MedicalDrugRoute(models.Model):
    _name = "medical.drug.route"

    name = fields.Char('Route', size=64, required=True)
    code = fields.Char('Code', size=32)

    _sql_constraints = [
        ('route_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]


class MedicalDrugForm(models.Model):
    _name = "medical.drug.form"

    name = fields.Char('Form', size=64, required=True, )
    code = fields.Char('Code', size=32)

    _sql_constraints = [
        ('drug_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]


class MedicalMedicinePrag(models.Model):
    _name = "medical.medicine.prag"

    name = fields.Char('Form', size=64, required=True, )
    code = fields.Char('Code', size=32)

    _sql_constraints = [
        ('drug_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]


class MedicalMedicationDosage(models.Model):
    _name = "medical.medication.dosage"
    _description = "Medicament Common Dosage combinations"

    name = fields.Char('Frequency', size=256, help='Common frequency name', required=True, )
    code = fields.Char('Code', size=64, help='Dosage Code, such as SNOMED, 229798009 = 3 times per day')
    abbreviation = fields.Char('Abbreviation', size=64,
                               help='Dosage abbreviation, such as tid in the US or tds in the UK')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Unit already exists')]


class MedicalAppointment(models.Model):
    _name = "medical.appointment"
    _order = "appointment_sdate desc"
    _inherit = ['mail.thread']

    @api.multi
    def unlink(self):
        raise ValidationError(_('You cannot delete Appointment.'))
        return super(MedicalAppointment, self).unlink()

    attachment_ids = fields.One2many('ir.attachment', 'appointment_id', 'attachments', track_visibility='onchange')

    @api.multi
    def get_img(self):
        for rec in self:
            res = {}
            img_lst_ids = []
            imd = self.env['ir.model.data']
            action_view_id = imd.xmlid_to_res_id('action_result_image_view')
            for i in rec.attachment_ids:
                img_lst_ids.append(i.id)
            res['image'] = img_lst_ids

            return {
                'type': 'ir.actions.client',
                'name': 'Appointment image',
                'tag': 'result_images',
                'params': {
                    'patient_id': rec.id or False,
                    'model': 'medical.appointment',
                    'values': res
                },
            }

    @api.model
    def _get_default_doctor(self):
        doc_ids = None
        partner_ids = [x.id for x in
                       self.env['res.partner'].search([('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])]
        if partner_ids:
            doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
        return doc_ids

    @api.multi
    def delayed_time(self):
        result = {}
        for patient_data in self:
            if patient_data.checkin_time and patient_data.checkin_time > patient_data.appointment_sdate:
                patient_data.delayed = True
            else:
                patient_data.delayed = False

    @api.multi
    def _waiting_time(self):
        def compute_time(checkin_time, ready_time):
            now = datetime.now()
            if checkin_time and ready_time:
                ready_time = datetime.strptime(ready_time, '%Y-%m-%d %H:%M:%S')
                checkin_time = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                delta = relativedelta(ready_time, checkin_time)
                years_months_days = str(delta.hours) + "h " + str(delta.minutes) + "m "
            else:
                years_months_days = "No Waiting time !"

            return years_months_days

        for patient_data in self:
            patient_data.waiting_time = compute_time(patient_data.checkin_time, patient_data.ready_time)

    READONLY_STATES_APPOINT = {
        'done': [('readonly', True)],
    }

    READONLY_STATES_INCHAIR = {'draft': [('readonly', False)],
                               'confirmed': [('readonly', False)]}

    READONLY_STATES_CHECKIN = {'draft': [('readonly', False)],
                               'confirmed': [('readonly', False)], 'checkin': [('readonly', False)]}

    operations = fields.One2many('medical.teeth.treatment', 'appt_id', 'Operations',
                                 track_visibility='onchange')
    doctor = fields.Many2one('medical.physician', 'Doctor', help="Doctor's Name",
                             required=True,
                             default=_get_default_doctor, readonly=True, states=READONLY_STATES_INCHAIR,
                             track_visibility='onchange')
    name = fields.Char('Appointment ID', size=64, readonly=True, default=lambda self: _('New'),
                       track_visibility='onchange')
    patient = fields.Many2one('medical.patient', 'Patient', help="Patient Name", required=False, readonly=True,
                              states=READONLY_STATES_INCHAIR, track_visibility='onchange')
    appointment_sdate = fields.Datetime('Appointment Start', required=True, default=fields.Datetime.now,
                                        readonly=False, states=READONLY_STATES_APPOINT, track_visibility='onchange')
    appointment_edate = fields.Datetime('Appointment End', required=False, readonly=False,
                                        states=READONLY_STATES_APPOINT, track_visibility='onchange')
    room_id = fields.Many2one('medical.hospital.oprating.room', 'Room', required=False, readonly=False,
                              states=READONLY_STATES_APPOINT, track_visibility='onchange')
    urgency = fields.Boolean('Urgent', default=False, readonly=True, states=READONLY_STATES_CHECKIN,
                             track_visibility='onchange')
    comments = fields.Text('Note', readonly=False, states=READONLY_STATES_APPOINT, track_visibility='onchange')
    checkin_time = fields.Datetime('Checkin Time', readonly=True, track_visibility='onchange')
    ready_time = fields.Datetime('In Chair', readonly=True, track_visibility='onchange')
    waiting_time = fields.Char('Waiting Time', compute='_waiting_time')
    no_invoice = fields.Boolean('Invoice exempt', readonly=False, states=READONLY_STATES_APPOINT,
                                track_visibility='onchange')
    invoice_done = fields.Boolean('Invoice Done', readonly=False, states=READONLY_STATES_APPOINT,
                                  track_visibility='onchange')
    user_id = fields.Many2one('res.users', related='doctor.user_id', string='doctor', store=True,
                              track_visibility='onchange')
    inv_id = fields.Many2one('account.invoice', 'Invoice', readonly=True, track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Booked'), ('confirmed', 'Confirmed'), ('missed', 'Missed'),
         ('checkin', 'Checked In'), ('ready', 'In Chair'), ('done', 'Completed'), ('cancel', 'Canceled')], 'State',
        readonly=True, default='draft', track_visibility='onchange')
    apt_id = fields.Boolean(default=False, track_visibility='onchange')
    apt_process_ids = fields.Many2many('medical.procedure', 'apt_process_rel', 'appointment_id', 'process_id',
                                       "Initial Treatment", readonly=False, states=READONLY_STATES_APPOINT,
                                       track_visibility='onchange')
    pres_id1 = fields.One2many('medical.prescription.order', 'pid1', 'Prescription', readonly=False,
                               states=READONLY_STATES_APPOINT, track_visibility='onchange')
    patient_state = fields.Selection([('walkin', 'Walk In'), ('withapt', 'Come with Appointment')], 'Patients status',
                                     required=True, default='walkin', readonly=True, states=READONLY_STATES_INCHAIR,
                                     track_visibility='onchange')
    #     treatment_ids = fields.One2many ('medical.lab', 'apt_id', 'Treatments')
    saleperson_id = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, readonly=False,
                                    states=READONLY_STATES_APPOINT, track_visibility='onchange')
    delayed = fields.Boolean(compute='delayed_time', string='Delayed', store=True, track_visibility='onchange')

    _sql_constraints = [
        ('date_check', "CHECK (appointment_sdate <= appointment_edate)",
         "Appointment Start Date must be before Appointment End Date !"), ]

    @api.multi
    def get_date(self, date1, lang):
        new_date = ''
        if date1:
            search_id = self.env['res.lang'].search([('code', '=', lang)])
            new_date = datetime.strftime(datetime.strptime(date1, '%Y-%m-%d %H:%M:%S').date(), search_id.date_format)
        return new_date

    @api.multi
    def cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def confirm_appointment(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def ready(self):
        ready_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.write({'state': 'ready', 'ready_time': ready_time})
        return True

    @api.multi
    def missed(self):
        self.write({'state': 'missed'})

    @api.model
    def create(self, vals):
        for appointmnet in self:
            if appointmnet.room_id.id == vals['room_id']:
                history_start_date = datetime.strptime(appointmnet.appointment_sdate, '%Y-%m-%d %H:%M:%S')
                print("\n\n history_start_date-----", history_start_date, type(history_start_date))
                history_end_date = False
                reservation_end_date = False
                if appointmnet.appointment_edate:
                    history_end_date = datetime.strptime(appointmnet.appointment_edate, '%Y-%m-%d %H:%M:%S')
                reservation_start_date = datetime.strptime(vals['appointment_sdate'], '%Y-%m-%d %H:%M:%S')
                #                 if vals.has_key('appointment_edate') and vals['appointment_edate']:
                if 'appointment_edate' in vals and vals['appointment_edate']:
                    reservation_end_date = datetime.strptime(vals['appointment_edate'], '%Y-%m-%d %H:%M:%S')
                if history_end_date and reservation_end_date:
                    if (history_start_date <= reservation_start_date < history_end_date) or (
                                    history_start_date < reservation_end_date <= history_end_date) or (
                                (reservation_start_date < history_start_date) and (
                                reservation_end_date >= history_end_date)):
                        raise ValidationError(
                            _('Room  %s is booked in this reservation period!') % (appointmnet.room_id.name))
                elif history_end_date:
                    if (history_start_date <= reservation_start_date) or (
                                history_start_date < reservation_end_date) or (
                        reservation_start_date < history_start_date):
                        raise ValidationError(
                            _('Room  %s is booked in this reservation period!') % (appointmnet.room_id.name))
                elif reservation_end_date:
                    if (history_start_date <= reservation_start_date < history_end_date) or (
                                history_start_date <= history_end_date) or (
                        reservation_start_date < history_start_date):
                        raise ValidationError(
                            _('Room  %s is booked in this reservation period!') % (appointmnet.room_id.name))
            if appointmnet.doctor.id == vals['doctor']:
                reservation_end_date = False
                history_end_date = False
                history_start_date = datetime.strptime(appointmnet.appointment_sdate, '%Y-%m-%d %H:%M:%S')
                if appointmnet.appointment_edate:
                    history_end_date = datetime.strptime(appointmnet.appointment_edate, '%Y-%m-%d %H:%M:%S')
                reservation_start_date = datetime.strptime(vals['appointment_sdate'], '%Y-%m-%d %H:%M:%S')
                if vals['appointment_edate']:
                    reservation_end_date = datetime.strptime(vals['appointment_edate'], '%Y-%m-%d %H:%M:%S')
                print("\n -history_start_date--reservation_start_date-", reservation_end_date and history_end_date,
                      history_start_date, reservation_start_date, reservation_end_date, history_end_date)
                if (reservation_end_date and history_end_date) and (
                                (history_start_date <= reservation_start_date < history_end_date) or (
                                            history_start_date < reservation_end_date <= history_end_date) or (
                                    (reservation_start_date < history_start_date) and (
                                    reservation_end_date >= history_end_date))):
                    raise ValidationError(
                        _('Doctor  %s is booked in this reservation period !') % (appointmnet.doctor.name.name))

        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or 'New'

        result = super(MedicalAppointment, self).create(vals)
        if result.patient_state == 'walkin':
            result.checkin()
        if 'patient' in list(vals.keys()) and vals['patient']:
            self._cr.execute('insert into pat_apt_rel(patient,apid) values (%s,%s)', (vals['patient'], result.id))
        return result

    patient_name = fields.Char("Patient Name", readonly=False, states=READONLY_STATES_APPOINT,
                               track_visibility='onchange')
    patient_phone = fields.Char("Patient Phone", readonly=False, states=READONLY_STATES_APPOINT,
                                track_visibility='onchange')
    qid = fields.Char("QID", track_visibility='onchange')
    is_registered = fields.Boolean("Is a registered patient?", readonly=True, states=READONLY_STATES_INCHAIR,
                                   track_visibility='onchange')
    patient_revisit = fields.Boolean("Patient Revisit ?", readonly=True, track_visibility='onchange')
    treatment_ids = fields.One2many("treatment.invoice", 'appointment_id', "Treatments", readonly=False,
                                    states=READONLY_STATES_APPOINT, track_visibility='onchange')
    finding_ids = fields.One2many("complaint.finding", 'appt_id', "Complaints and findings", readonly=False,
                                  states=READONLY_STATES_APPOINT, track_visibility='onchange')
    prescription_ids = fields.One2many("prescription.line", 'appt_id', "Prescriptions", readonly=False,
                                       states=READONLY_STATES_APPOINT, track_visibility='onchange')
    invoice_id = fields.Many2one("account.invoice", "Invoice entry", readonly=True, track_visibility='onchange')
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)
    invoice_ids = fields.Many2many("account.invoice", string='Invoices', compute="_get_invoiced", readonly=True,
                                   copy=False)
    payment_count = fields.Integer(string='# of Payments', compute='_get_payments', readonly=True)
    payment_ids = fields.Many2many("account.payment", string='Payments', compute="_get_payments", readonly=True,
                                   copy=False)
    amount_due = fields.Char('Outstanding Amount', compute='_get_invoiced')
    plan_signature = fields.Binary(string='Signature')
    treatment_plan_date = fields.Date(string="Treatment Plan Date", track_visibility='onchange')
    hav_operation = fields.Boolean("Have operation?", compute='_get_hav_operation')
    hav_prescription = fields.Boolean("Have Prescription?", compute='_get_hav_prescription')

    @api.multi
    def print_prescription(self):
        datas = {'ids': self.ids}
        values = self.env.ref('pragtech_dental_management.prescription_report2').report_action(self, data=datas)
        return values

    @api.depends('name', 'patient', 'prescription_ids')
    def _get_hav_prescription(self):
        for appt in self:
            check_hav_prescrption = False
            for i in appt.prescription_ids:
                check_hav_prescrption = True
            appt.update({
                'hav_prescription': check_hav_prescrption
            })

    @api.depends('name', 'patient')
    def _get_hav_operation(self):
        for appt in self:
            check_hav_operation = False
            for i in appt.operations:
                check_hav_operation = True
            appt.update({
                'hav_operation': check_hav_operation
            })

    @api.multi
    def attach_treatment_plan(self):
        data = {'ids': self.ids}
        patient = ""
        if self.patient:
            patient = self.patient.name_get()[0][1]
        data, data_format = self.env.ref('pragtech_dental_management.report_treatment_plan2_pdf').render(self.ids,
                                                                                                         data=data)
        att_id = self.env['ir.attachment'].create({
            'name': 'Treatment_Plan_' + self.treatment_plan_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': patient + '_treatment_plan.pdf',
            'res_model': 'medical.appointment',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

    @api.multi
    def done(self):
        treatment_ids = self.treatment_ids
        invoice_vals = {}
        invoice_line_vals = []
        each_line = [0, False]
        product_dict = {}
        patient_brw = self.patient
        partner_brw = patient_brw.name
        jr_brw = self.env['account.journal'].search([('type', '=', 'sale'), ('name', '=', 'Customer Invoices')])
        ICPSudo = self.env['ir.config_parameter'].sudo()
        basic_product_id = literal_eval(ICPSudo.get_param('basic_product_id', default='False'))
        product_obj = self.env['product.product'].browse(basic_product_id)
        if not basic_product_id:
            raise Warning('You need to specify Product to be used for Basic Checkup.')
        product_dict['product_id'] = product_obj.id
        p_brw = product_obj
        if patient_brw.current_insurance.company_id.id in [comp.id for comp in
                                                           p_brw.insurance_company_ids]:
            product_dict[
                'amt_paid_by_patient'] = patient_brw.current_insurance.company_id.amt_paid_by_patient
            product_dict['discount_amt'] = patient_brw.current_insurance.company_id.discount_amt

        product_dict['name'] = product_obj.name
        product_dict['quantity'] = 1
        product_dict['price_unit'] = p_brw.lst_price
        cost_center_id = False
        if self.doctor:
            if self.doctor.department_id:
                if self.doctor.department_id:
                    cost_center_id = self.doctor.department_id.cost_center_id.id
        product_dict['cost_center_id'] = cost_center_id
        acc_obj = self.env['account.account'].search([('name', '=', 'Local Sales'),
                                                      ('user_type_id', '=', 'Income')], limit=1)
        for account_id in jr_brw:
            product_dict[
                'account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id

        each_line.append(product_dict)
        invoice_line_vals.append(each_line)
        # Creating invoice lines
        # get account id for products
        for each in treatment_ids:
            each_line = [0, False]
            product_dict = {}
            product_dict['product_id'] = each.description.id
            p_brw = each.description
            if patient_brw.current_insurance.company_id.id in [comp.id for comp in
                                                               p_brw.insurance_company_ids]:
                product_dict[
                    'amt_paid_by_patient'] = patient_brw.current_insurance.company_id.amt_paid_by_patient
                product_dict['discount_amt'] = patient_brw.current_insurance.company_id.discount_amt

            if each.note:
                product_dict['name'] = each.note
            else:
                product_dict['name'] = each.description.name
            product_dict['quantity'] = 1
            product_dict['price_unit'] = each.amount
            acc_obj = self.env['account.account'].search([('name', '=', 'Local Sales'),
                                                          ('user_type_id', '=', 'Income')], limit=1)
            for account_id in jr_brw:
                product_dict[
                    'account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id
            product_dict['cost_center_id'] = cost_center_id
            each_line.append(product_dict)
            invoice_line_vals.append(each_line)
        # Creating invoice dictionary
        invoice_vals['account_id'] = partner_brw.property_account_receivable_id.id
        invoice_vals['partner_id'] = partner_brw.id
        invoice_vals['dentist'] = self.doctor.id
        invoice_vals['cost_center_id'] = cost_center_id
        invoice_vals['is_patient'] = True
        invoice_vals['appt_id'] = self.id
        invoice_vals['insurance_company'] = patient_brw.current_insurance.company_id.id
        invoice_vals['invoice_line_ids'] = invoice_line_vals
        inv_id = self.env['account.invoice'].create(invoice_vals)
        return self.write({'state': 'done', 'invoice_id': inv_id.id})

    @api.onchange('is_registered')
    def _onchange_is_registered_field(self):
        for rec in self:
            if rec.is_registered:
                rec.patient_revisit = True
                rec.patient = False
                rec.patient_phone = False
                rec.patient_name = False
                rec.qid = False
            else:
                rec.patient = False
                rec.patient_phone = False
                rec.patient_name = False
                rec.qid = False
                rec.patient_revisit = False

    @api.multi
    def appt_open_chart(self):
        if self.patient:
            result = self.patient.open_chart()
            return result

    @api.multi
    def show_inv_due(self):
        pass

    @api.onchange('appointment_sdate')
    def onchange_appointment_sdate(self):
        for rec in self:
            if rec.appointment_sdate:
                date_start = datetime.strptime(str(rec.appointment_sdate), '%Y-%m-%d %H:%M:%S')
                rec.appointment_edate = date_start + timedelta(minutes=15)

    @api.onchange('patient')
    def onchange_patient(self):
        for rec in self:
            if rec.patient:
                rec.patient_name = rec.patient.name.name
                rec.patient_phone = rec.patient.mobile
                rec.qid = rec.patient.qid
                rec.is_registered = True

    @api.multi
    def write(self, vals):
        if 'patient' in list(vals.keys()):
            qry = """SELECT * FROM pat_apt_rel WHERE apid = %s"""
            self._cr.execute(qry, [self.id])
            res = self._cr.fetchall()
            if res:
                self._cr.execute('UPDATE pat_apt_rel SET patient=%s WHERE apid=%s', (vals['patient'], self.id))
            else:
                self._cr.execute('insert into pat_apt_rel(patient,apid) values (%s,%s)', (vals['patient'], self.id))
        return super(MedicalAppointment, self).write(vals)

    @api.multi
    def confirm(self):
        for rec in self:
            rec.write({'state': 'confirmed'})

    @api.multi
    def treatment_plan(self):
        appt = self.id
        doctor = ""
        patient = ""
        if self.patient_id:
            patient = self.patient.patient_name
        if self.dentist:
            doctor = self.dentist.name.name
        return {
            'name': _('Treatment Plan'),
            'type': 'ir.actions.act_window',
            'res_model': 'treatment.sign.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': False,
            'context': {
                'default_appt_id': appt,
                'default_doctor': doctor,
                'default_patient': patient,
            }
        }

    @api.multi
    def questionnaire_popup(self):
        if self.patient:
            language = 'english'
            if self.patient.language:
                language = self.patient.language
            return {
                'name': _('Registration Form'),
                'type': 'ir.actions.act_window',
                'res_model': 'patient.registration',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'nodestroy': False,
                'context': {
                    'default_patient_id': self.patient.id,
                    'default_language': language,
                    'default_emergency_name': self.patient.emergency_name,
                    'default_emergency_phone': self.patient.emergency_phone,
                    'default_emergency_relation': self.patient.emergency_relation,
                    'default_dob': self.patient.dob,
                    'default_qid': self.patient.qid,
                    'default_address': self.patient.address,
                    'default_other_mobile': self.patient.other_mobile,
                    'default_mobile': self.patient.mobile,
                    'default_patient_name': self.patient.patient_name,
                    'default_name_tag': self.patient.name_tag,
                }
            }

    def checkin(self):
        checkin_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.write({'state': 'checkin', 'checkin_time': checkin_time})
        if self.doctor:
            doctor_partner = self.doctor.name
            for user in self.env['res.users'].search([]):
                if user.partner_id == doctor_partner:
                    checkin_local = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=3)
                    checkin_local = datetime.strftime(checkin_local, '%I:%M:%S %p')
                    message = self.patient_name + " checked In at " + str(checkin_local)
                    user.notify_info(message, title='Patient Checked In', sticky=True)

        if not self.patient:
            partner_id = self.env['res.partner'].create({'name': self.patient_name,
                                                         'phone': self.patient_phone,
                                                         'is_patient': True,
                                                         'is_person': True,
                                                         })
            patient_id = self.env['medical.patient'].create({'name': partner_id.id,
                                                             'patient_name': self.patient_name,
                                                             'register_date': date.today(),
                                                             'mobile': self.patient_phone,
                                                             'qid': self.qid
                                                             })
            self.patient = patient_id
            # return {
            #     'name': _('Patient Details'),
            #     'view_mode': 'form',
            #     'view_id':  self.env.ref('pragtech_dental_management.medical_patient_view').id,
            #     'res_model': 'medical.patient',
            #     'type': 'ir.actions.act_window',
            #     'res_id': patient_id.id,
            #     'target': 'form',
            # }

    @api.depends('name')
    def _get_payments(self):
        for appt in self:
            if appt.patient:
                patient = appt.patient
                payment_ids = self.env['account.payment'].search([('partner_id', '=', patient.name.id),
                                                                  ('partner_type', '=', 'customer')])
                appt.update({
                    'payment_count': len(set(payment_ids.ids)),
                    'payment_ids': payment_ids.ids
                })
            else:
                appt.update({
                    'payment_count': 0,
                    'payment_ids': []
                })

    @api.multi
    def action_view_payment(self):
        payments = self.mapped('payment_ids')
        action = self.env.ref('account.action_account_payments').read()[0]
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = payments.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends('name', 'patient')
    def _get_invoiced(self):
        for appt in self:
            if appt.patient:
                patient = appt.patient
                invoice_ids = self.env['account.invoice'].search([('partner_id', '=', patient.name.id),
                                                                  ('type', '=', 'out_invoice')])
                amount_due = 0
                for inv in invoice_ids:
                    amount_due += inv.residual_signed
                appt.update({
                    'invoice_count': len(set(invoice_ids.ids)),
                    'invoice_ids': invoice_ids.ids,
                    'amount_due': "{:.2f}".format(amount_due)
                })
            else:
                appt.update({
                    'invoice_count': 0,
                    'invoice_ids': []
                })

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['context'] = {'hide_for_service_bill': True, 'show_for_service_bill': True}
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class MedicalPatientMedication(models.Model):
    _name = "medical.patient.medication"
    _description = "Patient Medication"

    name = fields.Many2one('medical.patient', 'Patient ID', readonly=True)
    doctor = fields.Many2one('medical.physician', 'Physician', help="Physician who prescribed the medicament")
    is_active = fields.Boolean('Active', default=True,
                               help="Check this option if the patient is currently taking the medication")
    discontinued = fields.Boolean('Discontinued')
    course_completed = fields.Boolean('Course Completed')
    discontinued_reason = fields.Char('Reason for discontinuation', size=128,
                                      help="Short description for discontinuing the treatment")
    adverse_reaction = fields.Text('Adverse Reactions',
                                   help="Specific side effects or adverse reactions that the patient experienced")
    notes = fields.Text('Extra Info')
    patient_id = fields.Many2one('medical.patient', 'Patient')

    @api.multi
    @api.onchange('course_completed', 'discontinued', 'is_active')
    def onchange_medication(self):
        if self.course_completed:
            self.is_active = False
            self.discontinued = False
        elif self.is_active == False and self.discontinued == False and self.course_completed == False:
            self.is_active = True
        if self.discontinued:
            self.is_active = False
            self.course_completed = False
        elif self.is_active == False and self.discontinued == False and self.course_completed == False:
            self.is_active = True
        if self.is_active == True:
            self.course_completed = False
            self.discontinued = False
        elif self.is_active == False and self.discontinued == False and self.course_completed == False:
            self.course_completed = True


class MedicalPrescriptionOrder(models.Model):
    _name = "medical.prescription.order"
    _description = "prescription order"

    @api.model
    def _get_default_doctor(self):
        doc_ids = None
        partner_ids = self.env['res.partner'].search([('user_id', '=', self.env.user.id), ('is_doctor', '=', True)])
        if partner_ids:
            partner_ids = [x.id for x in partner_ids]
            doc_ids = [x.id for x in self.env['medical.physician'].search([('name', 'in', partner_ids)])]
        return doc_ids

    name = fields.Many2one('medical.patient', 'Patient ID', required=True, )
    prescription_id = fields.Char('Prescription ID', size=128, default='New',
                                  help='Type in the ID of this prescription')
    prescription_date = fields.Datetime('Prescription Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'Log In User', readonly=True, default=lambda self: self.env.user)
    pharmacy = fields.Many2one('res.partner', 'Pharmacy', domain=[('is_pharmacy', '=', True)])
    notes = fields.Text('Prescription Notes')
    pid1 = fields.Many2one('medical.appointment', 'Appointment', )
    doctor = fields.Many2one('medical.physician', 'Prescribing Doctor', help="Physician's Name",
                             default=_get_default_doctor)
    p_name = fields.Char('Demo', default=False)
    no_invoice = fields.Boolean('Invoice exempt')
    invoice_done = fields.Boolean('Invoice Done')
    state = fields.Selection([('invoiced', 'Invoiced'), ('tobe', 'To be Invoiced')], 'Invoice Status', default='tobe')
    inv_id = fields.Many2one('account.invoice', 'Invoice', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=True)

    _sql_constraints = [
        ('pid1', 'unique (pid1)', 'Prescription must be unique per Appointment'),
        ('prescription_id', 'unique (prescription_id)', 'Prescription ID must be unique')]

    @api.multi
    @api.onchange('name')
    def onchange_name(self):
        domain_list = []
        domain = {}
        if self.name:
            apt_ids = self.search([('name', '=', self.name.id)])
            for apt in apt_ids:
                if apt.pid1:
                    domain_list.append(apt.pid1.id)
        domain['pid1'] = [('id', 'not in', domain_list)]
        return {'domain': domain}

    @api.model
    def create(self, vals):
        if vals.get('prescription_id', 'New') == 'New':
            vals['prescription_id'] = self.env['ir.sequence'].next_by_code('medical.prescription') or 'New'
        result = super(MedicalPrescriptionOrder, self).create(vals)
        return result

    #         def onchange_p_name(self, cr, uid, ids, p_name,context = None ):
    #          n_name=context.get('name')
    #          d_name=context.get('physician_id')
    #          v={}
    #          v['name'] =  n_name
    #          v['doctor'] =  d_name
    #          return {'value': v}

    @api.multi
    def get_date(self, date1, lang):
        new_date = ''
        if date1:
            search_id = self.env['res.lang'].search([('code', '=', lang)])
            new_date = datetime.strftime(datetime.strptime(date1, '%Y-%m-%d %H:%M:%S').date(), search_id.date_format)
        return new_date


class MedicalHospitalBuilding(models.Model):
    _name = "medical.hospital.building"

    name = fields.Char('Name', size=128, required=True, help="Name of the building within the institution")
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', "1")],
                                  help="Medical Center")
    code = fields.Char('Code', size=64)
    extra_info = fields.Text('Extra Info')


class MedicalHospitalUnit(models.Model):
    _name = "medical.hospital.unit"

    name = fields.Char('Name', size=128, required=True, help="Name of the unit, eg Neonatal, Intensive Care, ...")
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', "1")],
                                  help="Medical Center")
    code = fields.Char('Code', size=64)
    extra_info = fields.Text('Extra Info')


class MedicalHospitalOpratingRoom(models.Model):
    _name = "medical.hospital.oprating.room"

    name = fields.Char('Name', size=128, required=True, help='Name of the Operating Room')
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', True)],
                                  help='Medical Center')
    building = fields.Many2one('medical.hospital.building', 'Building', index=True)
    unit = fields.Many2one('medical.hospital.unit', 'Unit')
    extra_info = fields.Text('Extra Info')

    _sql_constraints = [
        ('name_uniq', 'unique (name, institution)', 'The Operating Room code must be unique per Health Center.')]


class MedicalProcedure(models.Model):
    _description = "Medical Procedure"
    _name = "medical.procedure"

    name = fields.Char('Code', size=128, required=True)
    description = fields.Char('Long Text', size=256)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|', ('name', operator, name), ('description', operator, name)])
        if not recs:
            recs = self.search([('name', operator, name)])
        return recs.name_get()


class TeethCode(models.Model):
    _description = "teeth code"
    _name = "teeth.code"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=128, required=True)
    palmer_name = fields.Char('palmer_name', size=128, required=True)
    palmer_internal_id = fields.Integer('Palmar Internam ID')
    iso = fields.Char('iso', size=128, required=True)
    internal_id = fields.Integer('Internal IDS')

    @api.multi
    def write(self, vals):
        for rec in self:
            #             if vals.has_key('palmer_name'):
            if 'palmer_name' in vals:
                lst = self.search([('palmer_internal_id', '=', rec.palmer_internal_id)])
                #                 lst.write({'palmer_name': vals['palmer_name']})
                super(TeethCode, lst).write({'palmer_name': vals['palmer_name']})
        return super(TeethCode, self).write(vals)

    @api.model
    def name_get(self):
        res = []
        teeth_obj = self.env['chart.selection'].search([])
        obj = teeth_obj[-1]
        for each in self:
            name = each.name
            if obj.type == 'palmer':
                name = str(each.palmer_internal_id)
                if each.internal_id <= 8:
                    name += '-1x'
                elif each.internal_id <= 16:
                    name += '-2x'
                elif each.internal_id <= 24:
                    name += '-3x'
                else:
                    name += '-4x'
            elif obj.type == 'iso':
                name = each.iso
            res.append((each.id, name))
        return res

    @api.multi
    def get_teeth_code(self):
        l1 = [];
        d1 = {};
        teeth_ids = self.env['teeth.code'].search([])
        teeth_obj = self.env['chart.selection'].search([])
        teeth_type = teeth_obj[-1]
        for teeth in teeth_ids:
            if teeth_type.type == 'palmer':
                d1[int(teeth.internal_id)] = teeth.palmer_name
            elif teeth_type.type == 'iso':
                d1[int(teeth.internal_id)] = teeth.iso
            else:
                d1[int(teeth.internal_id)] = teeth.name
        x = d1.keys()
        x = sorted(x)
        for i in x:
            l1.append(d1[i])
        return l1;


class ChartSelection(models.Model):
    _description = "teeth chart selection"
    _name = "chart.selection"

    type = fields.Selection(
        [('universal', 'Universal Numbering System'), ('palmer', 'Palmer Method'), ('iso', 'ISO FDI Numbering System')],
        'Select Chart Type', default='universal')


class ProductCategory(models.Model):
    _inherit = "product.category"
    _description = "Product Category"

    treatment = fields.Boolean('Treatment')

    @api.multi
    def get_treatment_categs(self):
        all_records = self.search([])
        treatment_list = []
        for each_rec in all_records:
            if each_rec.treatment == True:
                treatment_list.append({'treatment_categ_id': each_rec.id, 'name': each_rec.name, 'treatments': []})

        product_rec = self.env['product.product'].search([('is_treatment', '=', True)])
        for each_product in product_rec:
            each_template = each_product.product_tmpl_id
            for each_treatment in treatment_list:
                if each_template.categ_id.id == each_treatment['treatment_categ_id']:
                    each_treatment['treatments'].append(
                        {'treatment_id': each_product.id, 'treatment_name': each_template.name,
                         'action': each_product.action_perform})
                    break

        return treatment_list


class MedicalTeethTreatment(models.Model):
    _description = "Teeth Treatment"
    _name = "medical.teeth.treatment"

    @api.model
    def _default_dignose(self):
        st_id = self.env['diagnosis'].search([], limit=1)
        return st_id

    patient_id = fields.Many2one('medical.patient', 'Patient Details')
    teeth_id = fields.Many2one('teeth.code', 'Tooth')
    description = fields.Many2one('product.product', 'Description', domain=[('is_treatment', '=', True)])
    detail_description = fields.Text('Surface')
    state = fields.Selection(
        [('planned', 'Planned'), ('condition', 'Condition'), ('completed', 'Completed'), ('in_progress', 'In Progress'),
         ('invoiced', 'Invoiced')], 'Status', default='planned')
    dentist = fields.Many2one('medical.physician', 'Doctor')
    amount = fields.Float('Amount')
    appt_id = fields.Many2one('medical.appointment', 'Appointment ID')
    teeth_code_rel = fields.Many2many('teeth.code', 'teeth_code_medical_teeth_treatment_rel', 'operation', 'teeth')
    diagnosis_id = fields.Many2one('diagnosis', 'Diagnosis', default=_default_dignose)
    diagnosis_description = fields.Text('Notes')
    treatment_invoice = fields.Many2one("treatment.invoice")
    amt_paid_by_patient = fields.Float('Co-payment(%)', default=100, readonly=True)
    amt_to_be_patient = fields.Float('Payment by Patient', readonly=True)

    @api.model
    def write(self, vals):
        appoints = self.mapped('appt_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appt_id == apps)
            msg = "<b> Updated Prescription Line :</b><ul>"
            for line in order_lines:
                if vals.get('description'):
                    msg += "<li>" + _("Description") + ": %s -> %s <br/>" % (
                    line.description.name, self.env['product.product'].browse(vals['description']).name,)
                if vals.get('diagnosis_id'):
                    msg += "<li>" + _("Diagnosis") + ": %s -> %s <br/>" % (
                    line.diagnosis_id.name, self.env['diagnosis'].browse(vals['diagnosis_id']).name,)
                if vals.get('diagnosis_description'):
                    msg += "<li>" + _("Notes") + ": %s -> %s <br/>" % (
                    line.diagnosis_description, vals['diagnosis_description'],)
                if vals.get('teeth_id'):
                    msg += "<li>" + _("Tooth") + ": %s -> %s <br/>" % (
                    line.teeth_id, self.env['teeth.code'].browse(vals['teeth_id']).name,)
                if vals.get('detail_description'):
                    msg += "<li>" + _("Notes") + ": %s -> %s <br/>" % (
                    line.detail_description, vals['detail_description'],)
                if vals.get('state'):
                    msg += "<li>" + _("State") + ": %s -> %s <br/>" % (line.state, vals['state'],)
                if vals.get('amount'):
                    msg += "<li>" + _("Amount") + ": %s -> %s <br/>" % (line.amount, vals['amount'],)
                if vals.get('amt_paid_by_patient'):
                    msg += "<li>" + _("Co-payment(%)") + ": %s -> %s <br/>" % (
                    line.amt_paid_by_patient, vals['amt_paid_by_patient'],)
                if vals.get('amt_to_be_patient'):
                    msg += "<li>" + _("Payment by Patient") + ": %s -> %s <br/>" % (
                    line.amt_to_be_patient, vals['amt_to_be_patient'],)
            msg += "</ul>"
            apps.message_post(body=msg)

        result = super(MedicalTeethTreatment, self).write(vals)
        if 'state' in list(vals.keys()):
            if self.state in ['in_progress', 'completed']:
                invoiced_treatments = self.env['treatment.invoice'].search([('treatment_id', '=', result.id)])
                if invoiced_treatments:
                    pass
                else:
                    if result.patient_id:
                        appt_id = self.env['medical.appointment'].search([('patient', '=', result.patient_id.id),
                                                                          ('state', 'in', ['checkin', 'ready'])],
                                                                         limit=1)
                        p_brw = result.description
                        if result.patient_id.current_insurance.company_id.id in [comp.id for comp in
                                                                                 p_brw.insurance_company_ids]:
                            vals[
                                'amt_paid_by_patient'] = result.patient_id.current_insurance.company_id.amt_paid_by_patient

                        if appt_id:
                            inv_id = self.env['treatment.invoice'].create({'appointment_id': appt_id.id,
                                                                           'treatment_id': result.id,
                                                                           'description': result.description.id,
                                                                           'amount': result.amount
                                                                           })

        return result

    @api.model
    def create(self, vals):
        if 'state' not in list(vals.keys()):
            vals['state'] = 'planned'
        elif 'state' in list(vals.keys()) and not vals['state']:
            vals['state'] = 'planned'
        if 'description' and 'patient_id' in list(vals.keys()):
            p_brw = self.env['product.product'].search([('id', '=', vals['description'])])
            pat_obj = self.env['medical.patient'].search([('id', '=', vals['patient_id'])])
            vals['amt_to_be_patient'] = vals['amount']
            if pat_obj.current_insurance.company_id.id in [comp.id for comp in
                                                           p_brw.insurance_company_ids]:
                vals['amt_paid_by_patient'] = pat_obj.current_insurance.company_id.amt_paid_by_patient
                if 'amount' in list(vals.keys()):
                    vals['amt_to_be_patient'] = (pat_obj.current_insurance.company_id.amt_paid_by_patient * vals[
                        'amount']) / 100

        result = super(MedicalTeethTreatment, self).create(vals)
        op_summary = self.env['operation.summary']
        operation_summary = op_summary.create(vals)
        appt_id = self.env['medical.appointment'].search([('patient', '=', result.patient_id.id),
                                                          ('state', 'in', ['checkin', 'ready'])],
                                                         limit=1)
        if not result.appt_id:
            result.appt_id = appt_id
            operation_summary.appt_id = appt_id
        # op_ids = op_summary.search([('appt_id', '=', appt_id.id)])
        # if len(op_ids.ids) > 1:
        if result.state in ['in_progress', 'completed']:
            invoiced_treatments = self.env['treatment.invoice'].search([('treatment_id', '=', result.id)])
            if invoiced_treatments:
                pass
            else:
                if result.patient_id:
                    if appt_id:
                        inv_id = self.env['treatment.invoice'].create({'appointment_id': appt_id.id,
                                                                       'treatment_id': result.id,
                                                                       'description': result.description.id,
                                                                       'note': result.detail_description,
                                                                       'amount': result.amount})
        msg = "<b> Created New Operation:</b><ul>"
        if vals.get('description'):
            msg += "<li>" + _("Description") + ": %s<br/>" % (result.description.name)
        if vals.get('diagnosis_id'):
            msg += "<li>" + _("Diagnosis") + ": %s  <br/>" % (result.diagnosis_id.display_name)
        if vals.get('diagnosis_description'):
            msg += "<li>" + _("Notes") + ": %s  <br/>" % (result.diagnosis_description)
        if vals.get('teeth_id'):
            msg += "<li>" + _("Tooth") + ": %s  <br/>" % (result.teeth_id.name)
        if vals.get('state'):
            msg += "<li>" + _("State") + ": %s  <br/>" % (result.state)
        if vals.get('detail_description'):
            msg += "<li>" + _("Surface") + ": %s  <br/>" % (result.detail_description)
        if vals.get('amount'):
            msg += "<li>" + _("Amount") + ": %s  <br/>" % (result.amount)
        if vals.get('amt_paid_by_patient'):
            msg += "<li>" + _("Co-payment(%)") + ": %s  <br/>" % (result.amt_paid_by_patient)
        if vals.get('amt_to_be_patient'):
            msg += "<li>" + _("Payment by Patient") + ": %s  <br/>" % (result.amt_to_be_patient)
        msg += "</ul>"
        result.appt_id.message_post(body=msg)
        return result

    @api.multi
    def unlink(self):
        line = None
        for rec in self:
            msg = "<b> Deleted Operation with Values:</b><ul>"
            if rec.description:
                msg += "<li>" + _("Description") + ": %s <br/>" % (rec.description.name,)
            if rec.diagnosis_id:
                msg += "<li>" + _("Diagnosis") + ": %s  <br/>" % (rec.diagnosis_id.display_name,)
            if rec.diagnosis_description:
                msg += "<li>" + _("Notes") + ": %s  <br/>" % (rec.diagnosis_description)
            if rec.teeth_id:
                msg += "<li>" + _("Tooth") + ": %s  <br/>" % (rec.teeth_id.name)
            if rec.state:
                msg += "<li>" + _("State") + ": %s  <br/>" % (rec.state)
            if rec.detail_description:
                msg += "<li>" + _("Surface") + ": %s  <br/>" % (rec.detail_description)
            if rec.amount:
                msg += "<li>" + _("Amount") + ": %s  <br/>" % (rec.amount)
            if rec.amt_paid_by_patient:
                msg += "<li>" + _("Co-payment(%)") + ": %s  <br/>" % (rec.amt_paid_by_patient)
            if rec.amt_to_be_patient:
                msg += "<li>" + _("Payment by Patient") + ": %s  <br/>" % (rec.amt_to_be_patient)
            msg += "</ul>"
            rec.appt_id.message_post(body=msg)
            line = super(MedicalTeethTreatment, rec).unlink()
        return line

    signature = fields.Binary(string='Signature')
    updated_date = fields.Date('Updated Date')
    wizard_treatment = fields.Char("Treatment", readonly=True)
    wizard_doctor = fields.Char("Doctor", readonly=True)

    @api.multi
    def action_consent_form(self):
        treat = ""
        doctor = ""
        patient = ""
        if self.patient_id:
            patient = self.patient_id.name.name
        if self.dentist:
            doctor = self.dentist.name.name
        if self.description:
            treat = self.description.name
        if self.detail_description:
            treat = treat + " : " + self.detail_description
        return {
            'name': _('CONSENT FOR OPERATION / PROCEDURE'),
            'type': 'ir.actions.act_window',
            'res_model': 'treatment.sign.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': False,
            'context': {
                'default_treatment': treat,
                'default_doctor': doctor,
                'default_patient': patient,
            }
        }

    @api.multi
    def print_consent(self):
        data = {'ids': self.ids}
        treat = ""
        patient = ""
        if self.patient_id:
            patient = self.patient_id.name_get()[0][1]
        if self.description:
            treat = self.description.name
        if self.detail_description:
            treat = treat + " : " + self.detail_description
        data, data_format = self.env.ref('pragtech_dental_management.report_treatment_sign2_pdf').render(self.ids,
                                                                                                         data=data)
        att_id = self.env['ir.attachment'].create({
            'name': 'Consent_' + treat + "_" + self.updated_date,
            'type': 'binary',
            'datas': base64.encodestring(data),
            'datas_fname': patient + '_consent.pdf',
            'res_model': 'medical.patient',
            'res_id': self.patient_id.id,
            'mimetype': 'application/pdf'
        })


class PatientComplaintWizard(models.Model):
    _name = "patient.complaint.wizard"

    name = fields.Many2one('medical.physician', 'Attended Doctor')
    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', required=True, default='english')
    patient_id = fields.Many2one('medical.patient', 'Patient ID', required=True)
    complaint_subject = fields.Char('Complaint Subject', required=True)
    complaint_date = fields.Date('Date', default=fields.Date.context_today, required=True)
    complaint = fields.Text('Complaint')

    @api.multi
    def action_confirm(self):
        complaint_obj = self.env['patient.complaint']
        vals = self.read()[0]
        if self.patient_id:
            vals['patient_id'] = self.patient_id.id
        if self.name:
            vals['name'] = self.name.id
        complaint_obj.create(vals)


class patient_complaint(models.Model):
    _name = "patient.complaint"

    complaint_id = fields.Char("Ref", readonly=True, default=lambda self: _('New'))
    language = fields.Selection([('english', 'English'),
                                 ('arabic', 'Arabic')], 'Language', readonly=True, required=True, default='english')
    name = fields.Many2one('medical.physician', 'Attended Doctor')
    patient_id = fields.Many2one('medical.patient', 'Patient ID', readonly=True)
    complaint_subject = fields.Char('Complaint Subject', required=True, readonly=True)
    complaint_date = fields.Date('Date', default=fields.Date.context_today, required=True, readonly=True)
    complaint = fields.Text('Complaint', readonly=True)
    action_ta = fields.Text('Action Taken Against')
    action_by = fields.Many2one('res.users', 'Action updated by', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('complaint_id', 'New') == 'New':
            vals['complaint_id'] = self.env['ir.sequence'].next_by_code('patient.complaint') or 'New'
        result = super(patient_complaint, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if 'action_ta' in vals:
            if self.name:
                vals['action_by'] = self.env.uid
        result = super(patient_complaint, self).write(vals)
        return result

    @api.multi
    def unlink(self):
        raise ValidationError(_('You cannot delete complaint record.'))
        return super(patient_complaint, self).unlink()


class IrAttachment(models.Model):
    """
    Form for Attachment details
    """
    _inherit = "ir.attachment"
    _name = "ir.attachment"

    patient_id = fields.Many2one('medical.patient', 'Patient')
    appointment_id = fields.Many2one('medical.appointment', 'Appointment')

    @api.model
    def create(self, values):
        line = super(IrAttachment, self).create(values)
        msg = "<b> Created New Attachment:</b><ul>"
        if values.get('name'):
            msg += "<li>" + _("Name") + ": %s<br/>" % (line.name)
        msg += "</ul>"
        line.appointment_id.message_post(body=msg)
        return line

    @api.multi
    def write(self, values):
        appoints = self.mapped('appointment_id')
        for apps in appoints:
            order_lines = self.filtered(lambda x: x.appointment_id == apps)
            for line in order_lines:
                msg = "<b> Updated Attachment : </b><ul>"
                if values.get('name'):
                    msg += "<li>" + _("Name") + ": %s -> %s <br/>" % (line.name, values['name'],)
                if not values.get('name'):
                    msg = "<b> Updated File Content of Attachment : %s </b><ul>" % (line.name,)
                msg += "</ul>"
            apps.message_post(body=msg)
        result = super(IrAttachment, self).write(values)
        return result

    @api.multi
    def unlink(self):
        line = None
        for rec in self:
            msg = "<b> Deleted Attachment with Values:</b><ul>"
            if rec.name:
                msg += "<li>" + _("Name") + ": %s <br/>" % (rec.name,)
            msg += "</ul>"
            rec.appointment_id.message_post(body=msg)
            line = super(IrAttachment, rec).unlink()
        return line



