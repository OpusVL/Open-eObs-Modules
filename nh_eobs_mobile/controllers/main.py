# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""
Defines helper methods and handlers for eObs Mobile.
"""
import logging
from datetime import datetime

import jinja2
import openerp
import os
from openerp import http
from openerp.addons.nh_eobs_api.controllers.route_api import route_manager
from openerp.addons.nh_eobs_api.routing import Route as EobsRoute
from openerp.addons.nh_eobs_mobile.controllers import urls
from openerp.http import request
from openerp.modules.module import get_module_path
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF, safe_eval
from werkzeug import exceptions
from werkzeug import utils

from openerp.addons.nh_observations import frequencies

_logger = logging.getLogger(__name__)

URL_PREFIX = '/mobile/'
URLS = urls.URLS


db_list = http.db_list

db_monodb = http.db_monodb

loader = jinja2.FileSystemLoader(get_module_path('nh_eobs_mobile') + '/views/')
env = jinja2.Environment(loader=loader)
single_patient = EobsRoute(
    'single_patient',
    '/patient/<patient_id>',
    methods=['GET'],
    url_prefix='/mobile'
)
escalations = EobsRoute(
    'escalations',
    '/escalations/',
    methods=['GET'],
    url_prefix='/mobile'
)
all_patients = EobsRoute(
    'all_patients',
    '/all_patients/',
    methods=['GET'],
    url_prefix='/mobile'
)
patient_list = EobsRoute(
    'patient_list',
    '/patients/',
    methods=['GET'],
    url_prefix='/mobile'
)
task_list = EobsRoute(
    'task_list',
    '/tasks/',
    methods=['GET'],
    url_prefix='/mobile'
)
single_task = EobsRoute(
    'single_task',
    '/task/<task_id>',
    methods=['GET'],
    url_prefix='/mobile'
)
route_manager.add_route(single_patient)
route_manager.add_route(patient_list)
route_manager.add_route(single_task)
route_manager.add_route(task_list)
route_manager.add_route(all_patients)


def abort_and_redirect(url):
    """
    Aborts and redirects to ``url``.
    :param url: URL
    :type url: str
    :returns: `302 Found` status code and redirection to ``url``
    """

    r = request.httprequest
    response = utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    exceptions.abort(response)


def ensure_db(redirect=URLS['login']):
    """
    Used by client when a :meth:`http.route()<openerp.http.route>` has
    authentication method parameter as "none" (``auth='none'``) and if
    the route is dependent on a database.
    If no database is found, it will redirect to URL assigned to
    ``redirect`` parameter.
    If database name is from a query parameter, it will be checked by
    :meth:`http.db_filter()<openerp.http.db_filter>` thus to avoid
    database forgery that could lead to xss attacks.
    :param redirect: URL to redirect to
    :type redirect: str
    :returns: ``None``
    :rtype: NoneType
    """

    db = request.params.get('db')

    # Ensure "legitness" of database
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database,
        # the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but
        # with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = r.base_url
        if r.query_string:
            # Can't use werkzeug.wrappers.BaseRequest.url with encoded hashes:
            # https://github.com/amigrave/werkzeug/commit/
            # b4a62433f2f7678c234cdcac6247a869f90a7eb7
            url_redirect += '?' + r.query_string
        utils.redirect(url_redirect, 302)
        request.session.db = db
        abort_and_redirect(url_redirect)

    # if db not provided, use the session one
    if not db:
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        db = db_monodb(request.httprequest)

    # if no db can be found til here, send to the database selector
    # the database selector will redirect to database manager if needed
    if not db:
        exceptions.abort(utils.redirect(redirect, 303))

    # always switch the session to the computed db
    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db


class MobileFrontend(openerp.addons.web.controllers.main.Home):
    """
    Defines handler methods for routes defined in :mod:`urls<urls>`.
    """

    @http.route(URLS['stylesheet'], type='http', auth='none')
    def get_stylesheet(self, *args, **kw):
        """
        Returns /static/src/css/nhc.css (custom stylesheet) response
        object.
        :returns: /static/src/css/nhc.css
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/css/nhc.css'.format(
                get_module_path('nh_eobs_mobile')
        ), 'r') as stylesheet:
            return request.make_response(
                stylesheet.read(),
                headers={'Content-Type': 'text/css; charset=utf-8'})

    @http.route(URLS['manifest'], type='http', auth='none')
    def get_manifest(self, *args, **kw):
        """
        Returns /static/src/manifest.json response object.
        :returns: /static/src/manifest.json
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/manifest.json'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as manifest:
            return request.make_response(
                manifest.read(),
                headers={'Content-Type': 'application/json'})

    @http.route(URLS['small_icon'], type='http', auth='none')
    def get_small_icon(self, *args, **kw):
        """
        Returns /static/src/icon/hd_small.png response object.
        :returns: /static/src/icon/hd_small.png
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/icon/hd_small.png'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as icon:
            return request.make_response(
                icon.read(), headers={'Content-Type': 'image/png'})

    @http.route(URLS['big_icon'], type='http', auth='none')
    def get_big_icon(self, *args, **kw):
        """
        Returns /static/src/icon/hd_hi.png response object.
        :returns: /static/src/icon/hd_hi.png
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/icon/hd_hi.png'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as icon:
            return request.make_response(
                icon.read(), headers={'Content-Type': 'image/png'})

    @http.route('/mobile/src/fonts/<xmlid>', auth='none', type='http')
    def get_font(self, xmlid, *args, **kw):
        """
        Returns font-woff response object from fonts contained in
        /static/srs/font/.
        :returns: a Web Open Font Format (WOFF) font
        :rtype: :class:`http.Response<openerp.http.Response>`
        """
        mod_path = get_module_path('nh_eobs_mobile')
        font_file_request = '{0}/static/src/fonts/{1}'.format(
            mod_path, xmlid)
        # Consider only the file's name (without additional unwanted parts)
        # when checking for file's existence
        font_file_path = '{0}/static/src/fonts/{1}'.format(
            mod_path, xmlid.split('?')[0]
        )
        if isinstance(xmlid, basestring) and os.path.exists(font_file_path):
            with open(font_file_request, 'r') as font:
                return request.make_response(
                    font.read(),
                    headers={'Content-Type': 'application/font-woff'})
        else:
            exceptions.abort(404)

    @http.route(URLS['logo'], type='http', auth='none')
    def get_logo(self, *args, **kw):
        """
        Returns /static/src/img/open_eobs_logo.png response object.
        :returns: /static/src/img/open_eobs_logo.png
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/img/open_eobs_logo.png'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as logo:
            return request.make_response(
                logo.read(), headers={'Content-Type': 'image/png'})

    @http.route(URLS['bristol_stools_chart'], type='http', auth='none')
    def get_bristol_stools_chart(self, *args, **kw):
        """
        Returns /static/src/img/bristol_stools.png response object.
        :returns: /static/src/img/bristol_stools.png
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/img/bristol_stools.png'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as bsc:
            return request.make_response(
                bsc.read(), headers={'Content-Type': 'image/png'})

    @http.route(URLS['jquery'], type='http', auth='none')
    def get_jquery(self, *args, **kw):
        """
        Returns /static/src/js/jquery.js response object.
        :returns: /static/src/js/jquery.js
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/js/jquery.js'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as jquery:
            return request.make_response(
                jquery.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['observation_form_js'], type='http', auth='none')
    def get_observation_js(self, *args, **kw):
        """
        Returns /static/src/js/observation.js response object.
        :returns: /static/src/js/observation.js
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/js/observation.js'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as js:
            return request.make_response(
                js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['observation_form_validation'], type='http', auth='none')
    def get_observation_validation(self, *args, **kw):
        """
        Returns /static/src/js/validation.js response object.
        :returns: /static/src/js/validation.js
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/js/validation.js'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as js:
            return request.make_response(
                js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['graph_lib'], type='http', auth='none')
    def graph_lib(self, *args, **kw):
        """
        Returns /static/src/js/nh_graphlib.js response object.
        :returns: /static/src/js/nh_graphlib.js
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/js/nh_graphlib.js'.format(
            get_module_path('nh_graphs')
        ), 'r') as pg:
            return request.make_response(
                pg.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['patient_graph'], type='http', auth='none')
    def patient_graph_js(self, *args, **kw):
        """
        Returns /static/src/js/draw_ews_graph.js response object.
        :returns: /static/src/js/draw_ews_graph.js
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/src/js/draw_ews_graph.js'.format(
            get_module_path('nh_eobs_mobile')
        ), 'r') as js:
            return request.make_response(
                js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['data_driven_documents'], type='http', auth='none')
    def d_three(self, *args, **kw):
        """
        Returns /static/lib/js/d3.js response object.
        :returns: /static/lib/js/d3.js
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        with open('{0}/static/lib/js/d3.js'.format(
            get_module_path('nh_graphs')
        ), 'r') as js:
            return request.make_response(
                js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URL_PREFIX, type='http', auth='none')
    def index(self, *args, **kw):
        """
        Redirects :class:`user<base.res_users>` to task list if logged
        in. Otherwise the user will be redirect to login.
        :returns: :class:`Response<werkzeug.wrappers.Response>`
        :rtype: :class:`werkzeug.wrappers.Response` object
        """

        ensure_db()
        if request.session.uid:
            return utils.redirect(URLS['task_list'], 303)
        else:
            return utils.redirect(URLS['login'], 303)

    @http.route(URLS['login'], type="http", auth="none")
    def mobile_login(self, *args, **kw):
        """
        Logs a :class:`user<base.res_users>` in (HTTP POST), redirecting
        to the task list. If username or password is invalid, the login
        page response is returned with a message. For HTTP GET, the
        the login page response is returned.
        :returns: Either task list or login response objects
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        if not request.uid:
            request.uid = openerp.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None
        if 'database' in values:
            database_legit = values['database'] in values['databases']
            if database_legit:
                values['databases'] = [values['database']]
        login_template = env.get_template('login.html')

        if request.httprequest.method == 'GET':
            response = request.make_response(
                login_template.render(
                    stylesheet=URLS['stylesheet'],
                    logo=URLS['logo'],
                    form_action=URLS['login'],
                    errors='',
                    databases=values['databases']
                )
            )
            response.set_cookie(
                'session_id',
                value=request.session_id,
                max_age=3600
            )
            return response
        if request.httprequest.method == 'POST':
            # TODO: Refactor to better manage the 'card pin' use case
            card_pin = request.params.get('card_pin', None)
            if card_pin:
                nfc_api = request.registry['res.users']
                user_id = nfc_api.get_user_id_from_card_pin(
                    request.cr, request.uid, card_pin)
                user_login = nfc_api.get_user_login_from_user_id(
                    request.cr, request.uid, user_id)
                if user_id is not False:
                    request.session.db = 'nhclinical'
                    request.session.uid = user_id
                    request.session.login = user_login
                    request.session.password = user_login
                    return utils.redirect(URLS['task_list'], 303)
            database = values['database'] if 'database' in values else False
            if database:
                uid = request.session.authenticate(
                    database,
                    request.params['username'],
                    request.params['password']
                )
                if uid is not False:
                    request.uid = uid
                    return utils.redirect(URLS['task_list'], 303)
            response = request.make_response(
                login_template.render(
                    stylesheet=URLS['stylesheet'],
                    logo=URLS['logo'],
                    form_action=URLS['login'],
                    errors='<div class="alert alert-error">'
                           'Invalid username/password</div>',
                    databases=values['databases']
                )
            )
            response.set_cookie(
                'session_id',
                value=request.session_id,
                max_age=3600
            )
            return response

    @http.route(URLS['logout'], type='http', auth="user")
    def mobile_logout(self, *args, **kw):
        """
        Logs a :class:`user<base.res_users>` out, returning them to the
        login page.
        :returns: login page response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        api = request.registry['nh.eobs.api']
        api.unassign_my_activities(request.cr, request.session.uid)
        request.session.logout(keep_db=True)
        return utils.redirect(URLS['login'], 303)

    @staticmethod
    def calculate_ews_class(score):
        """
        Returns the :class:`EWS<nh_clinical_patient_observation_ews>`
        class.
        :param score: EWS score
        :type score: str
        :returns: EWS class
        :rtype: str
        """

        if score == 'None':
            return 'level-none'
        elif score == 'Low':
            return 'level-one'
        elif score == 'Medium':
            return 'level-two'
        elif score == 'High':
            return 'level-three'
        else:
            return 'level-none'

    def process_patient_list(self, cr, uid, patient_list, context=None):
        for patient in patient_list:
            patient['url'] = '{0}{1}'.format(
                URLS['single_patient'], patient['id'])
            patient['color'] = self.calculate_ews_class(
                patient['clinical_risk'])
            patient['trend_icon'] = 'icon-{0}-arrow'.format(
                patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['bg_deadline_time'] = patient['next_bg_time'] \
                if patient['next_bg_time'] else ''
            patient['summary'] = patient.get('summary', False)
            if patient.get('followers'):
                followers = patient['followers']
                follow_csv = ', '.join([f['name'] for f in followers])
                patient['followers'] = follow_csv
                patient['follower_ids'] = [f['id'] for f in followers]
            if patient.get('invited_users'):
                users = patient['invited_users']
                invite_csv = ', '.join([u['name'] for u in users])
                patient['invited_users'] = invite_csv
        return patient_list

    @staticmethod
    def process_form_fields(form_desc):
        """
        Process the form fields and set them up for rendering

        :param form_desc: A list of form field dicts from get_form_description
        :return: tuple of list of processed form inputs and form dictionary
        """
        form = {}
        for form_input in form_desc:
            if form_input['type'] in ['float', 'integer']:
                input_type = form_input['type']
                form_input['step'] = 0.1 if input_type is 'float' else 1
                form_input['type'] = 'number'
                form_input['number'] = True
                form_input['info'] = form_input.get('info', '')
                form_input['errors'] = form_input.get('errors', '')
                form_input['min'] = str(form_input['min'])
            elif form_input['type'] == 'selection':
                form_input['selection_options'] = []
                form_input['info'] = form_input.get('info', '')
                form_input['errors'] = form_input.get('errors', '')
                for option in form_input['selection']:
                    opt = dict()
                    opt['value'] = '{0}'.format(option[0])
                    opt['label'] = option[1]
                    form_input['selection_options'].append(opt)
            elif form_input['type'] == 'text':
                form_input['info'] = form_input.get('info', '')
                form_input['errors'] = form_input.get('errors', '')
            elif form_input['type'] == 'meta':
                score = 'score' in form_input
                input_score = form_input['score']
                form['obs_needs_score'] = input_score if score else False
                partial_flow = form_input.get('partial_flow')
                if partial_flow:
                    form['partial_flow'] = partial_flow
        return form_desc, form

    @http.route(URLS['patient_list'], type='http', auth="user")
    def get_patients(self, *args, **kw):
        """
        Returns the patient task list for patients.
        :returns: patient task list response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        cr, uid, context = request.cr, request.session.uid, request.context
        patient_api = request.registry['nh.eobs.api']
        patient_api.unassign_my_activities(cr, uid)
        follow_activities = patient_api.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context
        )
        patients = self.process_patient_list(
            cr, uid, patient_api.get_patients(
                cr, uid, [], context=context), context=context)
        # JC says this concept is now deprecated
        # patient_api.get_patient_followers(cr, uid, patients, context=context)
        following_patients = self.process_patient_list(
            cr, uid, patient_api.get_followed_patients(
                cr, uid, []), context=context)

        for patient in patients:
            if patient.get('frequency'):
                patient['frequency_string'] = self._convert_frequency_to_string(
                    patient.get('frequency')
                )
            if patient.get('bg_frequency'):
                patient['bg_frequency_string'] = self._convert_frequency_to_string(
                    patient.get('bg_frequency')
                )

        favourites = self.get_user_favourites(uid)
        return request.render(
            'nh_eobs_mobile.patient_task_list',
            qcontext={
                'favourites': favourites,
                'notifications': follow_activities,
                'items': patients,
                'notification_count': len(follow_activities),
                'followed_items': following_patients,
                'section': 'patient',
                'username': request.session['login'],
                'urls': URLS}
        )

    @staticmethod
    def _convert_frequency_to_string(frequency):
        return '{:2d} hour(s) {:02d} min(s)'.format(*divmod(frequency, 60))

    @http.route(URLS['escalations'] + '<creator_id>', type='http', auth='user')
    def process_escalations(self, creator_id, *args, **kwargs):
        """
        The route loaded once the observation has been confirmed. Prepares values for the escalation tasks form
        :param creator_id: The id of the activity that started the chain of escalation tasks
        :param args:
        :param kwargs:
        :return: The escalations form view
        """
        cr, uid, context = request.cr, request.session.uid, request.context
        obj_nh_activity = request.registry['nh.activity']
        obj_nh_eobs_api = request.registry('nh.eobs.api')

        cancel_reasons = obj_nh_eobs_api.get_cancel_reasons(cr, uid, context=context)
        activities = obj_nh_activity.search(cr, uid, [('creator_id', '=', int(creator_id))])
        data = {
            "tasks": [],
            "patient": {},
            "cancel_reasons": cancel_reasons
        }
        for activity in activities:
            activity_detail = obj_nh_activity.browse(cr, uid, activity, context=context)
            if str(activity_detail.data_model) in ['nh.clinical.patient.observation.ews', 'nh.clinical.patient.observation.blood_glucose']:
                data['patient']['name'] = activity_detail.patient_id.full_name
                data['patient']['patient_id'] = activity_detail.patient_id.id
            else:
                data['tasks'].append(
                    {
                        "task_name": activity_detail.display_name,
                        "task_model": str(activity_detail.data_model),
                        "task_parent": str(activity_detail.creator_id.data_model),
                        "frequency": self._get_ews_frequency(
                            activity_detail.creator_id
                        ),
                        "bg_frequency": self._get_bg_frequency(
                            activity_detail.creator_id
                        ),
                        "activity_id": activity_detail.id,
                        "task_id": activity_detail.data_ref.id,
                        "input_fields": self._get_input_field(cr, uid, str(activity_detail.data_model), context=context),
                    }
                )

        return request.render(
            'nh_eobs_mobile.escalations_form',
            qcontext={
                'urls': URLS,
                'data': data,
            }
        )

    def _get_ews_frequency(self, creator_activity):
        if creator_activity.data_model == 'nh.clinical.patient.observation.ews':
            return self._convert_frequency_to_string(
                creator_activity.data_ref.frequency
            )
        return False

    def _get_bg_frequency(self, creator_activity):
        if creator_activity.data_model == \
                'nh.clinical.patient.observation.blood_glucose':
            return self._convert_frequency_to_string(
                creator_activity.data_ref.frequency
            )
        return False

    def _get_input_field(self, cr, uid, obj, context=None):
        """
        Some escalation tasks require additional data when they are confirmed. This checks the type of task and if
        applicable returns the required field type and associated data
        :param obj: The task type (defined as the model that the task is recorded in)
        :return: dict(): A dictionary containing the type of input field required and any associated values
        """

        input_fields = list()

        if obj == 'nh.clinical.notification.select_frequency':
            input_fields.extend(
                [
                    {
                        "name": obj,
                        "type": "selection",
                        "values": [
                            frequencies.EVERY_DAY,
                            frequencies.EVERY_3_DAYS,
                            frequencies.EVERY_WEEK,
                        ],
                        "label": "Frequency",
                    },
                ]
            )

        if obj == "nh.clinical.notification.frequency":
            input_fields.extend(
                [
                    {
                        "name": obj,
                        "type": "selection",
                        "values": frequencies.as_list(),
                        "label": "Notification Frequency"
                    }
                ]
            )

        return input_fields

    @staticmethod
    def _group_escalation_data(data):
        groups = []
        for key, val in data.items():
            if 'nh.clinical.notification' in key:
                cancel = [y for x, y in data.items() if val in x and 'cancel' in x]
                cancel = cancel and cancel[0] or None
                value = [y for x, y in data.items() if val in x and 'value' in x]
                value = value and value[0] or None
                groups.append({
                    'model': key,
                    'id': int(val),
                    'cancel': cancel,
                    'value': value
                })
        return groups

    @http.route(URLS['confirm_escalations'], type='http', auth='user')
    def confirm_escalations(self, *args, **kwargs):
        """
        The return route once the escalation tasks form has been confirmed (with extra
        data if applicable). Updates the state for the task activity record and adds
        any additional data to the task record.
        :param args:
        :param kwargs: The fields and values from the escalation tasks form
        :return: the 'get_tasks()' method
        """

        cr, uid, context = request.cr, request.session.uid, request.context
        obj_nh_activity = request.registry['nh.activity']
        tasks = self._group_escalation_data(kwargs)
        for task in tasks:
            obj_model = request.registry[task['model']]
            data_record = obj_model.browse(cr, uid, task['id'], context=context)
            activity = data_record.activity_id
            effective_date = activity.creator_id.effective_date_terminated
            vals = {
                'effective_date_terminated': effective_date,
            }
            if task.get('cancel'):
                vals.update({
                    'reason': task['cancel']
                })
            if 'frequency' in task['model'] and task.get('value'):
                vals.update({
                    'frequency': int(task['value'])
                })
            obj_model.submit(cr, uid, activity.id, vals, context=context)
            obj_nh_activity.complete(cr, uid, activity.id, context=context)

            # Calling complete method on the activity resets the effective date
            activity.effective_date_terminated = effective_date

            if task.get('cancel') and activity.creator_id.data_model == 'nh.clinical.patient.observation.blood_glucose':
                self._cancel_next_blood_glucose(cr, uid, obj_nh_activity, activity,
                                                context)

        if tasks:
            self._check_custom_frequency(tasks[0])

        request.registry["nh.clinical.materialized.queue"].create(cr, uid, {
            "name": "Refresh ews0",
            "view_name": "ews0"
        }, context=context)
        request.registry["nh.clinical.materialized.queue"].create(cr, uid, {
            "name": "Refresh ews0",
            "view_name": "bg0"
        }, context=context)

        return utils.redirect(URLS['task_list'], 303)

    def _check_custom_frequency(self, task_data):
        cr, uid, context = request.cr, request.session.uid, request.context
        obj_task_model = request.registry[task_data['model']]
        task = obj_task_model.browse(cr, uid, task_data['id'])
        activity = task.activity_id
        patient, spell = activity.patient_id, activity.spell_activity_id.data_ref
        if spell.custom_frequency:
            obj_nh_activity = request.registry['nh.activity']
            next_ews_activity_id = obj_nh_activity.search(cr, uid, [
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.patient.observation.ews'),
                ('patient_id', '=', patient.id)
            ], context=context)
            next_ews_activity = obj_nh_activity.browse(cr, uid, next_ews_activity_id, context=context)
            next_ews_activity.data_ref.write(
                {'frequency': spell.custom_frequency})

    @staticmethod
    def _cancel_next_blood_glucose(cr, uid, obj_nh_activity, activity, context):
        """
        Finds the scheduled Blood Glucose Observation and cancels it. This is based on
        the user selecting 'No' to the review frequency escalation task that occurs
        after a Blood Glucose observation.
        :param cr:
        :param uid:
        :param obj_nh_activity:
        :param activity:
        :param context:
        :return:
        """
        next_blood_glucose_activity_id = obj_nh_activity.search(cr, uid, [
            ('state', '=', 'scheduled'),
            ('data_model', '=', 'nh.clinical.patient.observation.blood_glucose'),
            ('patient_id', '=', activity.patient_id.id)
        ], context=context)
        obj_nh_activity.cancel(cr, uid, next_blood_glucose_activity_id, context=context)
        request.registry["nh.clinical.materialized.queue"].create(cr, uid, {
            "name": "Refresh ews0",
            "view_name": "bg0"
        }, context=context)

    @http.route(URLS['share_patient_list'], type='http', auth='user')
    def get_share_patients(self, *args, **kw):
        """
        Renders the shared patient list.
        :returns: shared patient list response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        cr, uid, context = request.cr, request.session.uid, request.context
        api = request.registry['nh.eobs.api']
        api.unassign_my_activities(cr, uid)
        patients = api.get_patients(cr, uid, [], context=context)
        # JC says this concept is now deprecated
        # api.get_patient_followers(cr, uid, patients, context=context)
        api.get_invited_users(cr, uid, patients, context=context)
        follow_activities = api.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context
        )
        self.process_patient_list(cr, uid, patients, context=context)
        sorted_pts = sorted(
            patients,
            key=lambda k: cmp(k['followers'], k['invited_users'])
        )
        return request.render(
            'nh_eobs_mobile.share_patients_list',
            qcontext={
                'items': sorted_pts,
                'section': 'patient',
                'username': request.session['login'],
                'share_list': True,
                'notification_count': len(follow_activities),
                'urls': URLS,
                'user_id': uid
            }
        )

    def process_task_list(self, cr, uid, task_list, context=None):
        """
        Process the task list from nh.eobs.api.get_activities

        :param cr: Odoo cursor
        :param uid: user id
        :param task_list: list of tasks from get_activities
        :param context: Odoo context
        :return: list of tasks with extra processing
        """
        for task in task_list:
            task['url'] = '{0}{1}'.format(URLS['single_task'], task['id'])
            task['color'] = self.calculate_ews_class(task['clinical_risk'])
        return task_list

    @http.route(URLS['task_list'], type='http', auth='user')
    def get_tasks(self, *args, **kw):
        """
        Renders the patient task list for tasks.
        :returns: task list response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """

        cr, uid, context = request.cr, request.uid, request.context
        task_api = request.registry['nh.eobs.api']
        task_api.unassign_my_activities(cr, uid)
        follow_activities = task_api.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context
        )
        # grab the patient object and get id?
        tasks = self.process_task_list(
            cr, uid, task_api.get_activities(
                cr, uid, [], context=context),
            context=context)

        for task in tasks:
            if task.get('frequency'):
                task['frequency_string'] = self._convert_frequency_to_string(
                    task.get('frequency')
                )
            if task.get('bg_frequency'):
                task['bg_frequency_string'] = self._convert_frequency_to_string(
                    task.get('bg_frequency')
                )

        favourites = self.get_user_favourites(uid)
        return request.render(
            'nh_eobs_mobile.patient_task_list',
            qcontext={
                'favourites': favourites,
                'items': tasks,
                'section': 'task',
                'username': request.session['login'],
                'notification_count': len(follow_activities),
                'urls': URLS
            }
        )

    @staticmethod
    def get_user_favourites(uid):

        user_filters = request.env['ir.filters'].search([
            ('user_id', '=', uid),
            ('model_id', '=', 'nh.clinical.wardboard'),
            ('action_id', '=', request.env['ir.model.data'].get_object_reference(
                'nh_eobs', 'action_wardboard'
            )[1])
        ])
        ward_names = []
        for user_filter in user_filters:
            domain = safe_eval(user_filter.domain)
            for elem in domain:
                if isinstance(elem, list) and elem[2] not in [ward["location"] for ward in ward_names]:
                    ward_names.append({
                        "location": str(elem[2]),
                        "default": "{is_default}".format(
                            is_default=user_filter.is_default
                        ).lower()
                    })

        return ward_names

    def get_task_form(self, cr, uid, task, patient, request, context=None):
        """
        Get the form for a task

        :param task: task object
        :return: tuple of form and form inputs
        """
        activity_model = request.registry('nh.activity')
        activity_record = activity_model.browse(cr, uid, task.get('id'))
        form_desc, form = self.process_form_fields(
            activity_record.data_ref.get_form_description(patient.get('id'))
        )
        form['action'] = \
            URLS['task_form_action'] + '{0}'.format(task.get('id'))
        # Add data model changing bit here
        model_name = task['data_model']
        form['type'] = model_name[(model_name.rindex('.') + 1):]
        form['task-id'] = task.get('id')
        form['patient-id'] = \
            int(patient['id']) if patient and patient.get('id') else False
        form['source'] = "task"
        form['start'] = datetime.now().strftime('%s')
        return form, form_desc

    @http.route(URLS['single_task']+'<task_id>', type='http', auth='user')
    def get_task(self, task_id, *args, **kw):
        """
        Returns a
        :class:`notification<notifications.nh_clinical_notification>`,
        :class:`observation<observations.nh_clinical_patient_observation>`
        or :class:`placement<operations.nh_clinical_patient_placement>`
        task. If the task is neither of these then an error is returned.
        :param task_id: id of task
        :type task_id: int
        :returns: task response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """
        # If invalid task ID redirect back to task list
        try:
            task_id = int(task_id)
        except ValueError:
            return utils.redirect(URLS['task_list'], 303)

        # Get the bits we need from the request
        cr, uid, context = request.cr, request.uid, request.context
        activity_reg = request.registry['nh.activity']
        api_reg = request.registry['nh.eobs.api']

        # Get the task object
        task = activity_reg.read(
            cr, uid, task_id,
            [
                'user_id',
                'data_model',
                'summary',
                'patient_id'
            ],
            context=context)

        task_rec = activity_reg.browse(cr, uid, task_id).data_ref

        # Get the patient object or redirect to task list if none
        patient = dict()
        if task and task.get('patient_id'):
            patient_info = api_reg.get_patients(
                cr, uid, [task['patient_id'][0]], context=context)
            if not patient_info:
                return utils.redirect(URLS['task_list'], 303)
            elif len(patient_info) > 0:
                patient_info = patient_info[0]
            patient['url'] = URLS['single_patient'] + '{0}'.format(
                patient_info['id'])
            patient['name'] = patient_info['full_name']
            patient['id'] = patient_info['id']
        else:
            return utils.redirect(URLS['task_list'], 303)

        # Unassign user from activities and assign them to this activity
        api_reg.unassign_my_activities(cr, uid)
        try:
            api_reg.assign(cr, uid, task_id, {'user_id': uid}, context=context)
        except orm.except_orm as e:
            except_message = 'Opening the task (id: {task_id}) ' \
                             'and trying to assign it to the current ' \
                             'user (id: {user_id}) raises this ' \
                             'exception: {exception}'
            exception_message = except_message.format(
                task_id=task_id,
                user_id=uid,
                exception=e
            )
            _logger.debug(exception_message)
            return utils.redirect(URLS['task_list'], 303)

        # Get follow activities for user
        follow_activities = api_reg.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context)

        is_notification = 'notification' in task['data_model']
        is_placement = 'placement' in task['data_model']
        is_observation = 'observation' in task['data_model']
        form, form_desc = \
            self.get_task_form(cr, uid, task, patient, request)
        view_desc = task_rec.get_view_description(form_desc)

        # TODO EOBS-1388: Extract adding of task valid key from controller
        task_valid = True
        if is_notification or is_placement:
            task_valid = task_rec.is_valid()
            cancellable = task_rec.is_cancellable()

            form['confirm_url'] = "{0}{1}".format(
                URLS['confirm_clinical_notification'], task_id)
            form['action'] = "{0}{1}".format(
                URLS['confirm_clinical_notification'], task_id)
            form['cancellable'] = cancellable
            if cancellable:
                form['cancel_url'] = "{0}{1}".format(
                    URLS['cancel_clinical_notification'], task_id)

            news_frequency, blood_glucose_frequency = self.get_current_frequency(
                patient
            )

            if news_frequency or blood_glucose_frequency:
                form['news_frequency_string'] = news_frequency
                form['blood_glucose_frequency_string'] = blood_glucose_frequency

        if is_notification or is_observation or is_placement:
            return request.render(
                'nh_eobs_mobile.data_input_screen',
                qcontext={
                    'name': task['summary'],
                    'view_description': view_desc,
                    'patient': patient,
                    'form': form,
                    'section': 'task',
                    'username': request.session['login'],
                    'notification_count': len(follow_activities),
                    'urls': URLS,
                    'task_valid': task_valid,
                    'cancellable': form.get('cancellable', False)
                }
            )
        else:
            return request.render(
                'nh_eobs_mobile.error',
                qcontext={
                    'error_string': 'Task is neither a notification '
                                    'nor an observation',
                    'section': 'task',
                    'username': request.session['login'],
                    'urls': URLS
                }
            )

    @staticmethod
    def get_current_frequency(patient):
        obj_nh_clinical_wardboard = request.env['nh.clinical.wardboard']
        wardboard_records = obj_nh_clinical_wardboard.search([
            ('patient_id', '=', patient.get('id')),
            ('spell_activity_id.state', '!=', 'completed')
        ])
        if len(wardboard_records) != 1:
            # TODO: Not sure if this can ever be hit so here as a placeholder
            # for now.
            pass
        return wardboard_records.frequency, wardboard_records.blood_glucose_frequency

    # TODO: eventually remove this method, it's no more used: it has
    # been replaced by method 'process_ajax_form()'
    # This method is still a valid fallback in case Javascript is disabled
    # on the client side, but
    # due to our current dependency from Javascript,
    # that is a very improbable scenario.
    @http.route(URLS['task_form_action']+'<task_id>', type="http", auth="user")
    def process_form(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        activity_api = request.registry('nh.activity')
        kw_copy = kw.copy()
        del kw_copy['taskId']
        kw_copy['date_started'] = datetime.fromtimestamp(
            int(kw_copy['startTimestamp'])).strftime(DTF)
        del kw_copy['startTimestamp']
        activity_api.submit(cr, uid, int(task_id), kw_copy, context)
        activity_api.complete(cr, uid, int(task_id), context)
        return utils.redirect(URLS['task_list'])

    @http.route(URLS['single_patient']+'<patient_id>',
                type='http',
                auth='user')
    def get_patient(self, patient_id, *args, **kw):
        """
        Renders the :class:`patient<base.nh_clinical_patient>` view.
        :returns: patient response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """
        def _is_hca():
            role = request.registry('res.users').browse(
                cr, uid, request.session.uid, context=context).role_id
            if role.id == request.env['ir.model.data'].get_object_reference(
                    'nh_clinical', 'role_nhc_hca')[1]:
                return 'True'
            return 'False'

        try:
            patient_id = int(patient_id)
        except ValueError:
            return utils.redirect(URLS['patient_list'], 303)
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        patient_list = api_pool.get_patients(
            cr, uid, [patient_id], context=context)
        if not patient_list:
            return utils.redirect(URLS['patient_list'], 303)
        elif len(patient_list) > 0:
            patient = patient_list[0]
        obs = api_pool.get_active_observations(
            cr, uid, patient_id, context=context)
        for index, ob in enumerate(obs):
            if ob['type'] == 'ews':
                obs.insert(0, obs.pop(index))
            if ob['type'] == 'gcs':
                obs.insert(1, obs.pop(index))
            if ob['type'] == 'pain':
                obs.insert(2, obs.pop(index))

        follow_activities = api_pool.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context)
        obs_data_vis_list = api_pool.get_data_visualisation_resources(
            cr, uid, context=context)
        user_group_ids = request.registry('res.users').read(
            cr, uid, uid, ['groups_id'])
        user_groups = request.registry('res.groups').read(
            cr, uid, user_group_ids.get('groups_id'), ['display_name']
        )
        user_groups = [rec.get('display_name') for rec in user_groups]
        return request.render(
            'nh_eobs_mobile.patient',
            qcontext={
                'patient': patient,
                'urls': URLS,
                'section': 'patient',
                'obs_list': obs,
                'notification_count': len(follow_activities),
                'username': request.session['login'],
                'data_vis_list': obs_data_vis_list,
                'user_groups': user_groups,
                'is_hca': _is_hca(),
            }
        )

    @http.route(URLS['patient_ob']+'<observation>/<patient_id>',
                type='http', auth='user')
    def take_patient_observation(self, observation, patient_id, *args, **kw):
        """
        Renders the
        :class:`observation<observations.nh_clinical_patient_observation>`
        entry view.
        :returns: observations entry response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        follow_activities = api_pool.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context)

        patient = dict()
        patient_info = api_pool.get_patients(
            cr, uid, [int(patient_id)], context=context)
        if not patient_info:
                exceptions.abort(404)
        elif len(patient_info) > 0:
            patient_info = patient_info[0]
        patient['url'] = URLS['single_patient'] + '{0}'.format(
            patient_info['id'])
        patient['name'] = patient_info['full_name']
        patient['id'] = patient_info['id']
        ob_model_name = \
            'nh.clinical.patient.observation.{0}'.format(observation)

        form_desc, form = self.process_form_fields(
            api_pool.get_form_description(
                cr, uid, int(patient_id),
                ob_model_name,
                context=context)
        )
        ob_rec = request.registry(ob_model_name)
        view_desc = ob_rec.new(cr, uid).get_view_description(form_desc)
        form['action'] = URLS['patient_form_action'] + '{0}/{1}'.format(
            observation, patient_id)
        form['type'] = observation
        form['task-id'] = False
        form['patient-id'] = int(patient_id)
        form['source'] = "patient"
        form['start'] = datetime.now().strftime('%s')
        observation_name_list = []
        for ob in api_pool.get_active_observations(cr, uid, patient_id):
            if ob['type'] == observation:
                observation_name_list.append(ob['name'])
        if len(observation_name_list) == 0:
            exceptions.abort(404)
        return request.render(
            'nh_eobs_mobile.data_input_screen',
            qcontext={
                'view_description': view_desc,
                'name': observation_name_list[0],
                'patient': patient,
                'form': form,
                'section': 'patient',
                'notification_count': len(follow_activities),
                'username': request.session['login'],
                'urls': URLS,
                'task_valid': True
            }
        )
