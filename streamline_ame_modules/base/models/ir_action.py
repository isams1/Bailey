from openerp import models, fields

class ir_actions_report_xml(models.Model):
    _inherit = "ir.actions.report.xml"
    
    report_type = fields.Selection([('qweb-pdf', 'PDF'),
                    ('qweb-html', 'HTML'),
                    ('controller', 'Controller'),
                    ('pdf', 'RML pdf (deprecated)'),
                    ('sxw', 'RML sxw (deprecated)'),
                    ('webkit', 'Webkit (deprecated)'),
                    ('xls', 'XLS')], 
                    'Report Type', required=True, help="HTML will open the report directly in your browser, PDF will use wkhtmltopdf to render the HTML into a PDF file and let you download it, Controller allows you to define the url of a custom controller outputting any kind of report.")