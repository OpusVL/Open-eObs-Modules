# coding: utf-8
from \
    openerp.addons.nh_eobs_slam.tests.nh_clinical_patient_observation_ews \
    import test_low_risk


class TestAssessmentNotification(test_low_risk.TestLowClinicalRisk):
    """ Test that after a low clinical risk that the assessment works """

    def setUp(self):
        super(TestAssessmentNotification, self).setUp()
        self.api_pool.complete(self.cr, self.user_id, self.triggered_ids[0],
                               {})
        domain = [
            ('creator_id', '=', self.triggered_ids[0]),
            ('state', 'not in', ['completed', 'cancelled'])]
        self.triggered_not_ids = self.activity_pool.search(self.cr, self.uid,
                                                           domain)

    def test_two_notificiations(self):
        """ Test the correct number of notifications generated """
        self.assertEqual(len(self.triggered_not_ids), 1,
                         msg='Not exactly 2 notification triggered')

    def test_shift_notification(self):
        """ Test that a shift coordinator notification is generated """
        activity = self.activity_pool.browse(self.cr, self.uid,
                                             self.triggered_not_ids[0])
        self.assertEqual(activity.data_model,
                         'nh.clinical.notification.shift_coordinator',
                         msg="Wrong notification triggered")
