from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, tools
import logging
import sys
import base64
import urllib2 
import ftplib

_logger = logging.getLogger(__name__)

class product_template(osv.Model):
    _inherit = "product.template"

    _columns = {
        'image_import_url': fields.char('Image Import URL'),
        'image_import_local_url': fields.char('Image Import Local URL'),
        'image_import_ftp_directory': fields.char('Image Import FTP Directory'),
        'image_import_ftp_file': fields.char('Image Import FTP FileName'),
    }

    def load(self, cr, uid, fields, data, context=None):
        data_file = []
        def handle_binary(more_data):
            data_file.append(more_data)

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
        elif 'image_import_local_url' in fields:
            index = fields.index("image_import_local_url")
            fields.append('image')
            data_image = []
            for item in data:
                try:
                    image = None
                    path_update = item[index].replace('\\','/')
                    path_update = 'file:///' + path_update
                    image = urllib2.urlopen(path_update).read()
                    if image:
                        image = base64.encodestring(image)
                    item = item + (image,)
                except urllib2.URLError as e:
                    item = item + (None,)
                    _logger.error(e)
                data_image.append(item)
            return super(product_template, self).load(cr, uid, fields, data_image, context)
        elif 'image_import_ftp_directory' in fields:
            directory_index = fields.index("image_import_ftp_directory")
            filename_index = fields.index("image_import_ftp_file")
            fields.append('image')
            data_image = []
            ftp_server = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_server')
            ftp_username = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_username')
            ftp_password = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ftp_password')
            ftp = ftplib.FTP(ftp_server) 
            ftp.login(ftp_username,ftp_password)
            is_update_path = False
            for item in data:
                try:
                    path = item[directory_index]
                    filename = item[filename_index]
                    if not is_update_path:
                        ftp.cwd(path)
                        is_update_path = True
                    local_file = open(filename, 'wb')
                    ftp.retrbinary("RETR " + filename ,callback=handle_binary)
                    data_file = "".join(data_file)
                    image = data_file
                    if image:
                        image = base64.encodestring(image)
                    item = item + (image,)
                    data_file = []
                except KeyError:
                    item = item + (None,)
                data_image.append(item)
            ftp.quit()
            return super(product_template, self).load(cr, uid, fields, data_image, context)
        return super(product_template, self).load(cr, uid, fields, data, context)