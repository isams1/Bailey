from openerp import fields, models,api,_
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,misc
import time

class employee_away_history(models.Model):
    
    _name = 'emp.away.history'
    
    @api.multi
    def set_date_from(self):
        """
        This method is used to set the Date From field based on Leave Button
        ------------------------------------------------
        """
        cr,uid,context = self.env.args
        context = dict(context)
        curr_date=time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        for rec in self:
            rec.write({'date_from':curr_date})
            emp_rec=self.env['hr.employee'].search([('id','=',rec.emp_id.id)])
            if emp_rec:
                emp_rec.write({'away':True})
        return True
    
    @api.multi
    def set_date_to(self):
        """
        This method is used to set the Date To field based on Return Button
        ------------------------------------------------
        """
        cr,uid,context = self.env.args
        context = dict(context)
        curr_date=time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        for rec in self:
            rec.write({'date_to':curr_date})
            emp_rec=self.env['hr.employee'].search([('id','=',rec.emp_id.id)])
            if emp_rec:
                emp_rec.write({'away':False})
        return True
    
    exp_date_from = fields.Date('Expected Date From')
    exp_date_to = fields.Date('Expected Date To')
    date_from = fields.Date('Date From')
    date_to=fields.Date('Date To')
    reason_id=fields.Many2one('emp.away.reason','Reason')
    emp_id=fields.Many2one('hr.employee','Employee')

class employee_away_reason(models.Model):
    
    _name = 'emp.away.reason'
    
    code=fields.Char(string='Code')
    name=fields.Char(string='Name')