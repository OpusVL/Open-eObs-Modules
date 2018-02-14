import __builtin__

from openerp.tests.common import SingleTransactionCase


class PatchedReadSuper(object):

    def read(*args, **kwargs):
        return {
            'patient_id': 1,
            'next_diff': 'soon',
            'frequency': '15 Minutes'
        }


class TestReadObsStop(SingleTransactionCase):
    """
    Test that next_diff on wardboard is set to 'Observations Stopped' when
    obs_stop flag is set to True
    """

    @classmethod
    def setUpClass(cls):
        super(TestReadObsStop, cls).setUpClass()
        cls.wardboard_model = cls.registry('nh.clinical.wardboard')
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.obs_stop_model = \
            cls.registry('nh.clinical.pme.obs_stop')

        def patch_wardboard_read_super(*args, **kwargs):
            return PatchedReadSuper()

        cls.patch_wardboard_read_super = patch_wardboard_read_super

        def patch_spell_search(*args, **kwargs):
            return [1]

        def patch_spell_read(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            res = {
                'id': 1,
                'obs_stop': False
            }
            if test in ['obs_stopped', 'no_reason', 'multiple']:
                res['obs_stop'] = True
            return res

        def patch_pme_search(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            vals = {
                'no_reason': [],
                'multiple': [2, 1]
            }
            return vals.get(test, [1])

        def patch_pme_read(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            if test == 'multiple':
                global reason_id_sent
                reason_id_sent = args[3]
                return {
                    'reason': (2, 'AWOL')
                }
            return {
                'reason': (1, 'Acute hospital ED')
            }

        cls.spell_model._patch_method('search', patch_spell_search)
        cls.spell_model._patch_method('read', patch_spell_read)
        cls.obs_stop_model._patch_method('search', patch_pme_search)
        cls.obs_stop_model._patch_method('read', patch_pme_read)

        cls.original_super = super

    def setUp(self):
        super(TestReadObsStop, self).setUp()
        __builtin__.super = self.patch_wardboard_read_super

    def tearDown(self):
        __builtin__.super = self.original_super
        super(TestReadObsStop, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        __builtin__.super = cls.original_super
        cls.spell_model._revert_method('search')
        cls.spell_model._revert_method('read')
        cls.obs_stop_model._revert_method('search')
        cls.obs_stop_model._revert_method('read')
        super(TestReadObsStop, cls).tearDownClass()

    def test_next_diff_with_obs_stop(self):
        """
        Test that next_diff is set to 'Observation Stopped' when obs_stop flag
        on spell is True
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(
            cr, uid, 1, fields=['next_diff', 'patient_id'],
            context={'test': 'obs_stopped'})
        self.assertEqual(read.get('next_diff'), 'Observations Stopped')
        self.assertEqual(read.get('frequency'), 'Acute hospital ED')

    def test_next_diff_without_obs_stop(self):
        """
        Test that next_diff is set to the next EWS deadline when obs_stop flag
        on spell is False
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(cr, uid, 1,
                                         fields=['next_diff', 'patient_id'],
                                         context={'test': 'obs_not_stopped'})
        self.assertEqual(read.get('next_diff'), 'soon')
        self.assertEqual(read.get('frequency'), '15 Minutes')

    def test_next_diff_without_obs_stop_reason(self):
        """
        Test that next_diff is set to the next EWS deadline when obs_stop flag
        on spell is True but no reason
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(cr, uid, 1,
                                         fields=['next_diff', 'patient_id'],
                                         context={'test': 'no_reason'})
        self.assertEqual(read.get('next_diff'), 'Observations Stopped')
        self.assertEqual(read.get('frequency'), '15 Minutes')

    def test_multiple_pme_reasons(self):
        """
        EOBS-448 check that when the patient has had multiple PME that
        the latest reason is returned as frequency
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(cr, uid, 1,
                                         fields=['next_diff', 'patient_id'],
                                         context={'test': 'multiple'})
        self.assertEqual(read.get('next_diff'), 'Observations Stopped')
        self.assertEqual(read.get('frequency'), 'AWOL')
        self.assertEqual(reason_id_sent, 2)
