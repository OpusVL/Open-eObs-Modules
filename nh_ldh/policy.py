from openerp.osv import orm

class nh_clinical_patient_observation_btuh_ews(orm.Model):
    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    _RR_RANGES = {'ranges': [8, 11, 20, 24], 'scores': '31023'}
    _O2_RANGES = {'ranges': [91, 93, 95], 'scores': '3210'}
    _BT_RANGES = {'ranges': [35.0, 35.999, 37.999, 38.999], 'scores': '31012'}
    _BP_RANGES = {'ranges': [79, 89, 109, 219], 'scores': '32103'}
    _PR_RANGES = {'ranges': [39, 89, 109, 129], 'scores': '30123'}
    """
    EWS policy has 4 different scenarios:
        case 0: no clinical risk
        case 1: low clinical risk
        case 2: medium clinical risk
        case 3: high clinical risk
    """
    _POLICY = {'ranges': [0, 4, 6], 'case': '0123', 'frequencies': [720, 240, 60, 30],
               'notifications': [
                   [{'model': 'frequency', 'groups': ['nurse', 'hca']}],
                   [{'model': 'assessment', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'medical_team', 'summary': 'Urgently inform medical team', 'groups': ['nurse', 'hca']},
                    {'model': 'frequency', 'groups': ['nurse', 'hca']},
                    {'model': 'nurse', 'summary': 'Consider assessment by CCOT beep 6427', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'medical_team', 'summary': 'Immediately inform medical team', 'groups': ['nurse', 'hca']},
                    {'model': 'frequency', 'groups': ['nurse', 'hca']},
                    {'model': 'nurse', 'summary': 'Urgent assessment by CCOT beep 6427', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}]
               ],
               'risk': ['None', 'Low', 'Medium', 'High']}


class nh_clinical_patient_admission(orm.Model):
    _name = 'nh.clinical.patient.admission'
    _inherit = 'nh.clinical.patient.admission'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.location_id.id'
                               }},
                              {'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'cancel_others': True,
                               'create_data': {
                                   'location_id': 'activity.data_ref.location_id.id'
                               }}]}

class nh_clinical_patient_transfer(orm.Model):
    _name = 'nh.clinical.patient.transfer'
    _inherit = 'nh.clinical.patient.transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.location_id.id'
                               },
                               'case': 1
                               }
                              , {'model': 'nh.clinical.patient.placement',
                                 'type': 'schedule',
                                 'context': 'eobs',
                                 'cancel_others': True,
                                 'create_data': {
                                    'suggested_location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.origin_loc_id.id, context=context) if "
                                       "activity.data_ref.origin_loc_id.usage != 'ward' else "
                                       "activity.data_ref.origin_loc_id.id"
                                 },
                                 'case': 2
                                 },
                              {'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'domains': [
                                   {
                                       'object': 'nh.activity',
                                       'domain': [['data_model', 'in', ['nh.clinical.patient.tci',
                                                                        'nh.clinical.adt.patient.discharge',
                                                                        'nh.clinical.patient.clerking',
                                                                        'nh.clinical.ptwr']],
                                                  ['state', 'not in', ['completed', 'cancelled']]]
                                   }
                               ],
                               'cancel_others': True,
                               'create_data': {
                                   'location_id': 'activity.data_ref.location_id.id'
                               },
                               'case': 1
                              }, {'model': 'nh.clinical.patient.tci',
                                 'type': 'schedule',
                                 'context': 'etakelist',
                                 'domains': [
                                       {
                                           'object': 'nh.activity',
                                           'domain': [['data_model', 'in', ['nh.clinical.patient.tci',
                                                                            'nh.clinical.adt.patient.discharge',
                                                                            'nh.clinical.patient.clerking',
                                                                            'nh.clinical.ptwr']],
                                                      ['state', 'not in', ['completed', 'cancelled']]]
                                       }
                                   ],
                                 'cancel_others': True,
                                 'create_data': {
                                    'location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.origin_loc_id.id, context=context) if "
                                       "activity.data_ref.origin_loc_id.usage != 'ward' else "
                                       "activity.data_ref.origin_loc_id.id"
                                 },
                                 'case': 2
                                 }]}


class nh_clinical_adt_spell_update(orm.Model):
    _name = 'nh.clinical.adt.spell.update'
    _inherit = 'nh.clinical.adt.spell.update'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.location_id.id'
                               }
                              },
                              {'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'cancel_others': False,
                               'domains': [
                                   {
                                       'object': 'nh.activity',
                                       'domain': [['data_model', 'in', ['nh.clinical.patient.tci',
                                                                        'nh.clinical.adt.patient.discharge',
                                                                        'nh.clinical.patient.clerking',
                                                                        'nh.clinical.ptwr']],
                                                  ['state', 'not in', ['completed', 'cancelled']]]
                                   }
                               ],
                               'create_data': {
                                   'location_id': 'activity.data_ref.location_id.id'
                               }
                              }]}


class nh_clinical_patient_discharge(orm.Model):
    _name = 'nh.clinical.patient.discharge'
    _inherit = 'nh.clinical.patient.discharge'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.location_id.id, context=context) if "
                                       "activity.data_ref.location_id.usage != 'ward' else "
                                       "activity.data_ref.location_id.id"
                               }
                               }]}