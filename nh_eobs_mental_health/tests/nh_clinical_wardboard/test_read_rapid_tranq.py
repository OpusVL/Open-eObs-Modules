from openerp.tests.common import SingleTransactionCase
import __builtin__


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
                'rapid_tranq': False
            }
            if test in ['rapid_tranq']:
                res['rapid_tranq'] = True
            return res

        cls.spell_model._patch_method('search', patch_spell_search)
        cls.spell_model._patch_method('read', patch_spell_read)

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
        super(TestReadObsStop, cls).tearDownClass()

    def test_with_rapid_tranq(self):
        """
        Test that wardboard rapid_tranq is True when spell has rapid_tranq
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(
            cr, uid, 1, fields=['rapid_tranq'],
            context={'test': 'rapid_tranq'})
        self.assertTrue(read.get('rapid_tranq'))

    def test_without_rapid_tranq(self):
        """
        Test that wardboard rapid_tranq is False when spell doesn't have
        rapid tranq
        """
        cr, uid = self.cr, self.uid
        read = self.wardboard_model.read(
            cr, uid, 1, fields=['rapid_tranq'],
            context={'test': 'not_rapid_tranq'})
        self.assertFalse(read.get('rapid_tranq'))
