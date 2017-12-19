# -*- coding: utf-8 -*-
"""
Notification overrides for SLaM configuration
 - Changes policy
 - Adds Inform Shift Coordinator notification
 - Adds Call Ambulance notification
 - Changes the triggered notifications for Assess Patient
"""

from openerp import api
from openerp.addons.nh_observations import frequencies
from openerp.osv import orm


class NHClinicalNotificationAssessment(orm.Model):
    """
    Implementation of SLaM's Assess Patient notification
    - Changes triggered notifications
    """
    _name = 'nh.clinical.notification.assessment'
    _inherit = 'nh.clinical.notification.assessment'
    _notifications = [
        {
            'model': 'shift_coordinator',
            'summary': 'Inform shift coordinator',
            'groups': ['nurse']
        }
    ]


class NHClinicalNotificationSelectFrequency(orm.Model):
    """
    Implementation of SLaM's frequency notification
    - Changes triggered notifications
    """
    _name = 'nh.clinical.notification.select_frequency'
    # TODO Without the square brackets an integrity violation error due to
    # null column value is thrown, why?
    _inherit = ['nh.clinical.notification.frequency']
    _description = 'Select Frequency'
    _notifications = [
        {
            'model': 'weekly_frequency_agreed',
            'groups': ['nurse'],
            'summary': 'Weekly frequency agreed with medical team'
        }
    ]

    _NO_RISK_FREQUENCIES = [
        frequencies.EVERY_DAY,
        frequencies.EVERY_3_DAYS,
        frequencies.EVERY_WEEK
    ]

    def complete(self, cr, uid, activity_id, context=None):
        # Sometimes `activity_id` comes through as a single element list
        # which can cause failures when passed on to `trigger_notifications()`
        if hasattr(activity_id, '__iter__'):
            activity_id = activity_id[0]

        super(NHClinicalNotificationSelectFrequency, self)\
            .complete(cr, uid, activity_id, context)

        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        group = 'nurse'
        spell_activity_id = activity.parent_id.id
        api_pool = self.pool['nh.clinical.api']

        notifications = self.get_notifications(cr, uid, activity)
        if notifications:
            api_pool.trigger_notifications(cr, uid, {
                'notifications': notifications,
                'parent_id': spell_activity_id,
                'creator_id': activity_id,
                'patient_id': activity.data_ref.patient_id.id,
                'model': self._name,
                'group': group
            }, context=context)

    def get_notifications(self, cr, uid, activity):
        """
        Gets the notifications associated with this model. They are triggered
        when the model's activity is completed.

        :return:
        """
        ews_obs_pool = self.pool['nh.clinical.patient.observation.ews']
        last_obs = ews_obs_pool\
            .get_last_obs(cr, uid, activity.patient_id.id)
        case = ews_obs_pool.get_case(last_obs)
        # Do not return any notifications when the patient's admittance date
        # or last obs is less than 7 days ago AND the acuity case is 'no risk'.
        frequency = activity.data_ref.frequency
        if case == 0 and frequency == frequencies.EVERY_WEEK[0]:
            return self._notifications

    @api.multi
    def get_form_description(self, patient_id):
        """
        Get form description showing different values depending on
        duration of patient's spell and clinical risk.

        :param patient_id: ID of the patient the form is for
        :return: List of fields for form
        """
        if not self.is_valid():
            return []

        available_frequencies = self._NO_RISK_FREQUENCIES
        # TODO Do this on __init__ instead of every time this method is called.
        notification_pool = self.pool['nh.clinical.notification.frequency']
        notification_pool.\
            set_form_description_frequencies(available_frequencies)
        return list(self._form_description)

    @api.multi
    def is_cancellable(self):
        """
        Checks if the notification is valid or not and if it isn't valid it
        can be cancelled

        :returns: If form is invalid or not
        :rtype: bool
        """
        return not self.is_valid()

    @api.multi
    def is_valid(self):
        """
        Checks the validity of the notification. If another observation has
        been completed before this Review Frequency notification has been
        completed then the notification is considered invalid

        :return: Boolean of if the notification is valid or not
        :rtype: bool
        """
        activity_model = self.env['nh.activity']
        original_ews = self.activity_id.creator_id
        ews_data_model = 'nh.clinical.patient.observation.ews'
        domain = [
            ['data_model', '=', ews_data_model],
            ['creator_id', '=', original_ews.id],
            ['state', 'in', ['completed', 'cancelled']]
        ]
        next_ews_finished = activity_model.search(domain)
        if next_ews_finished:
            if not next_ews_finished.data_ref.is_partial:
                return False
            else:
                ews_gen = self.get_child_activity(
                    activity_model, next_ews_finished, ews_data_model)
                next_full_ews = list(ews_gen)
                if next_full_ews and next_full_ews[0].state not in \
                        ['completed', 'cancelled']:
                    return True
                return False
        return True


class NHClinicalNotificationFrequency(orm.Model):

    _name = 'nh.clinical.notification.frequency'
    # TODO Without the square brackets an integrity violation error due to
    # null column value is thrown, why?
    _inherit = ['nh.clinical.notification.frequency']

    _LOW_RISK_FREQUENCIES_ADMITTED_LESS_THAN_7_DAYS_AGO = [
        frequencies.EVERY_15_MINUTES,
        frequencies.EVERY_30_MINUTES,
        frequencies.EVERY_HOUR,
        frequencies.EVERY_2_HOURS,
        frequencies.EVERY_4_HOURS,
        frequencies.EVERY_6_HOURS
    ]

    _LOW_RISK_FREQUENCIES_ADMITTED_7_DAYS_OR_MORE_AGO = [
        frequencies.EVERY_15_MINUTES,
        frequencies.EVERY_30_MINUTES,
        frequencies.EVERY_HOUR,
        frequencies.EVERY_2_HOURS,
        frequencies.EVERY_4_HOURS,
        frequencies.EVERY_6_HOURS,
        frequencies.EVERY_8_HOURS,
        frequencies.EVERY_12_HOURS,
        frequencies.EVERY_DAY,
        frequencies.EVERY_3_DAYS,
        frequencies.EVERY_WEEK
    ]

    def complete(self, cr, uid, activity_id, context=None):
        """
        :meth:`completes<activity.nh_activity.complete>` the activity
        and triggers a
        :class:`assessment<notifications.nh_clinical_notification_doctor_
        assessment>` by default.

        :returns: ``True``
        :rtype: bool
        """
        self._trigger_notifications(cr, uid, activity_id, context=context)
        return super(NHClinicalNotificationFrequency, self).complete(
            cr, uid, activity_id, context=context)

    def cancel(self, cr, uid, activity_id, context=None):
        """
        Sets activity ``state`` to `cancelled` and records the date and
        user on ``date_terminated`` and ``terminate_uid`` respectively.
        See :meth:`data model cancel<activity.nh_activity_data.cancel>`
        for full implementation.

        :param activity_id: :mod:`activity<activity.nh_activity>` id
        :type activity_id: int
        :returns: ``True``
        :rtype: bool
        """
        self._trigger_notifications(cr, uid, activity_id, context=context)
        return super(NHClinicalNotificationFrequency, self).cancel(
            cr, uid, activity_id, context=context)

    def _trigger_notifications(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']

        # TODO: trigger_notifications is also called in super but with lots
        # of conditionals that will take time to refactor without breaking
        # anything.
        # For now taking the quick and dirty route of adding another
        # trigger_notifications call here manually that does not use
        # get_notifications.
        trigger_options = {
            'notifications': self.get_slam_notifications(cr, uid, activity),
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id.data_ref._name,
            'group': 'nurse'
        }
        api_pool.trigger_notifications(
            cr, uid, trigger_options, context=context)

    def get_slam_notifications(self, cr, uid, activity):
        ews_obs_pool = self.pool['nh.clinical.patient.observation.ews']
        last_obs = ews_obs_pool \
            .get_last_obs(cr, uid, activity.patient_id.id)
        case = ews_obs_pool.get_case(last_obs)

        # Trigger a confirmation task for low risk patients with an
        # observation frequency less than daily.
        frequency = activity.data_ref.frequency
        # TODO: Should check for frequencies less than 12 hours rather than for
        # specific frequencies. If new frequencies are introduced notifications
        # will not be triggered.
        if case == 1 and frequency in [frequencies.EVERY_DAY[0],
                                       frequencies.EVERY_3_DAYS[0],
                                       frequencies.EVERY_WEEK[0]]:
            frequency_label = frequencies.get_label_for_minutes(frequency)
            return [
                {
                    'model': 'frequency_agreed',
                    'groups': ['nurse'],
                    'summary': 'Confirm \'{0}\' frequency agreed with'
                               ' Medical Team'.format(frequency_label)
                }
            ]
        else:
            return [
                {
                    'model': 'medical_team',
                    'summary': 'Inform Medical Team?',
                    'groups': ['nurse']
                }
            ]

    @api.multi
    def get_form_description(self, patient_id):
        """
        Get the fields for the Review Frequency form to display on mobile

        :param patient_id: ID of the patient the Review Frequency is for
        :type patient_id: int
        :return: A list of dictionaries representing the fields of the form
        :rtype: list
        """
        observation_pool = self.pool['nh.clinical.patient.observation.ews']

        if not self.is_valid():
            return []

        can_decrease_obs_frequency = observation_pool \
            .can_decrease_obs_frequency(self._cr, self._uid, patient_id,
                                        observation_pool.FINAL_EWS_DAYS,
                                        context=self._context)

        available_frequencies = \
            self._LOW_RISK_FREQUENCIES_ADMITTED_7_DAYS_OR_MORE_AGO \
            if can_decrease_obs_frequency \
            else self._LOW_RISK_FREQUENCIES_ADMITTED_LESS_THAN_7_DAYS_AGO

        notification_pool = self.pool['nh.clinical.notification.frequency']
        notification_pool. \
            set_form_description_frequencies(available_frequencies)
        return list(self._form_description)

    @api.multi
    def is_valid(self):
        """
        Checks the validity of the notification. If another observation has
        been completed before this Review Frequency notification has been
        completed then the notification is considered invalid

        :return: Boolean of if the notification is valid or not
        :rtype: bool
        """
        activity_model = self.env['nh.activity']
        # TODO EOBS-891: Need to make this get the original EWS dynamically,
        # otherwise future process changes will break it.
        original_ews = self.activity_id.creator_id.creator_id.creator_id
        if original_ews.data_model != 'nh.clinical.patient.observation.ews':
            raise TypeError(
                "Method makes an assumption that the 3rd parent of the "
                "notification is the original EWS but in this case it is not."
            )
        ews_data_model = 'nh.clinical.patient.observation.ews'
        domain = [
            ['data_model', '=', ews_data_model],
            ['creator_id', '=', original_ews.id],
            ['state', 'in', ['completed', 'cancelled']]
        ]
        next_ews_finished = activity_model.search(domain)
        if next_ews_finished:
            if not next_ews_finished.data_ref.is_partial:
                return False
            else:
                ews_gen = self.get_child_activity(
                    activity_model, next_ews_finished, ews_data_model)
                next_full_ews = list(ews_gen)
                if next_full_ews and next_full_ews[0].state not in \
                        ['completed', 'cancelled']:
                    return True
                return False
        return True

    @api.multi
    def is_cancellable(self):
        """
        Checks if the notification is valid or not and if it isn't valid it
        can be cancelled

        :returns: If form is invalid or not
        :rtype: bool
        """
        return not self.is_valid()


class NHClinicalNotificationWeeklyFrequencyAgreedWithMedicalTeam(orm.Model):
    """
    Implementation of SLaM's frequency notification
    - Changes triggered notifications
    """
    _name = 'nh.clinical.notification.weekly_frequency_agreed'
    # TODO Without the square brackets an integrity violation error due
    # to null column value is thrown, why?
    _inherit = ['nh.clinical.notification']
    _description = "Confirmation that a weekly observation frequency " \
                   "selected by a nurse has been agreed with the medical team."


class NHClinicalNotificationFrequencyAgreedWithMedicalTeam(orm.Model):
    """
    Implementation of SLaM's frequency notification
    - Changes triggered notifications
    """
    _name = 'nh.clinical.notification.frequency_agreed'
    # TODO Without the square brackets an integrity violation error due
    # to null column value is thrown, why?
    _inherit = ['nh.clinical.notification']
    _description = "Frequency Agreed With Medical Team?"
    _notifications = [
        {'model': 'medical_team', 'groups': ['nurse']}
    ]

    def complete(self, cr, uid, activity_id, context=None):
        # Sometimes `activity_id` comes through as a single element list
        # which can cause failures when passed on to `trigger_notifications()`
        if hasattr(activity_id, '__iter__'):
            activity_id = activity_id[0]

        super(NHClinicalNotificationFrequencyAgreedWithMedicalTeam, self)\
            .complete(cr, uid, activity_id, context)

        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        group = 'nurse'
        spell_activity_id = activity.parent_id.id
        api_pool = self.pool['nh.clinical.api']

        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._notifications,
            'parent_id': spell_activity_id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': self._name,
            'group': group
        }, context=context)


class NHClinicalNotificationShiftCoordinator(orm.Model):
    """
    Implementation of SLaM's Shift Coordinator notification
    """
    _name = 'nh.clinical.notification.shift_coordinator'
    _inherit = 'nh.clinical.notification'
    _description = "Inform Shift Coordinator?"
    _slam_notifications = [
        [],
        [
            {
                'model': 'frequency',
                'groups': ['nurse']
            }
        ],
        [
            {
                'model': 'medical_team',
                'summary': 'Urgently Inform Medical Team',
                'groups': ['hca', 'nurse']
            }
        ],
        [
            {
                'model': 'medical_team',
                'summary': 'Immediately Inform Medical Team',
                'groups': ['hca', 'nurse']
            }
        ]
    ]

    @api.model
    def get_notifications(self, activity):
        """ Override of
        :py:meth:`get_notifications`
        to ensure some notifications are created in specific situations.

        :return: notifications array
        """
        risks = ['None', 'Low', 'Medium', 'High']
        clinical_risk = activity.data_ref.get_triggering_ews_risk()
        case = risks.index(clinical_risk)
        return self._slam_notifications[case]

    def complete(self, cr, uid, activity_id, context=None):
        """
        :meth:`completes<activity.nh_activity.complete>` the activity
        and triggers a
        :class:`assessment<notifications.nh_clinical_notification_doctor_
        assessment>` by default.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)

        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self.get_notifications(cr, uid, activity),
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            # Used by nh.clinical.notification.frequency and it's subclasses
            # to search for the latest observation so that it can change the
            # the frequency of it to what has been chosen by the user.
            #
            # Currently hardcoded as a quick fix for SLaM,
            # which limits them to only changing the frequency of EWS.
            'model': 'nh.clinical.patient.observation.ews',
            'group': 'nurse'
        }, context=context)

        return super(NHClinicalNotificationShiftCoordinator, self).complete(
            cr, uid, activity_id, context=context)


class NHClinicalNotificationMedicalTeam(orm.Model):
    """
    Implementation of SLaM's Medical Team notification
    """
    _name = 'nh.clinical.notification.medical_team'
    _inherit = 'nh.clinical.notification.medical_team'
    _slam_notifications = [
        [],
        [],
        [
            {
                'model': 'ambulance',
                'summary': 'Call An Ambulance 2222/9999',
                'groups': ['hca', 'nurse']
            }
        ],
        [
            {
                'model': 'ambulance',
                'summary': 'Call An Ambulance 2222/9999',
                'groups': ['hca', 'nurse']
            }
        ]
    ]

    def get_notifications(self, cr, uid, activity):
        """ Override of
        :py:meth:`get_notifications`
        to ensure some notifications are created in specific situations.

        :return: notifications array
        """
        risks = ['None', 'Low', 'Medium', 'High']
        clinical_risk = activity.data_ref.get_triggering_ews_risk()
        case = risks.index(clinical_risk)
        return self._slam_notifications[case]

    def complete(self, cr, uid, activity_id, context=None):
        """
        :meth:`completes<activity.nh_activity.complete>` the activity
        and triggers a
        :class:`assessment<notifications.nh_clinical_notification_doctor_
        assessment>` by default.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self.get_notifications(cr, uid, activity),
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id.data_ref._name,
            'group': 'nurse'
        }, context=context)
        return super(NHClinicalNotificationMedicalTeam, self).complete(
            cr, uid, activity_id, context=context)

    def cancel(self, cr, uid, activity_id, context=None):
        """
        Sets activity ``state`` to `cancelled` and records the date and
        user on ``date_terminated`` and ``terminate_uid`` respectively.
        See :meth:`data model cancel<activity.nh_activity_data.cancel>`
        for full implementation.

        :param activity_id: :mod:`activity<activity.nh_activity>` id
        :type activity_id: int
        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self.get_notifications(cr, uid, activity),
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id.data_ref._name,
            'group': 'nurse'
        }, context=context)
        return super(NHClinicalNotificationMedicalTeam, self).cancel(
            cr, uid, activity_id, context=context
        )


class NHClinicalNotificationAmbulance(orm.Model):
    """
    Implementation of SLaM's Call Ambulance notification
    """
    _name = 'nh.clinical.notification.ambulance'
    _inherit = 'nh.clinical.notification'
    _description = "Call Ambulance?"

    def is_cancellable(self, cr, uid, context=None):
        return True
