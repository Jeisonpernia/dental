from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    patient_prefix = fields.Char("Patient ID Prefix", required=True, default=lambda self: _('PAC'))
    fax = fields.Char("Fax")
