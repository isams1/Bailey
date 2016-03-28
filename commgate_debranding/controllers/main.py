# -*- coding: utf-8 -*-
from openerp.addons.web.http import Controller, route, request
import simplejson
from openerp.addons.web.controllers.main import Database, module_boot
import openerp
from openerp import http
import jinja2
import sys
import os

if hasattr(sys, 'frozen'):
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader1 = jinja2.FileSystemLoader(path)
else:
    loader1 = jinja2.PackageLoader('openerp.addons.commgate_debranding', "view")

env1 = jinja2.Environment(loader=loader1, autoescape=True)
env1.filters["json"] = simplejson.dumps


class Database(Database):

    @http.route('/web/database/selector', type='http', auth="none")
    def selector(self, **kw):
        try:
            dbs = http.db_list()
            if not dbs:
                return http.local_redirect('/web/database/manager')
        except openerp.exceptions.AccessDenied:
            dbs = False
        return env1.get_template("commgate_database_selector.html").render({
            'databases': dbs,
            'debug': request.debug,
            'error': kw.get('error')
        })

    @http.route('/web/database/manager', type='http', auth="none")
    def manager(self, **kw):
        # TODO: migrate the webclient's database manager to server side views
        request.session.logout()

        return env1.get_template("commgate_database_manager.html").render({
            'modules': simplejson.dumps(module_boot()),
        })