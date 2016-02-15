from openerp import fields, models,api,_
from openerp.exceptions import ValidationError

class wiz_emp_away_history(models.TransientModel):
    
    _name = 'wiz.emp.away.history'
    
    employee_id = fields.Many2one('hr.employee','Employee')
    exp_date_from = fields.Date('Expected Date From')
    exp_date_to = fields.Date('Expected Date To')
    reason_id=fields.Many2one('emp.away.reason','Reason')
    all_employee=fields.Boolean('All Employee',default=False)
    
    @api.multi
    def generate_history(self):
        cr,uid,context = self.env.args
        context = dict(context)
        emp_rec=[]
        history_obj=self.env['emp.away.history']
        
        for rec in self:
            if rec.exp_date_to < rec.exp_date_from:
                    raise ValidationError('Expected Date To must be Higher than Expected Date From !')

            if context.get('default_all_employee',False):
                emp_rec=self.env['hr.employee'].search([('id','in',context.get('active_ids',False))])
            else:
                emp_rec=self.env['hr.employee'].search([('id','=',rec.employee_id.id)])
            if emp_rec and len(emp_rec)==1:
                vals={'emp_id':emp_rec.id,'exp_date_from':rec.exp_date_from,
                      'exp_date_to':rec.exp_date_to,'reason_id':rec.reason_id.id}
                history_obj.create(vals)
            elif emp_rec:
                for emp in emp_rec:
                    vals={'emp_id':emp.id,'exp_date_from':rec.exp_date_from,
                      'exp_date_to':rec.exp_date_to,'reason_id':rec.reason_id.id}
                    history_obj.create(vals)