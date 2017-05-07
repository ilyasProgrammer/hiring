# -*- coding: utf-8 -*-

from openerp import api, fields, models
import logging
import csv
import base64
import sys
from datetime import datetime
import urllib
import urllib2
import string
import ntpath

_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)

#1 -ok
#2 -466
#3 -384
#4 - ok
#5 - ok
#6 - ok

class UpdateIndex(models.Model):
    _name = 'updateindex'


    @api.model
    def update_index_go(self):
        IrAttachment = self.env['ir.attachment']
        recs = IrAttachment.search([('res_model', '=', 'hr.applicant')])
        l = len(recs)
        cnt=0
        for rec in recs:
            _logger.info("Iteration ", (cnt, l))
            rec.datas = rec.db_datas
            cnt += 1
