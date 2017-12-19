from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import SingleTransactionCase


class TestDoctorObsPermissions(SingleTransactionCase):
    """
    Check that doctor users are able to see the menu item to and are able to
    take ad-hoc NEWS observations for patients
    """

    @classmethod
    def setUpClass(cls):
        super(TestDoctorObsPermissions, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.user_pool = cls.registry('res.users')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.spellboard_pool = cls.registry('nh.clinical.spellboard')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.api_pool = cls.registry('nh.eobs.api')
        cls.category_pool = cls.registry('res.partner.category')
        cls.groups_pool = cls.registry('res.groups')
        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.activity_pool = cls.registry('nh.activity')
        alloc_pool = cls.registry('nh.clinical.user.responsibility.allocation')

        # create a doctor
        doctor_group = cls.groups_pool.search(cr, uid, [
            ['name', '=', 'NH Clinical Doctor Group']
        ])[0]

        doctor_category = cls.category_pool.search(cr, uid, [
            ['name', '=', 'Doctor']
        ])[0]

        cls.doctor = cls.user_pool.create(cr, uid, {
            'login': 'test_doctor',
            'password': 'test_doctor',
            'name': 'Test Doctor',
            'pos_id': 1,
            'pos_ids': [[6, 0, [1]]],
            'groups_id': [[4, doctor_group]],
            'category_id': [[4, doctor_category]]
        })

        # Create a patient to place
        cls.api_pool.register(cr, cls.doctor, 'HOSPTESTPATIENT', {
            'given_name': 'Test',
            'family_name': 'Patient',
            'patient_identifier': 'NHSTESTPATIENT'
        })

        # Create a patient to not place
        cls.api_pool.register(cr, cls.doctor, 'HOSPTESTPATIENT2', {
            'given_name': 'Test',
            'family_name': 'Patient 2',
            'patient_identifier': 'NHSTESTPA2'
        })

        patient = cls.patient_pool.search(cr, uid, [
            ['other_identifier', '=', 'HOSPTESTPATIENT']
        ])[0]
        cls.patient_id = patient

        patient2 = cls.patient_pool.search(cr, uid, [
            ['other_identifier', '=', 'HOSPTESTPATIENT2']
        ])[0]
        cls.patient_id2 = patient2

        ward = cls.location_pool.search(cr, uid, [
            ['code', '=', '325']
        ])[0]

        bed = cls.location_pool.search(cr, uid, [
            ['usage', '=', 'bed'],
            ['parent_id', '=', ward]
        ])[0]

        cls.spell_id = cls.spellboard_pool.create(cr, cls.doctor, {
            'patient_id': patient,
            'location_id': ward,
            'code': 'TESTPATIENTSPELL',
            'start_date': '2016-07-18 00:00:00'
        })

        cls.spell_id = cls.spellboard_pool.create(cr, cls.doctor, {
            'patient_id': patient2,
            'location_id': ward,
            'code': 'TESTPATIENTSPELL2',
            'start_date': '2016-07-18 00:00:00'
        })

        # Place patient into bed on ES2
        placement_data = {
            'suggested_location_id': ward,
            'patient_id': patient
        }
        placement_id = cls.placement_pool.create_activity(
            cr, cls.doctor, {}, placement_data)
        cls.activity_pool.submit(
            cr, cls.doctor, placement_id, {'location_id': bed})
        cls.activity_pool.complete(cr, cls.doctor, placement_id)

        # Assign Doctor to ES2
        activity_id = alloc_pool.create_activity(cr, uid, {}, {
            'responsible_user_id': cls.doctor,
            'location_ids': [[6, 0, [ward]]]})
        cls.activity_pool.complete(cr, uid, activity_id)

    def test_doctor_can_see_adhoc_obs_button(self):
        """
        Test that the doctor can see the Take Observation button patient page
        this is controlled by the list of observations a user can see
        """
        cr = self.cr
        obs = self.api_pool.get_active_observations(
            cr, self.doctor, self.patient_id)
        self.assertIsNotNone(obs)

    def test_doctor_can_submit_adhoc_obs(self):
        """
        Test that the doctor can submit and complete an observation
        """
        cr = self.cr
        observation = 'ews'
        test_ob = self.api_pool.create_activity_for_patient(
            cr, self.doctor, self.patient_id, observation)
        self.assertTrue(
            self.api_pool.complete(cr, self.doctor, test_ob,
                                   clinical_risk_sample_data.LOW_RISK_DATA))

    def test_doctor_cant_see_news_or_placement(self):
        """
        Test that NEWS tasks do not show on the doctor's activity list
        EOBS-274
        """
        cr = self.cr
        tasks = self.api_pool.get_activities(cr, self.doctor, [])
        tasks_names = [t.get('summary') for t in tasks]
        self.assertNotIn('NEWS Observation', tasks_names)
        self.assertNotIn('Patient Placement', tasks_names)

    def test_doctor_only_sees_patients_in_beds(self):
        """
        Test that Patients in the patient list are only those in beds
        EOBS-277
        """
        cr = self.cr
        patients = self.api_pool.get_patients(cr, self.doctor, [])
        patient_ids = [p.get('id') for p in patients]
        self.assertEqual(patient_ids, [self.patient_id])
