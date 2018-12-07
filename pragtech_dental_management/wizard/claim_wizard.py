from odoo import models, fields, api
import base64
from odoo.tools.misc import xlwt
import io


class ClaimWizard(models.TransientModel):
    _name = 'dental.claim.wizard'
    
    company = fields.Many2one('res.partner',string='Insurance Company',domain="[('is_insurance_company', '=', True)]")
    to_date = fields.Date(string='To Date')
    from_date = fields.Date(string='From Date')
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),   # choose language
                                       ('get', 'get')], default='choose')  
    name = fields.Char('File Name', readonly=True)
    @api.multi
    def print_report(self):
        datas = {'active_ids': self.env.context.get('active_ids', []),
                 'form':self.read(['to_date', 'from_date'])[0],
                 }
        values=self.env.ref('pragtech_dental_management.claim_report_qweb').report_action(self, data=datas)
        return values
    
    
    @api.multi  
    def generate_backlog_excel_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Claim Report')
        print("\n\n\n\n Workbook Created",workbook)
        # Add a font format to use to highlight cells.
#         bold = workbook.add_format({'bold':True,'size': 10})
#         normal = workbook.add_format({'size': 10})
#          workbook = xlsxwriter.Workbook('/tmp/abc.xlsx')
#         ('/tmp/%s.xlsx'%self.from_date)
#         worksheet = workbook.add_worksheet()
         
        bold = xlwt.easyxf("font: bold on;")
        normal = xlwt.easyxf()
        r = 0
        c = 0
         
        data_list = []
        output_header = ['Patient Name', 'MEM ID', 'Date of Birth', 'Nationality', 'Country of Residence','Sex','Mobile','Invoice Number',
                         'Healthcare Professional', 'Healthcare Professional ID', 'Healthcare Professional Type', 'Episode Number', 'Doctor', 'Appointment Start',
                         'Appointment End', 'State', 'Treatment', 'Treatment Code', 'Treatment price', 'Treatment group discount(%)', 'Co-payment', 'Amount paid by patient']
        for item in output_header:
            worksheet.write(r, c, item, bold)
            c += 1
 
        inv_data = self.env['account.invoice'].search \
            ([('date_invoice', '>=', self.from_date), ('date_invoice', '<=', self.to_date), ('patient','!=',False)])
#         data = []
        for inv in inv_data:
#             data = []
#             data.append(inv.patient.name.name)
#             if inv.patient.name.ref:
#                 data.append(inv.patient.name.ref)
#             else:
#                 data.append('')
#             if inv.patient.dob:
#                 data.append(inv.patient.dob)
#             else:
#                 data.append('')
#             if inv.patient.nationality_id:
#                 data.append(inv.patient.nationality_id.name)
#             else:
#                 data.append('')
#             if inv.patient.name.country_id:
#                 data.append(inv.patient.name.country_id.name)
#             else:
#                 data.append('')
#             if inv.patient.sex:
#                 if inv.patient.sex == 'm':
#                     data.append('Male')
#                 else:
#                     data.append('Female')
#             else:
#                 data.append('')
#             if inv.patient.mobile:
#                 data.append(inv.patient.mobile)
#             else:
#                 data.append('')
#             if inv.number:
#                 data.append(inv.number)
#             else:
#                 data.append('')
#             if inv.dentist:
#                 data.append(inv.dentist.name.name)
#             else:
#                 data.append('')
#             if inv.dentist.code:
#                 data.append(inv.dentist.code)
#             else:
#                 data.append('')
#             if inv.dentist.speciality:
#                 data.append(inv.dentist.speciality.name)
#             else:
#                 data.append('')
            if inv.patient.apt_id and inv.insurance_company == self.company:
                for apt in inv.patient.apt_id:
                    data = []
                    data.append(inv.patient.name.name)
                    if inv.patient.name.ref:
                        data.append(inv.patient.name.ref)
                    else:
                        data.append('')
                    if inv.patient.dob:
                        data.append(inv.patient.dob)
                    else:
                        data.append('')
                    if inv.patient.nationality_id:
                        data.append(inv.patient.nationality_id.name)
                    else:
                        data.append('')
                    if inv.patient.name.country_id:
                        data.append(inv.patient.name.country_id.name)
                    else:
                        data.append('')
                    if inv.patient.sex:
                        if inv.patient.sex == 'm':
                            data.append('Male')
                        else:
                            data.append('Female')
                    else:
                        data.append('')
                    if inv.patient.mobile:
                        data.append(inv.patient.mobile)
                    else:
                        data.append('')
                    if inv.number:
                        data.append(inv.number)
                    else:
                        data.append('')
                    if inv.dentist:
                        data.append(inv.dentist.name.name)
                    else:
                        data.append('')
                    if inv.dentist.code:
                        data.append(inv.dentist.code)
                    else:
                        data.append('')
                    if inv.dentist.speciality:
                        data.append(inv.dentist.speciality.name)
                    else:
                        data.append('')
                    if apt:
                        data.append(apt.name)
                        if apt.doctor:
                            data.append(apt.doctor.name.name)
                        else:
                            data.append(' ')
                        if apt.appointment_sdate:
                            data.append(apt.appointment_sdate)
                        else:
                            data.append(' ')
                        if apt.appointment_edate:
                            data.append(apt.appointment_edate)
                        else:
                            data.append(' ')
                        if apt.state:
                            data.append(apt.state)
                        else:
                            data.append('')
                    else:
                        data.append('')
                        data.append('')
                        data.append('')
                        data.append('')
                        data.append('')
                    if inv.invoice_line_ids:
                        product =[]
                        p_code =[]
                        for line in inv.invoice_line_ids:
                            product.append(line.product_id.name)
                            if line.product_id.default_code:
                                p_code.append(str(line.product_id.default_code))
                            else:
                                p_code.append('')
                            
                            
                            data.append(line.product_id.name or '')
                            data.append(line.product_id.default_code or '')
                            data.append(line.price_unit)
                            data.append(line.discount_amt)
                            data.append(line.amt_paid_by_patient)
                            data.append(line.price_subtotal)
                            
                            
                        if product:
                            product =','.join(product)
                        else:
                            product = ''
                        if p_code:
                            p_code =','.join(p_code)
                        else:
                            p_code = ''
#                         data.append(product)
#                         data.append(p_code)
                        
                    else:
                        data.append('')
                 
                    data_list.append(data)
        
#         print("\n\n\n\n\n",data)
#         data_list = [['1','2'],['1','GFHC'],['22','adygb']]  
        r += 1
        for data in data_list:
            c = 0
            for item in data:
                worksheet.write(r, c, item, normal)
                c += 1
            r += 1
             
             
             
        buf = io.BytesIO()
        workbook.save(buf)
        out = base64.encodestring(buf.getvalue())
        
        
#         workbook.close()
#         data = base64.b64encode(open('/tmp/abc.xlsx','rb').read())
#         self.file = data
#         self.file_name = 'demo.xlsx'
#         
#         return {
#                 'type': 'ir.actions.report.xml',
#                 'report_type': 'controller',
#                 'report_file': '/web/content/dental.claim.wizard/%s/data/%s.csv?download=true' % (self.id, 'file'),
#             }
         
        name = "claim_report.xls"
        self.write({ 'state': 'get', 'data': out, 'name': name })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dental.claim.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        