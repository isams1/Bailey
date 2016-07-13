from openerp import models, fields, api
import time

class streamline_ame_project_project(models.Model):
    _name = "streamline.ame.project.project"

    name = fields.Char(string='Name', size=256, select=True, default=lambda *a: 'Project_' + time.strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, default=lambda self: self.env['res.company']._company_default_get('purchase.order'))

    _sql_constraints = [
        ('name_uniq', 'unique (company_id, name)', 'The name of the company must be unique!')
    ]