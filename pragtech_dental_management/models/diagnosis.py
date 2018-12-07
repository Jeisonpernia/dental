# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from mock import DEFAULT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import hashlib
import time
from odoo.exceptions import Warning
import json


class Diagnosis(models.Model):
    _name = 'diagnosis'
    _rec_name = 'code'
    
    code = fields.Char('Code', required=True)
    description = fields.Text('Description', required=True)

    @api.model
    def get_all_records(self):
        diagnosis_obj=self.env['diagnosis'].search_read([])
        return diagnosis_obj

    @api.multi
    def get_dignosis_description(self):
        return str(self.description)
