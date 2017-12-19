from openerp.tests.common import TransactionCase


class TestGetActiveObservations(TransactionCase):
    """
    Test that get_active_observations returns the list of active observations
    installed into the system plus neurological observations and removes GCS
    from the list as per EOBS-1014
    """

    def setUp(self):
        super(TestGetActiveObservations, self).setUp()
        self.api_model = self.env['nh.eobs.api']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']

        def mock_spell_search(*args, **kwargs):
            return [666]

        def mock_spell_read(*args, **kwargs):
            obs_stop = False
            context = kwargs.get('context', {})
            if context.get('test') == 'obs_stop':
                obs_stop = True
            return {'obs_stop': obs_stop}

        def mock_activity_search(*args, **kwargs):
            return [666]

        self.spell_model._patch_method('search', mock_spell_search)
        self.spell_model._patch_method('read', mock_spell_read)
        self.activity_model._patch_method('search', mock_activity_search)
        self.obs_list = self.api_model.get_active_observations(0)

    def tearDown(self):
        super(TestGetActiveObservations, self).tearDown()
        self.spell_model._revert_method('search')
        self.spell_model._revert_method('read')
        self.activity_model._revert_method('search')

    def test_adds_neurological_observations(self):
        """
        Test that the neurological observation dict is added to the returned
        list
        """
        neuro = \
            [ob for ob in self.obs_list if ob.get('type') == 'neurological']
        self.assertEqual(
            neuro,
            [
                {
                    'type': 'neurological',
                    'name': 'Neurological'
                }
            ]
        )

    def test_removes_gcs(self):
        """
        Test that the gcs dict is removed from the returned list
        """
        gcs = [ob for ob in self.obs_list if 'type' == 'gcs']
        self.assertEqual(gcs, [])

    def test_empty_list_on_obs_stop(self):
        """
        Test that no observations are displayed when obs_stop flag is set to
        True
        """
        obs_list = self.api_model.with_context({'test': 'obs_stop'})\
            .get_active_observations(0)
        self.assertEqual(obs_list, [])
