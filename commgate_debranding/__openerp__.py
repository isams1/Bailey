# -*- encoding: utf-8 -*-
##############################################################################
#
#    Point Of Sale - Product Template module for Odoo
#    Copyright (C) 2014-Today Akretion (http://www.akretion.com)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'Commgate Debranding',
    'version' : '1.1',
    'author' : 'Commgate Pte Ltd',
    'category' : 'Commgate Pte Ltd - MB',
    'description':
        """
            1. Logo to CommGate Logo
            2. Powered by CommGate
            3. My Odoo.com account
            4. About Odoo
            5. Odoo Support
            6. Odoo Title

        """,
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'account'        
    ],
    'data': [
        'view/view.xml',
        'view/res_partner.xml',
        'view/res_company.xml',
        'view/account_config_settings.xml',
        'view/base_config_settings.xml',
    ],
    'qweb': [
        'static/src/xml/debranding.xml',
    ],
}
