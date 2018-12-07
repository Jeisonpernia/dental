from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_open_new(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: inv.amount_total < 0):
            raise UserError(_(
                "You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        to_open_invoices.invoice_validate_new()

    @api.multi
    def invoice_validate_new(self):
        for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
            invoice.message_subscribe([invoice.partner_id.id])
        self._check_duplicate_supplier_reference()
        self.write({'state': 'open'})

    def action_invoice_Register_Payment(self):
        self.action_invoice_open_new()
        action = self.env.ref('account.action_account_invoice_payment').read()[0]
        return action

    patient = fields.Many2one("medical.patient", 'Patient', readonly=True)
    dentist = fields.Many2one('medical.physician', 'Doctor')
    insurance_company = fields.Many2one('res.partner', 'Insurance Company')
    insurance_company_domain = fields.Char('Domain', compute='_get_ins_company_domain', store=True)

    @api.onchange('insurance_company')
    @api.depends('insurance_company')
    def onchange_insurance_company(self):
        for line in self.invoice_line_ids:
            if line.apply_insurance:
                line.amt_paid_by_patient = self.insurance_company.amt_paid_by_patient
                line.amt_paid_by_insurance = self.insurance_company.amt_paid_by_insurance
                line.discount_amt = self.insurance_company.discount_amt
            else:
                line.amt_paid_by_patient = 100

    @api.multi
    @api.onchange('partner_id')
    def partner_onchange(self):
        if (self.partner_id and self.partner_id.is_patient):
            patient_id = self.env['medical.patient'].search([('name', '=', self.partner_id.id)])
            self.patient = patient_id.id
        else:
            self.patient = False

    @api.one
    @api.depends('partner_id', 'insurance_company_domain')
    def _get_ins_company_domain(self):
        if self.partner_id.is_patient:
            domain_list = [insurance.company_id.id for insurance in self.partner_id.insurance_ids]
            self.insurance_company_domain = json.dumps([('id', 'in', domain_list)])
        else:
            self.insurance_company_domain = json.dumps([('id', 'in', [])])

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        patient_id = self.env['medical.patient'].search([('name', '=', res.partner_id.id)])
        if patient_id:
            res.patient = patient_id.id
        else:
            res.patient = False
        return res

    @api.multi
    @api.onchange('partner_id')
    def check_patient_invoice(self):
        for rec in self:
            if rec.partner_id:
                rec.is_patient = rec.partner_id.is_patient
                rec.is_insurance_company = rec.partner_id.is_insurance_company
                patient_ids = self.env['medical.patient'].search([('name', '=', rec.partner_id.id)])
                if not rec.patient and patient_ids:
                    rec.patient = patient_ids.ids[0]
                else:
                    rec.patient = False
            else:
                rec.is_patient = False
                rec.is_insurance_company = False
                rec.patient = False

    is_patient = fields.Boolean("Is Patient?", readonly=True)
    is_insurance_company = fields.Boolean("Is Insurance company?", readonly=True)
    insurance_invoice = fields.Many2one("account.invoice", 'Insurance invoice', readonly=True)
    appt_id = fields.Many2one("medical.appointment", 'Appointment', readonly=True)
    insurance_total = fields.Monetary(string='Insurance Total', store=True, readonly=True,
                                      compute='_compute_insurance_total',
                                      track_visibility='always')
    treatment_group_disc_total = fields.Monetary(string='Treatment Group Disc. Total', store=True, readonly=True,
                                                 compute='_compute_insurance_total',
                                                 track_visibility='always')

    @api.multi
    def invoice_validate(self):
        if self.insurance_company and self.insurance_total > 0:
            invoice_line_ids = self.invoice_line_ids
            invoice_vals = {}
            invoice_line_vals = []
            insurance_company = self.insurance_company
            # Creating invoice lines
            # get account id for products
            jr_brw = self.env['account.journal'].search([('type', '=', 'sale'), ('name', '=', 'Customer Invoices')])
            for each in invoice_line_ids:
                each_line = [0, False]
                product_dict = {}
                product_dict['product_id'] = each.product_id.id
                product_dict['amt_paid_by_patient'] = 0
                product_dict['discount_amt'] = 0
                product_dict['name'] = each.name
                product_dict['quantity'] = each.quantity
                product_dict['price_unit'] = (each.price_unit * each.amt_paid_by_insurance) / 100
                acc_obj = self.env['account.account'].search([('name', '=', 'Local Sales'),
                                                              ('user_type_id', '=', 'Income')], limit=1)
                for account_id in jr_brw:
                    product_dict[
                        'account_id'] = account_id.default_debit_account_id.id if account_id.default_debit_account_id else acc_obj.id
                each_line.append(product_dict)
                invoice_line_vals.append(each_line)
                # Creating invoice dictionary
            invoice_vals['account_id'] = insurance_company.property_account_receivable_id.id
            invoice_vals['partner_id'] = insurance_company.id
            invoice_vals['dentist'] = self.dentist.id
            if self.patient:
                invoice_vals['patient'] = self.patient.id
            invoice_vals['is_insurance_company'] = True
            if self.appt_id.id:
                invoice_vals['appt_id'] = self.appt_id.id
            invoice_vals['insurance_company'] = False
            invoice_vals['invoice_line_ids'] = invoice_line_vals
            if invoice_vals:
                inv_id = self.env['account.invoice'].create(invoice_vals)
                inv_id.action_invoice_open()
                self.write({'insurance_invoice': inv_id.id})
        return super(AccountInvoice, self).invoice_validate()

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_subtotal', 'invoice_line_ids.amt_paid_by_insurance')
    def _compute_insurance_total(self):
        for record in self:
            if record.insurance_company:
                ins_total = 0
                treatment_total = 0
                for line in record.invoice_line_ids:
                    treatment_total += (line.price_unit * line.quantity * line.discount_amt) / 100
                    ins_total += (line.price_unit * line.quantity * line.amt_paid_by_insurance) / 100
                record.insurance_total = ins_total
                record.treatment_group_disc_total = treatment_total

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        if self.is_patient:
            return self.env.ref('pragtech_dental_management.report_patient_invoice_pdf').report_action(self)
        else:
            return self.env.ref('account.account_invoices').report_action(self)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    amt_paid_by_patient = fields.Float('Co-payment(%)', default=100)
    amt_paid_by_insurance = fields.Float('By Insurance Company(%)', compute='onchange_amt')
    amt_by_insurance = fields.Float('Amount By Insurance Company(%)', compute='onchange_amt')
    discount_amt = fields.Float('Treatment Group Discount(%)')
    apply_insurance = fields.Boolean('Apply Insurance?', compute='_apply_insurance', store=True)

    @api.one
    @api.depends('invoice_id.partner_id', 'invoice_id.insurance_company', 'product_id')
    def _apply_insurance(self):
        if self.invoice_id.insurance_company:
            treatment_companies = [ins_company.id for ins_company in self.product_id.insurance_company_ids]
            patient_companies = [insurance.company_id.id for insurance in self.partner_id.insurance_ids]
            self.apply_insurance = True if self.invoice_id.insurance_company.id in patient_companies and self.invoice_id.insurance_company.id in treatment_companies else False
        else:
            self.apply_insurance = False

    @api.one
    @api.depends('amt_paid_by_patient', 'amt_paid_by_insurance', 'discount_amt', 'invoice_id.insurance_company',
                 'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)

        """patient have to pay only copayment (defined in insurance company) percent amount"""
        treatment_companies = [ins_company.id for ins_company in self.product_id.insurance_company_ids]
        patient_companies = [insurance.company_id.id for insurance in self.partner_id.insurance_ids]
        if self.invoice_id.insurance_company.id in treatment_companies and self.invoice_id.insurance_company.id in patient_companies:
            self.price_subtotal = price_subtotal_signed = taxes[
                'total_excluded'] if taxes else self.quantity * price * (
            1 - (100 - self.amt_paid_by_patient or 0.0) / 100.0)
        else:
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price

        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    @api.onchange('amt_paid_by_patient', 'discount_amt')
    @api.depends('amt_paid_by_patient', 'amt_paid_by_insurance', 'discount_amt')
    def onchange_amt(self):
        for this in self:
            if this.apply_insurance:
                if 100 - (this.amt_paid_by_patient + this.discount_amt) < 0:
                    raise Warning('Please enter valid amount')
                this.amt_paid_by_insurance = 100 - (this.amt_paid_by_patient + this.discount_amt)

    @api.model
    def create(self, vals):
        if vals.get('amt_paid_by_insurance') and vals.get('amt_paid_by_patient') + vals.get('discount_amt'):
            if vals.get('apply_insurance') and vals.get('amt_paid_by_insurance') and vals.get(
                    'amt_paid_by_patient') and vals.get('discount_amt') != 100:
                raise Warning('Cumulative percentage should be 100')
        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(AccountInvoiceLine, self).write(vals)
        if self.amt_paid_by_insurance + self.amt_paid_by_patient + self.discount_amt != 100 and self.apply_insurance:
            raise Warning('Cumulative percentage should be 100')
        return res
