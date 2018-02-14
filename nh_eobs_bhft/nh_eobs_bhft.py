from openerp.osv import orm
import logging

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_bhft_ews(orm.Model):
    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    _POLICY = {'ranges': [0, 4, 6], 'case': '0123', 'frequencies': [720, 240, 120, 60],
               'notifications': [
                   [{'model': 'frequency', 'groups': ['nurse', 'hca']}],
                   [{'model': 'assessment', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca']},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'medical_team', 'summary': 'Urgently speak to the medical team', 'groups': ['nurse', 'hca']},
                    {'model': 'frequency', 'groups': ['nurse', 'hca']},
                    {'model': 'nurse', 'summary': 'Consider assessment by CCOT', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca']},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'medical_team', 'summary': 'Immediately speak to the medical team', 'groups': ['nurse', 'hca']},
                    {'model': 'frequency', 'groups': ['nurse', 'hca']},
                    {'model': 'nurse', 'summary': 'Urgent assessment by CCOT', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca']},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}]
               ],
               'risk': ['None', 'Low', 'Medium', 'High']}


class bhft_notification_frequency(orm.Model):
    _name = 'nh.clinical.notification.frequency'
    _inherit = 'nh.clinical.notification.frequency'

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        review_frequency = activity_pool.browse(cr, uid, activity_id, context=context)
        domain = [
            ('patient_id', '=', review_frequency.data_ref.patient_id.id),
            ('data_model', '=', review_frequency.data_ref.observation),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        obs_ids = activity_pool.search(cr, uid, domain, order='create_date desc, id desc', context=context)
        obs = activity_pool.browse(cr, uid, obs_ids[0], context=context)
        obs_pool = self.pool[review_frequency.data_ref.observation]
        obs_pool.write(cr, uid, obs.data_ref.id, {'frequency': review_frequency.data_ref.frequency}, context=context)
        return super(bhft_notification_frequency, self).complete(cr, uid, activity_id, context=context)