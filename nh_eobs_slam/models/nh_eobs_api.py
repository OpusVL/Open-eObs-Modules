from datetime import datetime as dt, timedelta as td

from openerp import api
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NhEobsApi(orm.AbstractModel):
    """
    Override the nh.eobs.api to take into account non-nurse, non-hca users not
    seeing NEWS
    """

    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    def get_activities(self, cr, uid, ids, context=None):
        """
        Gets a list of :class:`activities<activity.nh_activity>`.

        :param cr: Odoo cursor
        :param uid: Odoo user ID
        :param ids: ids of the activities. An empty list returns all
            activities
        :type ids: list
        :param context: Odoo context
        :type context: dict
        :returns: list of dictionaries containing activities. See source
            for specific attributes returned for each activity
        :rtype: list
        """
        settings_pool = self.pool.get('nh.clinical.settings')
        users_pool = self.pool.get('res.users')

        # Get time period for list
        activity_period = settings_pool.get_setting(cr, uid, 'activity_period')
        activity_time = dt.now() + td(minutes=activity_period)

        # Get user groups
        user = users_pool.browse(cr, uid, uid)
        clinical_groups = ['NH Clinical HCA Group', 'NH Clinical Nurse Group']
        user_groups = [g.name for g in user.groups_id]
        clinical_user = any([g in clinical_groups for g in user_groups])
        doctor_user = 'NH Clinical Doctor Group' in user_groups
        # Get domain
        domain = []
        if ids:
            domain.append(('id', 'in', ids))
        else:
            if not clinical_user:
                domain.append(
                    ('data_model', 'not in',
                     ['nh.clinical.patient.observation.ews']))
            if doctor_user:
                domain.append(('data_model', 'not in',
                               ['nh.clinical.patient.placement']))
            domain += [
                ('state', 'not in', ['completed', 'cancelled']), '|',
                ('date_scheduled', '<=', activity_time.strftime(DTF)),
                ('date_deadline', '<=', activity_time.strftime(DTF)),
                ('user_ids', 'in', [uid]),
                '|', ('user_id', '=', False), ('user_id', '=', uid)
            ]

        return self.collect_activities(cr, uid, domain, context=context)

    def get_patients(self, cr, uid, ids, context=None):
        """
        Return containing every field from
        :class:`patient<base.nh_clinical_patient>` for each patients.

        :param ids: ids of the patients. If empty, then all patients are
            returned
        :type ids: list
        :returns: list of patient dictionaries
        :rtype: list
        """
        users_pool = self.pool.get('res.users')
        user = users_pool.browse(cr, uid, uid)
        clinical_groups = ['NH Clinical HCA Group', 'NH Clinical Nurse Group',
                           'NH Clinical Doctor Group']
        user_groups = [g.name for g in user.groups_id]
        clinical_user = any([g in clinical_groups for g in user_groups])
        domain = []
        if clinical_user:
            domain.append(
                ('patient_id.current_location_id.usage', '=', 'bed')
            )
        if ids:
            domain += [
                ('patient_id', 'in', ids),
                ('state', '=', 'started'),
                ('data_model', '=', 'nh.clinical.spell'),
                '|',
                ('user_ids', 'in', [uid]),  # filter user responsibility
                ('patient_id.follower_ids', 'in', [uid])
            ]
        else:
            domain += [
                ('state', '=', 'started'),
                ('data_model', '=', 'nh.clinical.spell'),
                ('user_ids', 'in', [uid]),  # filter user responsibility
            ]
        return self.collect_patients(cr, uid, domain, context=context)

    @api.model
    def get_active_observations(self, patient_id):
        """
        Provide the active observations list for SLaM as well as the order they
        will be displayed in.

        :return: list of dictionaries to render into template
        """
        active_obs = super(NhEobsApi, self).get_active_observations(patient_id)
        if active_obs:
            return [
                {
                    'type': 'ews',
                    'name': 'NEWS'
                },
                {
                    'type': 'blood_glucose',
                    'name': 'Blood Glucose'
                },
                {
                    'type': 'blood_product',
                    'name': 'Blood Product'
                },
                # {
                #     'type': 'food_fluid',
                #     'name': 'Daily Food and Fluid'
                # },
                {
                    'type': 'height',
                    'name': 'Height'
                },
                {
                    'type': 'neurological',
                    'name': 'Neurological'
                },
                {
                    'type': 'pbp',
                    'name': 'Postural Blood Pressure'
                },
                {
                    'type': 'weight',
                    'name': 'Weight'
                },
            ]
        else:
            return []
