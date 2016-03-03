from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, tools
import logging
import sys
import base64
import urllib2 

_logger = logging.getLogger(__name__)


class product_template(osv.Model):
    _inherit = "product.template"

    _columns = {
        'image_import_url': fields.char('Image Import URL'),
    }

    def load(self, cr, uid, fields, data, context=None):
        if 'image_import_url' in fields:
            index = fields.index("image_import_url")
            fields.append('image')
            data_image = []
            for item in data:
                try:
                    image = None
                    image = urllib2.urlopen(item[index]).read()
                    if image:
                        image = base64.encodestring(image)
                    item = item + (image,)
                except urllib2.URLError as e:
                    item = item + (None,)
                    _logger.error(e)
                data_image.append(item)
            return super(product_template, self).load(cr, uid, fields, data_image, context)
        
        return super(product_template, self).load(cr, uid, fields, data, context)