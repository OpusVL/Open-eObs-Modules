# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime

import openerp
from openerp import http
from openerp.addons.nh_eobs_api.routing import ResponseJSON
from openerp.addons.nh_eobs_api.routing import Route
from openerp.addons.nh_eobs_api.routing import RouteManager
from openerp.http import request
from openerp.modules.module import get_module_path
from openerp.osv import osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from werkzeug import exceptions

_logger = logging.getLogger(__name__)


# Create the RouteManager and the Route objects for the tests
route_manager = RouteManager(url_prefix='/api/v1')
route_list = [
    Route('json_share_patients', '/staff/assign/', methods=['POST']),
    Route('json_claim_patients', '/staff/unassign/', methods=['POST']),
    Route('json_colleagues_list', '/staff/colleagues/'),
    Route('json_invite_patients', '/staff/invite/<activity_id>/'),
    Route('json_accept_patients', '/staff/accept/<activity_id>/',
          methods=['POST']),
    Route('json_reject_patients', '/staff/reject/<activity_id>/',
          methods=['POST']),

    Route('json_take_task', '/tasks/take_ajax/<task_id>/', methods=['POST']),
    Route('json_cancel_take_task', '/tasks/cancel_take_ajax/<task_id>/',
          methods=['POST']),
    Route('json_task_form_action',
          '/tasks/submit_ajax/<observation>/<task_id>/', methods=['POST']),
    Route('confirm_clinical_notification',
          '/tasks/confirm_clinical/<task_id>/', methods=['POST']),
    Route('cancel_clinical_notification',
          '/tasks/cancel_clinical/<task_id>/', methods=['POST']),
    Route('confirm_review_frequency',
          '/tasks/confirm_review_frequency/<task_id>/', methods=['POST']),
    Route('confirm_bed_placement',
          '/tasks/confirm_bed_placement/<task_id>/', methods=['POST']),
    Route('ajax_task_cancellation_options', '/tasks/cancel_reasons/'),

    Route('json_patient_info', '/patient/info/<patient_id>/'),
    Route('json_patient_barcode', '/patient/barcode/<hospital_number>/'),
    Route(
        'ajax_get_patient_obs', '/patient/ajax_obs/<obs_type>/<patient_id>/'),
    Route('json_patient_form_action',
          '/patient/submit_ajax/<observation>/<patient_id>/',
          methods=['POST']),
    Route('escalations', '/escalations/', methods=['POST']),
    Route('confim_escalations', '/escalations/submit/', methods=['POST']),

    Route('calculate_obs_score',
          '/observation/score/<observation>/', methods=['POST']),

    Route('json_partial_reasons', '/<observation>/partial_reasons/'),
    Route('routes', '/routes/')
]

# Add ALL the routes into the Route Manager
for r in route_list:
    route_manager.add_route(r)


class NH_API(openerp.addons.web.controllers.main.Home):

    @http.route(**route_manager.expose_route('routes'))
    def get_js_routes(self, *args, **kw):
        name_of_template = 'routes_template.js'
        path_to_template = get_module_path('nh_eobs_api') + '/views/'
        # override the RouteManager's base url only for JS routes
        base_url = request.httprequest.host_url[:-1]
        routes = route_manager.get_javascript_routes(
            name_of_template, path_to_template,
            additional_context={'base_url': base_url,
                                'base_prefix': route_manager.URL_PREFIX})
        return request.make_response(
            routes, headers={'Content-Type': 'application/javascript'})

    @http.route(**route_manager.expose_route('json_share_patients'))
    def share_patients(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        user_api = request.registry['res.users']
        kw_copy = kw.copy() if kw else {}
        user_ids = [int(usid) for usid in kw_copy['user_ids'].split(',')]
        patient_ids = [int(pid) for pid in kw_copy['patient_ids'].split(',')]
        users = user_api.read(cr, uid, user_ids, ['display_name'],
                              context=context)
        for user_id in user_ids:
            api.follow_invite(cr, uid, patient_ids, user_id, context=context)
        reason = 'An invite has been sent to follow the selected patients.'
        response_data = {
            'reason': reason,
            'shared_with': [user['display_name'] for user in users]
        }
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Invitation sent',
            description='An invite has been sent to follow '
                        'the selected patients to: ',
            data=response_data)
        return request.make_response(response_json,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_claim_patients'))
    def claim_patients(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        kw_copy = kw.copy() if kw else {}
        patient_ids = [int(pid) for pid in kw_copy['patient_ids'].split(',')]
        api.remove_followers(cr, uid, patient_ids, context=context)
        response_data = {'reason': 'Followers removed successfully.'}
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Patients claimed',
            description='Followers removed successfully',
            data=response_data)
        return request.make_response(response_json,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_colleagues_list'))
    def get_colleagues(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        colleagues = api.get_share_users(cr, uid, context=context)
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Colleagues on shift',
            description='Choose colleagues for stand-in',
            data={'colleagues': colleagues})
        return request.make_response(response_json,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_invite_patients'))
    def get_shared_patients(self, *args, **kw):
        activity_id = kw.get('activity_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        activities = api.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context)
        res = []
        for a in activities:
            if a['id'] == int(activity_id):
                res = api.get_patients(cr, uid, a['patient_ids'],
                                       context=context)
                break
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Patients shared with you',
            description='These patients have been shared for you to follow',
            data=res)
        return request.make_response(response_json,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_accept_patients'))
    def accept_shared_patients(self, *args, **kw):
        activity_id = kw.get('activity_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        activities = api.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context)
        res = {}
        for a in activities:
            if a['id'] == int(activity_id):
                res = a
                res['status'] = True
                break
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Successfully accepted stand-in invite',
            description='You are following {0} patient(s) from {1}'.format(
                res['count'], res['user']),
            data=res)
        try:
            api.complete(cr, uid, int(activity_id), {}, context=context)
        except osv.except_osv:
            res = {'reason': 'Unable to complete the activity.'}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Unable to accept stand-in invite',
                description='An error occurred when trying '
                            'to accept the stand-in invite',
                data=res)

        return request.make_response(response_json,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_reject_patients'))
    def reject_shared_patients(self, *args, **kw):
        activity_id = kw.get('activity_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        activities = api.get_assigned_activities(
            cr, uid,
            activity_type='nh.clinical.patient.follow',
            context=context)
        res = {}
        for a in activities:
            if a['id'] == int(activity_id):
                res = a
                res['status'] = True
                break
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Successfully rejected stand-in invite',
            description='You are not following {0} patient(s) from {1}'.format(
                res['count'], res['user']),
            data=res)
        try:
            api.cancel(cr, uid, int(activity_id), {}, context=context)
        except osv.except_osv:
            res = {'reason': 'Unable to cancel the activity.'}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Unable to reject stand-in invite',
                description='An error occurred when trying to '
                            'reject the stand-in invite',
                data=res)

        return request.make_response(response_json,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_take_task'))
    def take_task_ajax(self, *args, **kw):
        task_id = kw.get('task_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        task_id = int(task_id)
        activity_reg = request.registry['nh.activity']
        api_reg = request.registry['nh.eobs.api']
        task = activity_reg.read(cr, uid, task_id, ['user_id'],
                                 context=context)
        if task and task.get('user_id') and task['user_id'][0] != uid:
            response_data = {'reason': 'Task assigned to another user.'}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_FAIL,
                title='Unable to take task',
                description='This task is already assigned to another user',
                data=response_data)
            return request.make_response(
                response_json,
                headers=ResponseJSON.HEADER_CONTENT_TYPE)
        else:
            try:
                api_reg.assign(cr, uid, task_id, {'user_id': uid},
                               context=context)
            except osv.except_osv:
                response_data = {'reason': 'Unable to assign to user.'}
                response_json = ResponseJSON.get_json_data(
                    status=ResponseJSON.STATUS_ERROR,
                    title='Unable to take task',
                    description='An error occurred when '
                                'trying to take the task',
                    data=response_data)
                return request.make_response(
                    response_json, headers=ResponseJSON.HEADER_CONTENT_TYPE)
            response_data = {'reason': 'Task was free to take.'}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_SUCCESS,
                title='Task successfully taken',
                description='You can now perform this task',
                data=response_data)
            return request.make_response(
                response_json, headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_cancel_take_task'))
    def cancel_take_task_ajax(self, *args, **kw):
        task_id = kw.get('task_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        task_id = int(task_id)
        activity_reg = request.registry['nh.activity']
        api_reg = request.registry['nh.eobs.api']
        task = activity_reg.read(cr, uid, task_id, ['user_id'],
                                 context=context)
        if task and task.get('user_id') and task['user_id'][0] != uid:
            response_data = {'reason': "Can't cancel other user's task."}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_FAIL,
                title='Unable to release task',
                description='The task you are trying to release '
                            'is being carried out by another user',
                data=response_data)
            return request.make_response(
                response_json, headers=ResponseJSON.HEADER_CONTENT_TYPE)
        else:
            try:
                api_reg.unassign(cr, uid, task_id, context=context)
            except osv.except_osv:
                response_data = {'reason': 'Unable to unassign task.'}
                response_json = ResponseJSON.get_json_data(
                    status=ResponseJSON.STATUS_ERROR,
                    title='Unable to release task',
                    description='An error occurred when trying to '
                                'release the task back into the task pool',
                    data=response_data)
                return request.make_response(
                    response_json, headers=ResponseJSON.HEADER_CONTENT_TYPE)
            response_data = {
                'reason': 'Task was successfully unassigned from you.'
            }
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_SUCCESS,
                title='Successfully released task',
                description='The task has now been released '
                            'back into the task pool',
                data=response_data)
            return request.make_response(
                response_json, headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_task_form_action'))
    def process_ajax_form(self, *args, **kw):
        observation = kw.get('observation')  # TODO: add a check if is None (?)
        task_id = kw.get('task_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        activity_api = request.registry('nh.activity')
        ob_str = 'nh.clinical.patient.observation.'+observation
        ob_pool = request.registry(ob_str)
        converter_pool = request.registry('ir.fields.converter')
        converter = converter_pool.for_model(cr, uid, ob_pool, str,
                                             context=context)
        kw_copy = kw.copy() if kw else {}
        data_timestamp = kw_copy.get('startTimestamp', None)
        data_task_id = kw_copy.get('taskId', None)
        data_device_id = kw_copy.get('device_id', None)

        if data_timestamp is not None:
            del kw_copy['startTimestamp']
        if data_task_id is not None:
            del kw_copy['taskId']
        if task_id is not None:
            del kw_copy['task_id']
        if observation is not None:
            del kw_copy['observation']
        if data_device_id is not None:
            del kw_copy['device_id']
        for key, value in kw_copy.items():
            if not value:
                del kw_copy[key]

        converted_data = converter(kw_copy, _logger.debug)
        if data_timestamp is not None:
            converted_data['date_started'] = \
                datetime.fromtimestamp(int(data_timestamp)).strftime(DTF)
        if data_device_id is not None:
            converted_data['device_id'] = data_device_id

        api.complete(cr, uid, int(task_id), converted_data, context)
        activity = activity_api.browse(cr, uid, int(task_id))
        obs = activity.data_ref

        description = self.get_submission_message(obs)
        response_data = obs.get_submission_response_data()

        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Successfully Submitted{0} {1}'.format(
                ' Partial' if obs.is_partial else '',
                ob_pool.get_description(append_observation=True)),
            description=description,
            data=response_data)
        return request.make_response(
            response_json, headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('calculate_obs_score'))
    def calculate_obs_score(self, *args, **kw):
        observation = kw.get('observation')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        model = 'nh.clinical.patient.observation.' + observation
        converter_pool = request.registry('ir.fields.converter')
        observation_pool = request.registry(model)
        converter = converter_pool.for_model(
            cr, uid, observation_pool, str, context=context
        )
        data = kw.copy() if kw else {}
        section = 'patient'
        if 'startTimestamp' in data:
            del data['startTimestamp']
        if 'taskId' in data:
            section = 'task'
            del data['taskId']
        if observation is not None:
            del data['observation']
        if observation == 'ews':
            observation = 'news'
            for key, value in data.items():
                if not value or key not in [
                    'avpu_text',
                    'blood_pressure_systolic',
                    'body_temperature',
                    'indirect_oxymetry_spo2',
                    'oxygen_administration_flag',
                    'pulse_rate',
                    'respiration_rate'
                ]:
                    del data[key]

        # iPad submits a key as an empty string which converter doesn't like
        data = {k: v for k, v in data.items() if k}

        converted_data = converter(data, _logger.debug)

        score_dict = api_pool.get_activity_score(
            cr, uid, model, converted_data, context=context
        )
        if not score_dict:
            exceptions.abort(400)
        modal_vals = {}
        score_type = observation.upper() if observation != 'neurological' \
            else 'Coma Scale'
        # TODO: Need to add patient name in somehow
        modal_vals['title'] = 'Submit {score_type} score of {score}'.format(
            score_type=score_type,
            score=score_dict.get('score', '')
        )
        if 'clinical_risk' in score_dict:
            modal_vals['content'] = '<p><strong>' \
                                    'Clinical risk: {risk}</strong>' \
                                    '</p><p>' \
                                    'Please confirm you want to ' \
                                    'submit this score</p>'.format(
                risk=score_dict['clinical_risk'])
        else:
            modal_vals['content'] = '<p>Please confirm you want to ' \
                                    'submit this score</p>'

        response_data = {
            'score': score_dict,
            'modal_vals': modal_vals,
            'status': 3,
            'next_action': 'json_{}_form_action'.format(section)
        }
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title=modal_vals['title'],
            description=modal_vals['content'],
            data=response_data
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(**route_manager.expose_route('json_partial_reasons'))
    def get_partial_reasons(self, *args, **kw):
        observation = kw.get('observation')
        obs_pool = request.registry(
            'nh.clinical.patient.observation.{0}'.format(observation))
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Reason for partial observation',
            description='Please state reason for submitting '
                        'partial observation',
            data=obs_pool._partial_reasons
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(**route_manager.expose_route('json_patient_info'))
    def get_patient_info(self, *args, **kw):
        patient_id = kw.get('patient_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        patient_info = api_pool.get_patients(cr, uid,
                                             [int(patient_id)],
                                             context=context)
        if len(patient_info) > 0:
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_SUCCESS,
                title=patient_info[0]['full_name'],
                description='Information on {0}'.format(
                    patient_info[0]['full_name']
                ),
                data=patient_info[0]
            )
            return request.make_response(
                response_json,
                headers=ResponseJSON.HEADER_CONTENT_TYPE
            )
        else:
            response_data = {'error': 'Patient not found.'}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Patient not found',
                description='Unable to get patient with ID provided',
                data=response_data
            )
            return request.make_response(
                response_json,
                headers=ResponseJSON.HEADER_CONTENT_TYPE
            )

    @http.route(**route_manager.expose_route('json_patient_barcode'))
    def get_patient_barcode(self, *args, **kw):
        # TODO: add a check if is None (?)
        hospital_number = kw.get('hospital_number')
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        try:
            patient_info = api_pool.get_patient_info(cr, uid,
                                                     hospital_number,
                                                     context=context)
            if len(patient_info) > 0:
                response_json = ResponseJSON.get_json_data(
                    status=ResponseJSON.STATUS_SUCCESS,
                    title=patient_info[0]['full_name'],
                    description='Information on {0}'.format(
                        patient_info[0]['full_name']
                    ),
                    data=patient_info[0]
                )
            else:
                response_data = {'error': 'Patient not found.'}
                response_json = ResponseJSON.get_json_data(
                    status=ResponseJSON.STATUS_ERROR,
                    title='Patient not found',
                    description='Unable to get patient with ID provided',
                    data=response_data
                )
        except osv.except_osv:
            response_data = {'error': 'Patient not found.'}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Patient not found',
                description='Unable to get patient with ID provided',
                data=response_data
            )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(**route_manager.expose_route('confirm_clinical_notification'))
    def confirm_clinical(self, *args, **kw):
        task_id = kw.get('task_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        activity_api = request.registry('nh.activity')
        kw_copy = kw.copy() if kw else {}
        if 'taskId' in kw_copy:
            del kw_copy['taskId']
        if 'frequency' in kw_copy:
            kw_copy['frequency'] = int(kw_copy['frequency'])
        if 'location_id' in kw_copy:
            kw_copy['location_id'] = int(kw_copy['location_id'])
        # TODO: add a check if method 'complete' fails(?)
        api.complete(cr, uid, int(task_id), kw_copy)
        triggered_ids = activity_api.search(
            cr, uid,
            [['creator_id', '=', int(task_id)]]
        )
        triggered_tasks_read = activity_api.read(cr, uid, triggered_ids, [])
        triggered_tasks = []
        for trig_task in triggered_tasks_read:
            access = api.check_activity_access(cr, uid, trig_task['id'],
                                               context=context)
            is_not_ob = 'ews' not in trig_task['data_model']
            if access and is_not_ob:
                triggered_tasks.append(trig_task)
        response_data = {'related_tasks': triggered_tasks, 'status': 1}
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Submission successful',
            description='The notification was successfully submitted',
            data=response_data
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(**route_manager.expose_route('cancel_clinical_notification'))
    def cancel_clinical(self, *args, **kw):
        task_id = kw.get('task_id')  # TODO: add a check if is None (?)
        cr, uid = request.cr, request.uid
        api_pool = request.registry('nh.eobs.api')
        kw_copy = kw.copy() if kw else {}

        data_timestamp = kw_copy.get('startTimestamp', None)
        data_task_id = kw_copy.get('taskId', None)

        if data_timestamp is not None:
            del kw_copy['startTimestamp']
        if data_task_id is not None:
            del kw_copy['taskId']
        for key, value in kw_copy.items():
            if not value:
                del kw_copy[key]

        # Try to get the cancel reason and add it to the dict if successful.
        cancel_reason = kw_copy.get('reason')
        if cancel_reason:
            kw_copy['reason'] = int(cancel_reason)

        try:
            api_pool.cancel(cr, uid, int(task_id), kw_copy)
        except osv.except_osv:
            response_data = {
                'error': 'The server returned an error while trying '
                         'to cancel the task.'
            }
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Cancellation unsuccessful',
                description='Unable to cancel the notification',
                data=response_data
            )
            return request.make_response(
                response_json,
                headers=ResponseJSON.HEADER_CONTENT_TYPE
            )

        response_data = {'related_tasks': [], 'status': 4}
        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Cancellation successful',
            description='The notification was successfully cancelled',
            data=response_data
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(**route_manager.expose_route('ajax_task_cancellation_options'))
    def cancel_reasons(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')

        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Reason for cancelling task?',
            description='Please state reason for cancelling task',
            data=api_pool.get_cancel_reasons(cr, uid, context=context)
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(**route_manager.expose_route('ajax_get_patient_obs'))
    def get_patient_obs(self, *args, **kw):
        patient_id = kw.get('patient_id')  # TODO: add a check if is None (?)
        obs_type = kw.get('obs_type')
        cr, uid = request.cr, request.uid
        api_pool = request.registry('nh.eobs.api')
        patient_list = api_pool.get_patients(cr, uid, [int(patient_id)])
        if len(patient_list) > 0:
            patient = patient_list[0]
            observations = api_pool.get_activities_for_patient(
                cr, uid,
                patient_id=int(patient_id),
                activity_type=obs_type
            )
            observations.reverse()
            response_data = {
                'obs': observations,
                'obsType': obs_type
            }
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_SUCCESS,
                title='{0}'.format(patient['full_name']),
                description='Observations for {0}'.format(
                    patient['full_name']
                ),
                data=response_data
            )
        else:
            response_data = {'error': 'Data not found.'}
            response_json = ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Data not found',
                description='Unable to find data with ID and ob name provided',
                data=response_data
            )

        return request.make_response(response_json,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @http.route(**route_manager.expose_route('json_patient_form_action'))
    def process_patient_observation_form(self, *args, **kw):
        # TODO: add a check if is None (?)
        obs_model_name = kw.get('observation')
        # TODO: add a check if is None (?)
        patient_id = kw.get('patient_id')
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        activity_api = request.registry('nh.activity')
        obs_str = 'nh.clinical.patient.observation.'+obs_model_name
        observation_pool = request.registry(obs_str)
        converter_pool = request.registry('ir.fields.converter')
        converter = converter_pool.for_model(cr, uid, observation_pool,
                                             str, context=context)
        kw_copy = kw.copy() if kw else {}
        data_timestamp = kw_copy.get('startTimestamp', False)
        data_task_id = kw_copy.get('taskId', False)
        data_device_id = kw_copy.get('device_id', False)

        if data_timestamp:
            del kw_copy['startTimestamp']
        if data_task_id:
            del kw_copy['taskId']
        if obs_model_name is not None:
            del kw_copy['observation']
        if patient_id is not None:
            del kw_copy['patient_id']
        if data_device_id:
            del kw_copy['device_id']
        for key, value in kw_copy.items():
            if not value:
                del kw_copy[key]

        converted_data = converter(kw_copy, _logger.debug)
        if data_timestamp:
            converted_data['date_started'] = datetime.fromtimestamp(
                int(data_timestamp)).strftime(DTF)
        if data_device_id:
            converted_data['device_id'] = data_device_id

        vals_data = {}
        if obs_model_name == 'neurological' or obs_model_name == 'gcs':
            if 'eyes' in converted_data:
                vals_data['eyes'] = converted_data['eyes']
            if 'verbal' in converted_data:
                vals_data['verbal'] = converted_data['verbal']
            if 'motor' in converted_data:
                vals_data['motor'] = converted_data['motor']
        elif obs_model_name == 'food_fluid':
            if 'passed_urine' in converted_data:
                vals_data['passed_urine'] = converted_data['passed_urine']
            if 'bowels_open' in converted_data:
                vals_data['bowels_open'] = converted_data['bowels_open']
        else:
            vals_data = converted_data

        new_activity_id = api.create_activity_for_patient(
            cr, uid, int(patient_id), obs_model_name, vals_data=vals_data,
            context=context
        )
        api.complete(cr, uid, int(new_activity_id), converted_data, context)
        new_activity = activity_api.browse(cr, uid, new_activity_id)
        obs = new_activity.data_ref

        description = self.get_submission_message(obs)
        response_data = obs.get_submission_response_data()

        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Successfully Submitted{0} {1}'.format(
                ' Partial' if obs.is_partial else '',
                observation_pool.get_description(append_observation=True)
            ),
            description=description,
            data=response_data
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @staticmethod
    def get_submission_message(observation):
        try:
            message = observation.get_submission_message()
        except NotImplementedError:
            message = ''
        return message
