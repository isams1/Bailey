from openerp import models, fields
import time

class streamline_ame_project_project(models.Model):
    _name = "streamline.ame.project.project"
    
    name = fields.Char(string='Name', size=256, select=True, default=lambda *a: 'Project_' + time.strftime('%Y-%m-%d'))