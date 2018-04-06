import json
import logging
from datetime import datetime, timedelta

import openerp.modules as addons
from openerp import http
from openerp.addons.nh_eobs_api.controllers import route_api
from openerp.addons.nh_eobs_api.routing import ResponseJSON
from openerp.api import Environment
from openerp.http import request
from openerp.osv import orm, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

_logger = logging.getLogger(__name__)


class NhEobsApiRoutes(orm.AbstractModel):
    """
    A class to change the nh_eobs_api.controllers.routes method
    """

    _name = 'nh.eobs.routes.slam'

    @http.route(
        **route_api.route_manager.expose_route('json_patient_form_action'))
    def process_patient_observation_form(self, *args, **kw):
        # TODO: add a check if is None (?)
        obs_model_name = kw.get('observation')
        # TODO: add a check if is None (?)
        patient_id = kw.get('patient_id')
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        activity_api = request.registry('nh.activity')
        obs_str = 'nh.clinical.patient.observation.' + obs_model_name
        observation_pool = request.registry(obs_str)
        converter_pool = request.registry('ir.fields.converter')
        converter = converter_pool.for_model(cr, uid, observation_pool,
                                             str, context=context)
        kw_copy = kw.copy() if kw else {}
        data_timestamp = kw_copy.get('startTimestamp', False)
        data_task_id = kw_copy.get('taskId', False)
        data_device_id = kw_copy.get('device_id', False)
        data_recorded_concerns = kw_copy.get('recorded_concerns', False)
        data_dietary_needs = kw_copy.get('dietary_needs', False)

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
        if data_recorded_concerns:
            del kw_copy['recorded_concerns']
        if data_dietary_needs:
            del kw_copy['dietary_needs']
        for key, value in kw_copy.items():
            if not value:
                del kw_copy[key]

        converted_data = converter(kw_copy, _logger.debug)
        if data_timestamp:
            converted_data['date_started'] = datetime.fromtimestamp(
                int(data_timestamp)).strftime(DTF)
        if data_device_id:
            converted_data['device_id'] = data_device_id
        if data_recorded_concerns:
            converted_data['recorded_concerns'] = \
                [[6, 0, map(int, data_recorded_concerns.split(','))]]
        if data_dietary_needs:
            converted_data['dietary_needs'] = \
                [[6, 0, map(int, data_dietary_needs.split(','))]]

        vals_data = {}
        if obs_model_name == 'neurological':
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

        if obs_model_name == "ews":

            task_tree = self._get_task_tree(uid)

            user_type = "nurse"
            current_case = self._get_case(obs)
            tasks_required = task_tree[user_type][current_case]

            task_list = [
                {
                    "escalation_task_list": True,
                }
            ]

            obj_nh_activity = self.pool['nh.activity']
            for t in tasks_required:
                self._create_associated_tasks(cr, uid, t, new_activity, new_activity_id, obj_nh_activity, task_list)

        description = self.get_submission_message(obs)
        response_data = obs.get_submission_response_data()

        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_LIST if "ews" in obs_model_name else ResponseJSON.STATUS_SUCCESS,
            title='Successfully Submitted{0} {1}'.format(
                ' Partial' if obs.is_partial else '',
                observation_pool.get_description()
            ),
            description=description,
            data=response_data
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    def _create_associated_tasks(self, cr, uid, t, new_activity, new_activity_id, obj_nh_activity, task_list):
        obj_model = self.pool[t['model']]
        activity_id = obj_nh_activity.create(cr, uid,
                                             {
                                                 "data_model": t['model'],
                                                 "state": "new",
                                                 "creator_id": int(new_activity_id),
                                                 "user_id": new_activity.user_id.id,
                                                 "parent_id": new_activity.parent_id.id,
                                                 "date_deadline": datetime.now() + timedelta(minutes=5),
                                                 # "data_ref": False,
                                                 "pos_id": new_activity.pos_id.id,
                                                 "patient_id": new_activity.patient_id.id,
                                                 "location_id": new_activity.location_id.id,
                                                 "spell_activity_id": new_activity.spell_activity_id.id,
                                             }
                                             )
        t['fields'].update({
            "activity_id": activity_id,
            "patient_id": new_activity.patient_id.id,
        })
        model_id = obj_model.create(cr, uid, t['fields'])
        obj_nh_activity.write(cr, uid, activity_id, {"data_ref": "%s,%s" % (t['model'], model_id)})
        task_list.append(
            {
                "model": t['model'],
                "activity_id": activity_id,
                "task_id": model_id
            }
        )

    def _get_case(self, obs):
        score = obs.score
        case = ""
        if 0 < score <= 4:
            case = "case_1"
        elif 5 <= score <= 6:
            case = "case_3"
        elif 7 <= score:
            case = "case_4"

        return case

    def _get_task_tree(self, uid):
        """
        A tree representation of the escalation tasks that are required depending on the the observation score.
        :param uid: the current user id
        :return: dict(): The task tree
        """

        task_tree = {
            "nurse": {
                "case_1": [
                    {
                        "model": "nh.clinical.notification.shift_coordinator",
                        "fields": {}
                    },
                    {
                        "model": "nh.clinical.notification.frequency",
                        "fields": {
                            "observation": "nh.clinical.patient.observation.ews",
                            "frequency": False
                        }
                    },
                    {
                        "model": "nh.clinical.notification.medical_team",
                        "fields": {
                            "doctor_notified": False,
                            "is_duty_doctor": False
                        }
                    }
                ],
                "case_2": [
                    {
                        "model": "nh.clinical.notification.shift_coordinator",
                        "fields": {}
                    },
                    {
                        "model": "",
                        "fields": {}
                    },
                    {
                        "model": "",
                        "fields": {}
                    }

                ],
                "case_3": [
                    {
                        "model": "nh.clinical.notification.medical_team",
                        "fields": {
                            "doctor_notified": False,
                            "is_duty_doctor": False
                        }
                    },
                    {
                        "model": "nh.clinical.notification.ambulance",
                        "fields": {}
                    }
                ],
                "case_4": [
                    {
                        "model": "nh.clinical.notification.medical_team",
                        "fields": {
                            "doctor_notified": False,
                            "is_duty_doctor": False
                        }
                    },
                    {
                        "model": "nh.clinical.notification.ambulance",
                        "fields": {}
                    }
                ]
            },
            "hca": {
                "case_1": [
                    "inform_nurse"
                ],
                "case_2": [
                    "inform_nurse"
                ],
                "case_3": [
                    "inform_nurse"
                ],
                "case_4": [
                    "inform_nurse"
                ],
            }
        }

        return task_tree

    @http.route(
        **route_api.route_manager.expose_route('json_task_form_action'))
    def process_ajax_form(self, *args, **kw):
        observation = kw.get('observation')  # TODO: add a check if is None (?)
        task_id = kw.get('task_id')  # TODO: add a check if is None (?)
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        activity_api = request.registry('nh.activity')
        ob_str = 'nh.clinical.patient.observation.' + observation
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

        task_tree = self._get_task_tree(uid)

        user_type = "nurse"
        current_case = self._get_case(obs)
        tasks_required = task_tree[user_type][current_case]

        task_list = [
            {
                "escalation_task_list": True,
            }
        ]

        obj_nh_activity = self.pool['nh.activity']
        for t in tasks_required:
            self._create_associated_tasks(cr, uid, t, activity, task_id, obj_nh_activity, task_list)

        description = self.get_submission_message(obs)
        response_data = obs.get_submission_response_data()

        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_LIST,
            title='Successfully Submitted{0} {1}'.format(
                ' Partial' if obs.is_partial else '',
                ob_pool.get_description()),
            description=description,
            data=response_data)

        return request.make_response(
            response_json, headers=ResponseJSON.HEADER_CONTENT_TYPE)

    @staticmethod
    def get_triggered_tasks(cr, uid, task_id, context=None):
        """
        Get the triggered tasks from the task ID

        :param cr: Odoo cursor
        :param uid: User ID getting the triggered tasks
        :param task_id: ID of the activity checking triggered tasks of
        :param context: Odoo context
        :return: list of triggered task dicts
        """
        env = Environment(cr, uid, {})
        api_model = env.registry('nh.clinical.api')
        activity_model = env.registry('nh.activity')
        triggered_ids = activity_model.search(
            cr, uid,
            [['creator_id', '=', int(task_id)]]
        )
        triggered_tasks_read = activity_model.read(cr, uid, triggered_ids)
        triggered_tasks = []
        for trig_task in triggered_tasks_read:
            access = api_model.check_activity_access(
                cr, uid, trig_task['id'], context=context)
            is_not_ob = 'ews' not in trig_task['data_model']
            if access and is_not_ob:
                triggered_tasks.append(trig_task)
        return triggered_tasks

    def cancel_notification(self, cr, uid, task_id, vals=None, context=None):
        """
        Cancel notification and send JSON response ready to send back to the
        frontend

        :param cr: Odoo cursor
        :param uid: User ID cancelling notification
        :param task_id: ID of the notification being cancelled
        :param vals: dictionary of values to send as part of cancel
        :param context: Odoo context
        :return: JSON string of response
        """
        if not vals:
            vals = {}
        env = Environment(cr, uid, {})
        api_pool = env.registry('nh.eobs.api')
        task_id = int(task_id)
        try:
            api_pool.cancel(cr, uid, task_id, vals)
        except osv.except_osv:
            response_data = {
                'error': 'The server returned an error while trying '
                         'to cancel the task.'
            }
            return ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Cancellation unsuccessful',
                description='Unable to cancel the notification',
                data=response_data
            )

        activity_model = env.registry('nh.activity')
        patient_name = activity_model.read(
            cr, uid, task_id, ['patient_id'])['patient_id'][1]
        description = 'All escalation tasks for <strong>{}</strong> ' \
                      'have been completed'.format(patient_name)
        triggered_tasks = self.get_triggered_tasks(
            cr, uid, task_id, context=context)
        response_data = {'related_tasks': triggered_tasks, 'status': 4}
        return ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Cancellation successful',
            description=description,
            data=response_data
        )

    def complete_notification(self, cr, uid, task_id, vals=None, context=None):
        """
        Complete notifcation and return JSON object ready to send back to
        frontend

        :param cr: Odoo Cursor
        :param uid: User doing the action
        :param task_id: ID of the notification to complete
        :param vals: dict of values to send as part of complete
        :param context: Odoo context
        :return: JSON string of response
        """
        if not vals:
            vals = {}
        task_id = int(task_id)
        env = Environment(cr, uid, {})
        api_pool = env.registry('nh.eobs.api')
        try:
            api_pool.complete(cr, uid, task_id, vals)
        except osv.except_osv:
            response_data = {
                'error': 'The server returned an error while trying '
                         'to complete the task.'
            }
            return ResponseJSON.get_json_data(
                status=ResponseJSON.STATUS_ERROR,
                title='Submission unsuccessful',
                description='Unable to complete the notification',
                data=response_data
            )
        activity_model = env.registry('nh.activity')
        activity = activity_model.read(cr, uid, task_id)
        patient_name = activity.get('patient_id')[1]
        description = 'All escalation tasks for <strong>{}</strong> ' \
                      'have been completed'.format(patient_name)
        excluded_notification_models = [
            'nh.clinical.notification.nurse',
            'nh.clinical.notification.hca'
        ]
        if activity.get('data_model') in excluded_notification_models:
            description = 'The notification was successfully submitted'
        triggered_tasks = \
            self.get_triggered_tasks(cr, uid, task_id, context=context)
        response_data = {'related_tasks': triggered_tasks, 'status': 1}
        return ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Submission successful',
            description=description,
            data=response_data
        )

    @http.route(
        **route_api.route_manager.expose_route('cancel_clinical_notification'))
    def cancel_clinical(self, *args, **kw):
        task_id = kw.get('task_id')  # TODO: add a check if is None (?)
        cr, uid = request.cr, request.uid

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
        response_json = self.cancel_notification(cr, uid, task_id, kw_copy)
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(
        **route_api.route_manager.expose_route('confirm_clinical_notification')
    )
    def confirm_clinical(self, *args, **kw):
        task_id = kw.get('task_id')
        cr, uid, context = request.cr, request.uid, request.context
        kw_copy = kw.copy() if kw else {}
        if 'taskId' in kw_copy:
            del kw_copy['taskId']
        if 'frequency' in kw_copy:
            kw_copy['frequency'] = int(kw_copy['frequency'])
        if 'location_id' in kw_copy:
            kw_copy['location_id'] = int(kw_copy['location_id'])
        response_json = self.complete_notification(
            cr, uid, task_id, kw_copy, context=context)
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @http.route(
        **route_api.route_manager.expose_route(
            'ajax_task_cancellation_options'))
    def cancel_reasons(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')

        response_json = ResponseJSON.get_json_data(
            status=ResponseJSON.STATUS_SUCCESS,
            title='Why is this action not required?',
            description='Please state the reason '
                        'why this action is not required',
            data=api_pool.get_cancel_reasons(cr, uid, context=context)
        )
        return request.make_response(
            response_json,
            headers=ResponseJSON.HEADER_CONTENT_TYPE
        )

    @staticmethod
    def get_submission_message(obs_or_notification):
        try:
            message = obs_or_notification.get_submission_message()
        except NotImplementedError:
            message = ''
        return message

    def __init__(self, pool, cr):
        loaded = addons.module.loaded
        if 'nh_eobs_slam' in loaded:
            route_api.NH_API.process_ajax_form = self.process_ajax_form
            route_api.NH_API.process_patient_observation_form = \
                self.process_patient_observation_form
            route_api.NH_API.cancel_clinical = self.cancel_clinical
            route_api.NH_API.confirm_clinical = self.confirm_clinical
            route_api.NH_API.cancel_reasons = self.cancel_reasons
        super(NhEobsApiRoutes, self).__init__(pool, cr)
