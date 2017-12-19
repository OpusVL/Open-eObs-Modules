# coding: utf-8
""" Test medium Clinical Risk """
from openerp.addons.nh_eobs_slam.tests.common import clinical_risk_common
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestMediumClinicalRisk(clinical_risk_common.MedHighClinicalRiskCase):
    """
    Test that observations with medium clinical risk work properly
    """

    def setUp(self):
        self.obs_data = clinical_risk_sample_data.MEDIUM_RISK_DATA
        self.expected_score = 5
        self.expected_risk = 'Medium'
        self.expected_freq = 60
        super(TestMediumClinicalRisk, self).setUp()
        notifications = self.activity_pool.browse(self.cr, self.uid,
                                                  self.triggered_ids)
        self.notifications = [act.data_model for act in notifications]
