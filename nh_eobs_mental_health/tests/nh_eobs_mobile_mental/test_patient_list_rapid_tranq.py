from openerp.tests.common import SingleTransactionCase


class TestPatientListRapidTranq(SingleTransactionCase):
    """
    Test that the override of process patient list is working correctly
    """

    @classmethod
    def setUpClass(cls):
        super(TestPatientListRapidTranq, cls).setUpClass()
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.mobile_model = cls.registry('nh.eobs.mobile.mental')

        def patch_spell_search(*args, **kwargs):
            return [1, 2]

        def patch_spell_read(*args, **kwargs):
            return [
                {
                    'patient_id': (1, 'Patient One'),
                    'rapid_tranq': False
                }, {
                    'patient_id': (2, 'Patient Two'),
                    'rapid_tranq': True
                }
            ]

        def patch_calculate_ews_class(*args, **kwargs):
            return 'level-none'

        cls.patient_list = [
            {
                'id': 1,
                'clinical_risk': 'low',
                'ews_trend': 'down',
                'next_ews_time': 'soon'
            },
            {
                'id': 2,
                'clinical_risk': 'low',
                'ews_trend': 'down',
                'next_ews_time': 'now'
            }
        ]

        cls.spell_model._patch_method('search', patch_spell_search)
        cls.spell_model._patch_method('read', patch_spell_read)
        cls.mobile_model._patch_method(
            'calculate_ews_class', patch_calculate_ews_class)

        cls.patients = cls.mobile_model.process_patient_list(
            cls.cr, cls.uid, cls.patient_list, context={'test': 'rapid_tranq'})

    @classmethod
    def tearDownClass(cls):
        cls.spell_model._revert_method('search')
        cls.spell_model._revert_method('read')
        cls.mobile_model._revert_method('calculate_ews_class')
        super(TestPatientListRapidTranq, cls).tearDownClass()

    def test_rapid_tranq_flag(self):
        """
        Test the patient list returns rapid_tranq as True when the spell's
        rapid_tranq falg is True
        """
        self.assertTrue(self.patients[0].get('rapid_tranq'))

    def test_non_rapid_tranq_flag(self):
        """
        Test the patient list returns rapid_tranq as False when the spell's
        rapid tranq flag is False
        """
        self.assertFalse(self.patients[1].get('rapid_tranq'))
