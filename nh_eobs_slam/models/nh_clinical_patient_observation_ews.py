"""
EWS Observation overrides for SLaM configuration
 - Changes policy
 - Changes the way the frequency is calculated for the next observation
 - Adds Inform Shift Coordinator notification
 - Adds Call Ambulance notification
"""
from openerp.addons.nh_observations import frequencies
from openerp.osv import orm


class NHClinicalPatientObservationSlamEws(orm.Model):
    """
    Implementation of SLaM EWS Policy
    """
    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    _POLICY = {
        'ranges': [0, 4, 6],
        'case': '0123',
        'frequencies': [720, 360, 60, 30],
        'notifications': [
            [
                {
                    'model': 'select_frequency',
                    'summary': 'Select Frequency',
                    'groups': ['hca', 'nurse']
                }
            ],
            [
                {
                    'model': 'assessment',
                    'groups': ['nurse', 'hca']
                },
                {
                    'model': 'hca',
                    'summary': 'Inform Nurse About Patient',
                    'groups': ['hca']
                },
                {
                    'model': 'nurse',
                    'summary': 'Informed About Patient Status (NEWS)?',
                    'groups': ['hca']
                }
            ],
            [
                {
                    'model': 'hca',
                    'summary': 'Inform Nurse About Patient',
                    'groups': ['hca']
                },
                {
                    'model': 'nurse',
                    'summary': 'Informed About Patient Status (NEWS)?',
                    'groups': ['hca']
                },
                {
                    'model': 'shift_coordinator',
                    'summary': 'Inform Shift Coordinator',
                    'groups': ['hca', 'nurse']
                }
            ],
            [
                {
                    'model': 'hca',
                    'summary': 'Inform Nurse About Patient',
                    'groups': ['hca']
                },
                {
                    'model': 'nurse',
                    'summary': 'Informed About Patient Status (NEWS)?',
                    'groups': ['hca']
                },
                {
                    'model': 'shift_coordinator',
                    'summary': 'Inform Shift Coordinator',
                    'groups': ['hca', 'nurse']
                }
            ]
        ],
        'risk': ['None', 'Low', 'Medium', 'High']
    }

    INITIAL_EWS_DAYS = 4
    FINAL_EWS_DAYS = 7
    PRE_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ = _POLICY['frequencies'][0]
    POST_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ = frequencies.EVERY_DAY[0]

    def init(self, cr):
        """
        Migrate any database pre-partial observations FIX so it ignores them
        for Score/Clinical Risk views.
        :return:
        """
        partial_ews_ids = self.search(cr, 1, [['is_partial', '=', True]])
        self.write(cr, 1, partial_ews_ids, {'clinical_risk': 'Unknown'})

    def get_notifications(self, cr, uid, activity):
        """ Override of
        :py:meth:`nh_clinical_patient_observation_ews.get_notifications`
        to ensure some notifications are created in specific situations.

        :return:
        """
        observation_pool = self.pool['nh.clinical.patient.observation.ews']
        case = observation_pool.get_case(activity.data_ref)
        # Do not return any notifications when the patient's admittance date
        # or last obs is less than 7 days ago AND the acuity case is 'no risk'.
        if case == 0:
            can_descrease = observation_pool.can_decrease_obs_frequency(
                cr, uid, activity.patient_id.id, self.FINAL_EWS_DAYS)
            if not can_descrease:
                return []
        return super(NHClinicalPatientObservationSlamEws, self)\
            .get_notifications(cr, uid, activity)

    def change_activity_frequency(self, cr, uid, patient_id, name, case,
                                  context=None):
        """ Override the frequency update so can do a 72 hour old spell check
        :param cr: cursor
        :param uid: user id
        :param patient_id: patient id
        :param name: Name of model to update
        :param case: the case from the policy dict, used to ensure only do the
        72 hour check when is case 0
        :param context: a context
        :return:
        """
        if case == 0:
            api_pool = self.pool['nh.clinical.api']
            can_decrease = self.can_decrease_obs_frequency(
                cr, uid, patient_id, self.INITIAL_EWS_DAYS, context=context)
            if can_decrease:
                return api_pool.change_activity_frequency(
                    cr, uid, patient_id, name,
                    self.POST_INITIAL_EWS_DAYS_NO_RISK_OBS_FREQ,
                    context=context)

        return super(NHClinicalPatientObservationSlamEws, self).\
            change_activity_frequency(cr, uid, patient_id,
                                      name, case, context=context)
