##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp import models, api, fields

class site_master(models.Model):
    _name = 'site.master'
    _description = 'Site Master'
    
    name = fields.Char('Site Name')

class site_location(models.Model):
    _name = 'site.location'
    _description = 'Site Location'
    
    name = fields.Char('Site Location')
    site_id = fields.Many2one('site.master', string='Site Master')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: