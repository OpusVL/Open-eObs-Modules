__author__ = 'colinwren'
import openerp, re, json, jinja2, bisect, time
from openerp.addons.nh_eobs_mobile.controllers import urls
from openerp import http
from openerp.modules.module import get_module_path
from datetime import datetime
from openerp.http import request
from werkzeug import utils, exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

URL_PREFIX = '/mobile/'

class ListerFrontend(openerp.addons.nh_eobs_mobile.controllers.main.MobileFrontend):

    @http.route(URL_PREFIX + 'src/html/pupil_size_chart.html', type="http", auth="none")
    def pupil_size_chart(self, *args, **kw):
        return request.render('nh_eobs_lister.pupil_size_reference', qcontext={})