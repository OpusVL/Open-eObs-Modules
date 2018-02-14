from openerp.osv import orm, fields, osv
import re
import logging
import bisect
import copy
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class nh_eobs_api(orm.AbstractModel):
    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    _active_observations = [
        {
            'type': 'ews',
            'name': 'NEWS'
        },
        {
            'type': 'height',
            'name': 'Height'
        },
        {
            'type': 'weight',
            'name': 'Weight'
        },
        {
            'type': 'blood_product',
            'name': 'Blood Product'
        },
        {
            'type': 'blood_sugar',
            'name': 'Blood Sugar'
        },
        {
            'type': 'stools',
            'name': 'Bowel Open'
        },
        {
            'type': 'gcs',
            'name': 'Glasgow Coma Scale (GCS)'
        },
        {
            'type': 'pbp',
            'name': 'Postural Blood Pressure'
        },
        {
            'type': 'pain',
            'name': 'Pain Score'
        },
        {
            'type': 'urinary_analysis',
            'name': 'Urinary Analysis'
        },
        {
            'type': 'neurovascular',
            'name': 'Neurovascular'
        },
        {
            'type': 'urine_output',
            'name': 'Urine Output'
        }
    ]


class enht_users(orm.Model):
    _inherit = 'res.users'

    def init(self, cr):
        # MIGRATION FROM NON ROLE BASED DB
        category_pool = self.pool['res.partner.category']
        hca_cat_id = category_pool.search(cr, 1, ['|', ['name', '=', 'CSW'], ['name', '=', 'HCA']])[0]
        nur_cat_id = category_pool.search(cr, 1, [['name', '=', 'Nurse']])[0]
        sco_cat_id = category_pool.search(cr, 1, ['|', ['name', '=', 'Nurse in Charge'], ['name', '=', 'Shift Coordinator']])[0]
        sma_cat_id = category_pool.search(cr, 1, [['name', '=', 'Senior Manager']])[0]
        doc_cat_id = category_pool.search(cr, 1, [['name', '=', 'Doctor']])[0]
        sdr_cat_id = category_pool.search(cr, 1, [['name', '=', 'Senior Doctor']])[0]
        jdr_cat_id = category_pool.search(cr, 1, [['name', '=', 'Junior Doctor']])[0]
        reg_cat_id = category_pool.search(cr, 1, [['name', '=', 'Registrar']])[0]
        con_cat_id = category_pool.search(cr, 1, [['name', '=', 'Consultant']])[0]
        rec_cat_id = category_pool.search(cr, 1, [['name', '=', 'Receptionist']])[0]
        adm_cat_id = category_pool.search(cr, 1, [['name', '=', 'System Administrator']])[0]
        kio_cat_id = category_pool.search(cr, 1, [['name', '=', 'Kiosk']])[0]
        roles = [hca_cat_id, nur_cat_id, sco_cat_id, sma_cat_id, doc_cat_id, sdr_cat_id, jdr_cat_id, reg_cat_id,
                 con_cat_id, rec_cat_id, adm_cat_id, kio_cat_id]
        migrate_users = self.search(cr, 1, [['category_id', 'not in', roles]])
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical HCA Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, hca_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Nurse Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, nur_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Shift Coordinator Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, sco_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Senior Manager Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, sma_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Doctor Group']],
                                       ['id', 'in', migrate_users]])
        for uid in user_ids:
            self.write(cr, 1, uid, {'category_id': [[4, doc_cat_id], [3, sdr_cat_id], [3, jdr_cat_id], [3, reg_cat_id],
                                                    [3, con_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Admin Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, adm_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Kiosk Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, kio_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Senior Doctor Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, sdr_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Junior Doctor Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, jdr_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Registrar Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, reg_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Consultant Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, con_cat_id]]})
        user_ids = self.search(cr, 1, [['groups_id.name', 'in', ['NH Clinical Receptionist Group']],
                                       ['id', 'in', migrate_users]])
        self.write(cr, 1, user_ids, {'category_id': [[4, rec_cat_id]]})
        # END OF MIGRATION
        super(enht_users, self).init(cr)


class nh_clinical_patient_placement_lister(orm.Model):
    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 'type': 'recurring',
                               'cancel_others': True, 'context': 'eobs'},
                              {'model': 'nh.clinical.patient.weight_monitoring', 'type': 'complete',
                               'data': {'status': True}, 'context': 'renal'},
                              {'model': 'nh.clinical.patient.observation.height', 'type': 'schedule',
                               'cancel_others': True, 'context': 'eobs', 'domains': [
                                   {
                                       'object': 'nh.activity',
                                       'domain': [['data_model', '=', 'nh.clinical.patient.observation.height'],
                                                  ['state', '=', 'completed']]
                                   }
                               ]},
                              {'model': 'nh.clinical.patient.observation.weight', 'type': 'schedule',
                               'cancel_others': True, 'context': 'eobs', 'domains': [
                                   {
                                       'object': 'nh.activity',
                                       'domain': [['data_model', '=', 'nh.clinical.patient.observation.weight'],
                                                  ['state', '=', 'completed']]
                                   }
                               ]}]}

class nh_clinical_patient_observation_lister_ews(orm.Model):
    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    _POLICY = {'ranges': [0, 4, 6], 'case': '0123', 'frequencies': [480, 240, 60, 15],
               'notifications': [
                   [{'model': 'frequency', 'groups': ['nurse']}],
                   [{'model': 'assessment', 'minutes_due': 30, 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'assessment', 'minutes_due': 30, 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'assessment', 'minutes_due': 15, 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}]
               ],
               'risk': ['None', 'Low', 'Medium', 'High']}

    def init(self, cr):
        """
        Migrate any database pre-partial observations FIX so it ignores them for Score/Clinical Risk views.
        :return:
        """
        partial_ews_ids = self.search(cr, 1, [['is_partial', '=', True]])
        self.write(cr, 1, partial_ews_ids, {'clinical_risk': 'Unknown'})


    def calculate_o2_allowed_score(self, cr, uid, patient_id, o2value, o2flag, context=None):
        o2target_pool = self.pool['nh.clinical.patient.o2target']
        o2level_id = o2target_pool.get_last(cr, uid, patient_id, context=context)
        if not o2level_id:
            return 0
        o2level_pool = self.pool['nh.clinical.o2level']
        o2 = o2level_pool.read(cr, uid, o2level_id, ['min', 'max'], context=context)
        if o2['min'] <= o2value:
            mino2 = o2value
            score = int(self._O2_RANGES['scores'][bisect.bisect_left(self._O2_RANGES['ranges'], mino2)])
            return score+2*int(o2flag)
        else:
            return 0

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        observation_pool = self.pool['nh.clinical.patient.observation']
        blood_sugar_pool = self.pool['nh.clinical.patient.observation.blood_sugar']
        groups_pool = self.pool['res.groups']
        api_pool = self.pool['nh.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        case = 2 if activity.data_ref.three_in_one and case < 3 else case
        hcagroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False
        spell_activity_id = activity.parent_id.id
        self.handle_o2_devices(cr, uid, activity_id, context=context)

        if not activity.data_ref.is_partial:
            allowed_score = self.calculate_o2_allowed_score(cr, uid, activity.data_ref.patient_id.id,
                                                            activity.data_ref.indirect_oxymetry_spo2,
                                                            activity.data_ref.oxygen_administration_flag,
                                                            context=context)
            if activity.data_ref.score > allowed_score:
                api_pool.trigger_notifications(cr, uid, {
                    'notifications': self._POLICY['notifications'][case],
                    'parent_id': spell_activity_id,
                    'creator_id': activity_id,
                    'patient_id': activity.data_ref.patient_id.id,
                    'model': self._name,
                    'group': group
                }, context=context)

        res = observation_pool.complete(cr, uid, activity_id, context=context)

        # create next EWS
        next_activity_id = self.create_activity(cr, SUPERUSER_ID,
                             {'creator_id': activity_id, 'parent_id': spell_activity_id},
                             {'patient_id': activity.data_ref.patient_id.id}, context=context)
        if activity.data_ref.is_partial:
            activity_pool.schedule(cr, uid, next_activity_id, date_scheduled=activity.date_scheduled, context=context)
        else:
            post_surgery_pool = self.pool['nh.clinical.patient.post_surgery']
            critical_care_pool = self.pool['nh.clinical.patient.critical_care']
            ps_status = post_surgery_pool.current_status(cr, uid, activity.data_ref.patient_id.id, context=context)
            cc_status = critical_care_pool.current_status(cr, uid, activity.data_ref.patient_id.id, context=context)
            if ps_status:
                frequency = min(post_surgery_pool._ews_frequency, self._POLICY['frequencies'][case])
            elif cc_status:
                frequency = min(critical_care_pool._ews_frequency, self._POLICY['frequencies'][case])
            else:
                frequency = self._POLICY['frequencies'][case]
            api_pool.change_activity_frequency(cr, SUPERUSER_ID,
                                               activity.data_ref.patient_id.id,
                                               self._name,
                                               frequency, context=context)
        # trigger Blood Sugar
        if activity.data_ref.avpu_text != 'A' and not activity.data_ref.is_partial:
            bs_act_id = blood_sugar_pool.create_activity(cr, SUPERUSER_ID, {
                'creator_id': activity_id,
                'parent_id': spell_activity_id}, {
                'patient_id': activity.data_ref.patient_id.id}, context=context)
            activity_pool.schedule(cr, SUPERUSER_ID, bs_act_id, dt.now() + td(minutes=60), context=context)
        # self.refresh_views(cr, uid, ['ews0', 'ews1', 'ews2'], context=context)
        return res


class nh_clinical_notification_assessment(orm.Model):
    _name = 'nh.clinical.notification.assessment'
    _inherit = 'nh.clinical.notification.assessment'
    _description = 'Assess Patient'
    _notifications = [
        [],
        [{'model': 'frequency', 'groups': ['nurse']}],
        [{'model': 'inform_doctor', 'summary': 'Urgently inform medical team', 'groups': ['nurse', 'hca']},
         {'model': 'frequency', 'groups': ['nurse', 'hca']},
         {'model': 'nurse', 'summary': 'Inform CCOT if unresolved after one hour. Bleep L1663 or Q0169', 'groups': ['nurse', 'hca']}],
        [{'model': 'inform_doctor', 'summary': 'Immediately inform SPR or above', 'groups': ['nurse', 'hca']},
         {'model': 'nurse', 'summary': 'Urgent assessment by CCOT', 'groups': ['nurse', 'hca']}]
    ]

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        notification_pool = self.pool['nh.clinical.notification']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = ews_pool.get_last_case(cr, uid, activity.data_ref.patient_id.id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._notifications[case],
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id.data_ref._name,
            'group': 'nurse'
        }, context=context)
        return notification_pool.complete(cr, uid, activity_id, context=context)


class lister_wardboard(osv.Model):
    _name = "nh.clinical.wardboard"
    _inherit = "nh.clinical.wardboard"

    def _get_pbp_flag(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        pbp_pool = self.pool['nh.clinical.patient.observation.pbp']
        for wb_id in ids:
            pbp_ids = self.read(cr, uid, wb_id, ['pbp_ids'], context=context)['pbp_ids']
            res[wb_id] = any([pbp_pool.read(cr, uid, pbp_id, ['result'], context=context)['result'] == 'yes' for pbp_id in pbp_ids]) if pbp_ids else False
        return res

    def _get_data_ids_multi(self, cr, uid, ids, field_names, arg, context=None):
        res = {id: {field_name: [] for field_name in field_names} for id in ids}
        for field_name in field_names:
            model_name = self._columns[field_name].relation
            sql = """select spell_id, ids from wb_activity_data where data_model='%s' and spell_id in (%s) and state='completed'"""\
                             % (model_name, ", ".join([str(spell_id) for spell_id in ids]))
            cr.execute(sql)
            rows = cr.dictfetchall()
            for row in rows:
                res[row['spell_id']][field_name] = row['ids']
        return res

    _columns = {
        'pbp_flag': fields.function(_get_pbp_flag, type='boolean', string='PBP Flag', readonly=True),
        'urinary_analysis_ids': fields.function(_get_data_ids_multi, multi='urinary_analysis_ids', type='many2many', relation='nh.clinical.patient.observation.urinary_analysis', string='Urinary Analysis Obs'),
        'neurovascular_ids': fields.function(_get_data_ids_multi, multi='neurovascular_ids', type='many2many', relation='nh.clinical.patient.observation.neurovascular', string='Neurovascular Obs'),
        'bss_ids': fields.function(_get_data_ids_multi, multi='bss_ids', type='many2many', relation='nh.clinical.patient.observation.stools', string='Bowels Open Flag')
    }

    def wardboard_ews(self, cr, uid, ids, context={}):
        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_lister_wardboard_obs_list_form')], context=context)
        if not model_data_ids:
            pass # view doesnt exist
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context)[0]['res_id']

        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'view_id': int(view_id),
            'context': context
        }

    def write(self, cr, uid, ids, vals, context=None):
        res = super(lister_wardboard, self).write(cr, uid, ids, vals, context=context)
        activity_pool = self.pool['nh.activity']
        for wb in self.browse(cr, uid, ids, context=context):
            if 'post_surgery' in vals:
                ps_pool = self.pool['nh.clinical.patient.post_surgery']
                ps_id = ps_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'status': vals['post_surgery'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, ps_id, context=context)
            if 'critical_care' in vals:
                cc_pool = self.pool['nh.clinical.patient.critical_care']
                cc_id = cc_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'status': vals['critical_care'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, cc_id, context=context)
            if 'uotarget_vol' in vals or 'uotarget_unit' in vals:
                uotarget_pool = self.pool['nh.clinical.patient.uotarget']
                current = uotarget_pool.current_target(cr, uid, wb.spell_activity_id.patient_id.id, context=context)
                if not current:
                    if not vals.get('uotarget_vol') or not vals.get('uotarget_unit'):
                        raise osv.except_osv('Urine Output Target Submission Error!', 'Both Volume and Unit are required')
                uotarget_id = uotarget_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'volume': vals.get('uotarget_vol') if vals.get('uotarget_vol') else current[0],
                    'unit': vals.get('uotarget_unit') if vals.get('uotarget_unit') else current[1]
                }, context=context)
                activity_pool.complete(cr, uid, uotarget_id, context=context)
        return res


class nh_lister_ward_dashboard(orm.Model):  # avoid the views being dropped by wardboard on initialization
    _name = 'nh.eobs.ward.dashboard'
    _inherit = 'nh.eobs.ward.dashboard'

    def view_high_risk(self, cr, uid, ids, context=None):
        wdb = self.browse(cr, uid, ids[0], context=context)
        context.update({'search_default_group_by_ward': 1, 'search_default_high_risk': 1,
                        'search_default_ward_id': wdb.id})

        return {
            'name': 'Acuity Board',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'view_type': 'form',
            'view_mode': 'tree,form,kanban',
            'domain': [('spell_state', '=', 'started'), ('location_id.usage', '=', 'bed')],
            'target': 'current',
            'context': context
        }


class nh_clinical_notification_inform_doctor(orm.Model):
    _name = 'nh.clinical.notification.inform_doctor'
    _inherit = ['nh.clinical.notification']
    _description = 'Inform Medical Team?'
    _notifications = [{'model': 'doctor_assessment', 'groups': ['nurse']}]

    def is_bleep(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        pattern = "^[0-9]{4,6}$"
        for data in record:
            if re.match(pattern, data.bleep):
                return True
            else:
                return False
        return {}

    _columns = {
        'doctor_name': fields.char('Informed Doctor', size=200),
        'bleep': fields.char('BLEEP', size=10)
    }
    _constraints = [(is_bleep, 'Error: Invalid BLEEP', ['bleep']), ]

    _form_description = [
        {
            'name': 'doctor_name',
            'type': 'text',
            'label': 'Informed Doctor',
            'initially_hidden': False
        },
        {
            'name': 'bleep',
            'type': 'text',
            'label': 'BLEEP',
            'initially_hidden': False,
            'regex': '^[0-9]{4,6}$',
            'secondary_label': '4-6 Digit BLEEP number'
        }
    ]

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._notifications,
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id._name,
            'group': 'nurse'
        }, context=context)
        return super(nh_clinical_notification_inform_doctor, self).complete(cr, uid, activity_id, context=context)

    def is_cancellable(self, cr, uid, context=None):
        return True


class lister_notification_frequency(orm.Model):
    _name = 'nh.clinical.notification.frequency'
    _inherit = 'nh.clinical.notification.frequency'
    _description = 'Review Frequency'
    _notifications = [{'model': 'inform_doctor', 'groups': ['nurse']}]

    def get_form_description(self, cr, uid, patient_id, context=None):
        frequencies = [(15, 'Every 15 Minutes'), (30, 'Every 30 Minutes'), (60, 'Every Hour'), (120, 'Every 2 Hours'),
                       (240, 'Every 4 Hours'), (360, 'Every 6 Hours'), (480, 'Every 8 Hours')]
        flist = copy.deepcopy(frequencies)
        fd = copy.deepcopy(self._form_description)
        activity_pool = self.pool['nh.activity']
        ews_ids = activity_pool.search(cr, uid, [['patient_id', '=', patient_id],
                                                 ['parent_id.state', '=', 'started'],
                                                 ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                 ['state', '=', 'scheduled']], order='sequence desc', context=context)
        if ews_ids:
            f = activity_pool.browse(cr, uid, ews_ids[0], context=context).data_ref.frequency
            for tuple in frequencies:
                if tuple[0] > f:
                    flist.remove(tuple)
        for field in fd:
            if field['name'] == 'frequency':
                field['selection'] = flist
        return fd


class lister_patient_observation_gcs(orm.Model):
    _name = 'nh.clinical.patient.observation.gcs'
    _inherit = 'nh.clinical.patient.observation.gcs'

    _pupil_sizes = [
        ['8', '8mm'],
        ['7', '7mm'],
        ['6', '6mm'],
        ['5', '5mm'],
        ['4', '4mm'],
        ['3', '3mm'],
        ['2', '2mm'],
        ['1', '1mm'],
    ]

    _columns = {
        'pupil_right_size': fields.selection(_pupil_sizes, 'Right Pupil Size'),
        'pupil_left_size': fields.selection(_pupil_sizes, 'Left Pupil Size'),
        'pupil_right_reaction': fields.selection([['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']], 'Right Pupil Reaction'),
        'pupil_left_reaction': fields.selection([['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']], 'Left Pupil Reaction')
    }

    def get_form_description(self, cr, uid, patient_id, context=None):
        fd = list(self._form_description)
        fd.append({
            'name': 'pupil_right_size',
            'type': 'selection',
            'label': 'Right Pupil Size',
            'selection': self._pupil_sizes,
            'selection_type': 'text',
            'initially_hidden': False
        })
        fd.append({
            'name': 'pupil_right_reaction',
            'type': 'selection',
            'label': 'Right Pupil Reaction',
            'selection': [['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']],
            'selection_type': 'text',
            'initially_hidden': False,
        })
        fd.append({
            'name': 'pupil_left_size',
            'type': 'selection',
            'label': 'Left Pupil Size (mm)',
            'selection': self._pupil_sizes,
            'selection_type': 'text',
            'initially_hidden': False
        })
        fd.append({
            'name': 'pupil_left_reaction',
            'type': 'selection',
            'label': 'Left Pupil Reaction',
            'selection': [['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']],
            'selection_type': 'text',
            'initially_hidden': False,
        })
        return fd

class nh_clinical_user_management(orm.Model):
    _name = "nh.clinical.user.management"
    _inherit = "nh.clinical.user.management"
    _ward_ids_not_editable = ['Nurse', 'CSW', 'Student Nurse']


class lister_overdue_view(orm.Model):
    _name = 'nh.clinical.overdue'
    _inherit = 'nh.clinical.overdue'

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res = super(lister_overdue_view, self).read(cr, uid, ids, fields, context, load)
        if not isinstance(res, list):
            res = [res]
        for r in res:
            if r.get('groups'):
                if r.get('groups') == 'HCA':
                    r['groups'] = 'CSW'
                elif r.get('groups') == 'HCA, Nurse':
                    r['groups'] = 'CSW, Nurse'
        return res


class lister_observation_stools(orm.Model):
    _name = 'nh.clinical.patient.observation.stools'
    _inherit = 'nh.clinical.patient.observation.stools'
    _required = ['bowel_open']
    _description = 'Bowel Open Parameter'

    _form_description = [
        {
            'name': 'bowel_open',
            'type': 'selection',
            'label': 'Bowel Open',
            'selection': [[True, 'Yes'], [False, 'No']],
            'initially_hidden': False
        }
    ]
