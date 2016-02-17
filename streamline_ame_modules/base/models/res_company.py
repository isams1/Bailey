from openerp import models, fields

class res_company(models.Model):
    _inherit = "res.company"
    
    letterhead = fields.Binary("LetterHead", help="This field holds the image used as Report Header")
    letterfoot = fields.Binary("Letter Footer", help="This field holds the image used as Report Header")