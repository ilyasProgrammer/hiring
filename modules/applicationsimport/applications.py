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

_logger = logging.getLogger("# " + __name__)
_logger.setLevel(logging.DEBUG)


class ImportJobs(models.Model):
    _name = 'importapplications'

    @api.model
    def action_load_data(self):
        applicant = self.env['hr.applicant']
        job = self.env['hr.job']
        partner = self.env['res.partner']
        source = self.env['utm.source']
        country = self.env['res.country']
        IrAttachment = self.env['ir.attachment']
        filename = '/tmp/jobs.csv'
        with open(filename, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(spamreader)
            for ind, row in enumerate(spamreader):
                # if ind == 100:
                #     break
                _logger.info("Iteration: %s", ind)
                found_job = job.search([('name', '=', row[0].strip())], limit=1)
                found_applicant = applicant.search([('name', '=', found_job.name + ' ' + row[1].strip())], limit=1)
                found_partner = partner.search([('name', '=', row[1].strip())], limit=1)
                found_source = source.search([('name', '=', row[11].strip())], limit=1)
                all = string.maketrans('', '')
                nodigs = all.translate(all, string.digits)
                salary = float(row[9].strip().translate(all, nodigs) or 0)
                if not found_partner and len(row[4].strip()):
                    found_country = country.search([('name', '=', row[4].strip())], limit=1)
                    found_partner = partner.create({'name': row[1].strip(),
                                                    'country_id': found_country.id if found_country else None,
                                                    'city': row[5].strip(),
                                                    'email': row[3].strip(),
                                                    'gender': row[2].strip().lower(),  # - Gender / field from OCA partner_contact_gender
                                                    'street': row[6].strip()})
                    _logger.info("New partner created: %s", found_partner.name)
                if not found_source and len(row[11].strip()):
                    found_source = source.create({'name': row[11].strip()})
                    _logger.info("New source created: %s", found_source.name)
                vals = {
                        'job_id': found_job.id if found_job else None,  # - Applied for / to be mapped for the "Applied Job"
                        'name':  found_job.name + ' ' + found_partner.name if found_partner else None,
                        'partner_id': found_partner.id if found_partner else None,
                        'email_from': row[3].strip(),  # - Email / to be mapped for "Contact email"
                        'availability': datetime.strptime(row[7], '%A, %d %b, %Y').strftime("%Y-%m-%d"),  # - Available to start / to be mapped for "Availability"
                        'description': row[8].strip(),  # - Short introduction / to be mapped for "Application Summary"
                        'salary_expected': salary,  # - Current salary / to be mapped for "Expected Salary"
                        'reference': row[10].strip(),  # - Did someone refer you to Vardot? / to be mapped for "Referred By"
                        'source_id': found_source.id if found_source else None,  # - How did you hear about this job? / to be mapped for "Source"
                        }
                if found_applicant:
                    found_applicant.write(vals)
                    _logger.info("Old application updated: %s", found_applicant.name)
                else:
                    try:
                        new_application = applicant.create(vals)
                        _logger.info("New application created: %s", new_application.name)
                    except:
                        _logger.error("Wrong line %s in file. Exception: %s", (ind, sys.exc_info()[0]))
                file_data = get_http_page(row[12])
                if file_data:  # - Resume / to be downloaded as file and uploaded to Odoo as attachment mapped as CV for the application.
                    file = base64.b64encode(file_data)
                    _logger.info("File downloaded: %s", row[12])
                    IrAttachment.create({
                        'name': found_partner.name,
                        'datas_fname': found_partner.name,
                        'db_datas': file,
                        'res_model': applicant._name,
                        'type': 'binary',
                        'res_id': found_applicant.id or new_application.id,
                    })


def get_http_page(url, params=None):
    # url - to load page from
    # params - dict
    if params:
        params = urllib.urlencode(params)
    request_headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "http://thewebsite.com",
        "Connection": "keep-alive"
    }
    request = urllib2.Request(url, headers=request_headers)
    contents = urllib2.urlopen(request).read()
    return contents
