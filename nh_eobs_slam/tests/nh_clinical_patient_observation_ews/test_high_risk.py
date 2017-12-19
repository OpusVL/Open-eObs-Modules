# coding: utf-8
""" Test high Clinical Risk """
from openerp.addons.nh_eobs_slam.tests.common import clinical_risk_common
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestHighClinicalRisk(clinical_risk_common.MedHighClinicalRiskCase):
    """
    Test that observations with high clinical risk work properly
    """

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.HIGH_RISK_DATA
        self.expected_score = 10
        self.expected_risk = 'High'
        self.expected_freq = 30
        super(TestHighClinicalRisk, self).setUp()
        notifications = self.activity_pool.browse(self.cr, self.uid,
                                                  self.triggered_ids)
        self.notifications = [act.data_model for act in notifications]
