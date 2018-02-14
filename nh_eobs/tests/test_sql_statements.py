from openerp.tests.common import TransactionCase


class TestSqlStatements(TransactionCase):

    def setUp(self):
        super(TestSqlStatements, self).setUp()
        self.sql_pool = self.registry('nh.clinical.sql')
        self.settings_pool = self.registry('nh.clinical.settings')
        self.workload_pool = self.registry('nh.clinical.settings.workload')

    def test_last_discharge_users(self):
        test_sql = ' '.join(
            [sql.strip() for sql in
             self.sql_pool.get_last_discharge_users('3d').split('\n') if sql])
        proper_sql = 'SELECT activity.spell_id AS spell_id, ' \
                     'array_agg(DISTINCT users.id) AS user_ids, ' \
                     'array_agg(DISTINCT users2.id) AS ward_user_ids FROM ' \
                     'wb_spell_ranked activity INNER JOIN ' \
                     'wb_discharge_ranked discharge ON discharge.parent_id ' \
                     '= activity.id AND discharge.rank = 1 AND ' \
                     'discharge.state = \'completed\' INNER JOIN ' \
                     'nh_clinical_patient_discharge discharge_data ON ' \
                     'discharge_data.id = discharge.data_id INNER JOIN ' \
                     'nh_clinical_location location ON location.id = ' \
                     'discharge_data.location_id INNER JOIN ' \
                     'ward_locations wl ON wl.id = location.id LEFT JOIN ' \
                     'user_location_rel ulrel ON ulrel.location_id = ' \
                     'location.id LEFT JOIN res_users users ON users.id = ' \
                     'ulrel.user_id LEFT JOIN user_location_rel ulrel2 ON ' \
                     'ulrel2.location_id = wl.ward_id LEFT JOIN res_users ' \
                     'users2 ON users2.id = ulrel2.user_id WHERE now() AT ' \
                     'TIME ZONE \'UTC\' - discharge.date_terminated < ' \
                     'INTERVAL \'3d\' AND activity.rank = 1 AND ' \
                     'activity.state = \'completed\' GROUP BY ' \
                     'activity.spell_id'
        self.assertEqual(test_sql, proper_sql)

    def test_last_transfer_users(self):
        test_sql = ' '.join(
            [sql.strip() for sql in
             self.sql_pool.get_last_transfer_users('3d').split('\n') if sql])
        proper_sql = 'SELECT activity.spell_id AS spell_id, ' \
                     'array_agg(DISTINCT users.id) AS user_ids, ' \
                     'array_agg(DISTINCT users2.id) AS ward_user_ids FROM ' \
                     'wb_spell_ranked activity INNER JOIN ' \
                     'wb_transfer_ranked transfer ON transfer.parent_id = ' \
                     'activity.id AND transfer.rank = 1 AND transfer.state' \
                     ' = \'completed\' INNER JOIN ' \
                     'nh_clinical_patient_transfer transfer_data ON ' \
                     'transfer_data.id = transfer.data_id INNER JOIN ' \
                     'nh_clinical_location location ON location.id = ' \
                     'transfer_data.origin_loc_id INNER JOIN ' \
                     'ward_locations wl ON wl.id = location.id LEFT JOIN ' \
                     'user_location_rel ulrel ON ulrel.location_id = ' \
                     'location.id LEFT JOIN res_users users ON users.id = ' \
                     'ulrel.user_id LEFT JOIN user_location_rel ulrel2 ON ' \
                     'ulrel2.location_id = wl.ward_id LEFT JOIN res_users ' \
                     'users2 ON users2.id = ulrel2.user_id WHERE now() AT ' \
                     'TIME ZONE \'UTC\' - transfer.date_terminated < ' \
                     'INTERVAL \'3d\' AND activity.rank = 1 AND ' \
                     'activity.state = \'started\' GROUP BY activity.spell_id'
        self.assertEqual(test_sql, proper_sql)

    def test_wardboard(self):
        test_sql = ' '.join(
            [sql.strip() for sql in
             self.sql_pool.get_wardboard('10d').split('\n') if sql])
        proper_sql = 'SELECT DISTINCT spell.id AS id, spell.patient_id AS ' \
                     'patient_id, spell_activity.id AS spell_activity_id, ' \
                     'spell_activity.date_started AS spell_date_started, ' \
                     'spell_activity.date_terminated AS ' \
                     'spell_date_terminated, spell.pos_id, spell.code AS ' \
                     'spell_code, spell_activity.state AS spell_state, CASE ' \
                     'WHEN extract(days FROM justify_hours(now() AT TIME ' \
                     'ZONE \'UTC\' - spell_activity.date_started)) > 0 THEN ' \
                     'extract(days FROM justify_hours(now() AT TIME ZONE ' \
                     '\'UTC\' - spell_activity.date_started)) || ' \
                     '\' day(s) \' ELSE \'\' END || to_char(justify_hours(' \
                     'now() '\
                     'AT TIME ZONE \'UTC\' - spell_activity.date_started), ' \
                     '\'HH24:MI\') time_since_admission, spell.move_date, ' \
                     'patient.family_name, patient.given_name, ' \
                     'patient.middle_names, CASE WHEN patient.given_name IS ' \
                     'NULL THEN \'\' ELSE upper(substring(patient.given_name '\
                     'FROM 1 FOR 1)) END AS initial, ' \
                     'coalesce(patient.family_name, \'\') || \', \' || ' \
                     'coalesce(patient.given_name, \'\') || \' \' || ' \
                     'coalesce(patient.middle_names,\'\') AS full_name, ' \
                     'location.name AS location, location.id AS location_id, '\
                     'wlocation.ward_id AS ward_id, patient.sex, ' \
                     'patient.dob, patient.other_identifier AS ' \
                     'hospital_number, CASE ' \
                     'char_length(patient.patient_identifier) = 10 WHEN ' \
                     'TRUE THEN substring(patient.patient_identifier FROM 1 ' \
                     'FOR 3) || \' \' || ' \
                     'substring(patient.patient_identifier FROM 4 FOR 3) || ' \
                     '\' \' || substring(patient.patient_identifier FROM 7 ' \
                     'FOR 4) ELSE patient.patient_identifier END AS ' \
                     'nhs_number, extract(year FROM age(now(), patient.dob))' \
                     ' AS age, ews0.next_diff_polarity || CASE WHEN ' \
                     'ews0.date_scheduled IS NOT NULL THEN CASE WHEN ' \
                     'extract(days FROM (greatest(now() AT TIME ZONE ' \
                     '\'UTC\', ews0.date_scheduled) - least(now() AT TIME ' \
                     'ZONE \'UTC\', ews0.date_scheduled))) > 0 THEN ' \
                     'extract(days FROM (greatest(now() AT TIME ZONE ' \
                     '\'UTC\', ews0.date_scheduled) - least(now() AT TIME ' \
                     'ZONE \'UTC\', ews0.date_scheduled))) || \' day(s) \' ' \
                     'ELSE \'\' END || to_char(justify_hours(greatest(now() ' \
                     'AT TIME ZONE \'UTC\', ews0.date_scheduled) - ' \
                     'least(now() AT TIME ZONE \'UTC\', ' \
                     'ews0.date_scheduled)), \'HH24:MI\') || \' hours\' ELSE' \
                     ' to_char((INTERVAL \'0s\'), \'HH24:MI\') END AS ' \
                     'next_diff, CASE ews0.frequency < 60 WHEN true THEN ' \
                     'ews0.frequency || \' min(s)\' ELSE ews0.frequency/60 ' \
                     '|| \' hour(s) \' || ews0.frequency - ' \
                     'ews0.frequency/60*60 || \' min(s)\' END AS frequency, ' \
                     'ews0.date_scheduled, CASE WHEN ews1.id IS NULL THEN ' \
                     '\'none\' ELSE ews1.score::text END AS ' \
                     'ews_score_string, ews1.score AS ews_score, CASE WHEN ' \
                     'ews1.id IS NOT NULL AND ews2.id IS NOT NULL AND ' \
                     '(ews1.score - ews2.score) = 0 THEN \'same\' WHEN ' \
                     'ews1.id IS NOT NULL AND ews2.id IS NOT NULL AND ' \
                     '(ews1.score - ews2.score) > 0 THEN \'up\' WHEN ' \
                     'ews1.id IS NOT NULL AND ews2.id IS NOT NULL AND ' \
                     '(ews1.score - ews2.score) < 0 THEN \'down\' WHEN ' \
                     'ews1.id IS NULL AND ews2.id IS NULL THEN \'none\' ' \
                     'WHEN ews1.id IS NOT NULL AND ews2.id IS NULL THEN ' \
                     '\'first\' WHEN ews1.id IS NULL AND ews2.id IS NOT ' \
                     'NULL THEN \'no latest\' END AS ews_trend_string, ' \
                     'CASE WHEN ews1.id IS NULL THEN \'NoScore\' ELSE ' \
                     'ews1.clinical_risk END AS clinical_risk, ews1.score ' \
                     '- ews2.score AS ews_trend, param.height, ' \
                     'param.o2target_level_id AS o2target, CASE WHEN ' \
                     'param.mrsa THEN \'yes\' ELSE \'no\' END AS mrsa, CASE ' \
                     'WHEN param.diabetes THEN \'yes\' ELSE \'no\' END AS ' \
                     'diabetes, CASE WHEN pbp.status THEN \'yes\' ELSE ' \
                     '\'no\' END AS pbp_monitoring, ' \
                     'CASE WHEN param.status THEN \'yes\' ELSE \'no\' ' \
                     'END AS palliative_care, CASE WHEN param.post_surgery ' \
                     'AND param.post_surgery_date > now() - INTERVAL \'4h\' ' \
                     'THEN \'yes\' ELSE \'no\' END AS post_surgery, CASE ' \
                     'WHEN param.critical_care AND param.critical_care_date ' \
                     '> now() - INTERVAL \'24h\' THEN \'yes\' ELSE \'no\' ' \
                     'END AS critical_care, param.uotarget_vol, ' \
                     'param.uotarget_unit, consulting_doctors.names AS ' \
                     'consultant_names, CASE WHEN ' \
                     'spell_activity.date_terminated > now() - INTERVAL ' \
                     '\'10d\' AND spell_activity.state = \'completed\' THEN ' \
                     'true ELSE false END AS recently_discharged FROM ' \
                     'nh_clinical_spell spell INNER JOIN nh_activity ' \
                     'spell_activity ON spell_activity.id = ' \
                     'spell.activity_id INNER JOIN nh_clinical_patient ' \
                     'patient ON spell.patient_id = patient.id LEFT JOIN ' \
                     'nh_clinical_location location ON location.id = ' \
                     'spell.location_id LEFT JOIN ews1 ON spell.id = ' \
                     'ews1.spell_id LEFT JOIN ews2 ON spell.id = ' \
                     'ews2.spell_id LEFT JOIN ews0 ON spell.id = ' \
                     'ews0.spell_id LEFT JOIN ward_locations wlocation ' \
                     'ON wlocation.id = location.id LEFT JOIN ' \
                     'consulting_doctors ON consulting_doctors.spell_id = ' \
                     'spell.id LEFT JOIN pbp pbp ON pbp.spell_id = ' \
                     'spell.id LEFT JOIN param ON param.spell_id = ' \
                     'spell.id ORDER BY location.name'
        self.assertEqual(test_sql, proper_sql)

    def test_workload_case_generator(self):
        """
        Test that when given a list of valid workload buckets it generates a
        list of case statements
        """
        buckets = [{'sequence': 1, 'name': '46+ minutes remain'},
                   {'sequence': 2, 'name': '45-31 minutes remain'},
                   {'sequence': 3, 'name': '16+ minutes late'}]
        cases = self.sql_pool.generate_workload_cases(buckets)
        self.assertEqual(cases[0], 'WHEN proximity > 46 THEN 1')
        self.assertEqual(cases[1], 'WHEN proximity BETWEEN 45 AND 31 THEN 2')
        self.assertEqual(cases[2], 'WHEN proximity < -16 THEN 3')

    def test_workload_case_generator_raises(self):
        """
        Test that the when given a list that has an invalid bucket it raises
        an exception
        """
        buckets = [{'sequence': 1, 'name': 'a minutes remain'}]
        with self.assertRaises(ValueError) as case_err:
            self.sql_pool.generate_workload_cases(buckets)
        self.assertEqual(case_err.exception.message,
                         'Time period in position 1 is invalid')

    def test_workload_sql_view_cases(self):
        """
        Test that the SQL view renders the cases in the select
        """
        buckets = [{'sequence': 1, 'name': '46+ minutes remain'},
                   {'sequence': 2, 'name': '45-31 minutes remain'},
                   {'sequence': 3, 'name': '16+ minutes late'}]

        test_sql = ' '.join(
            [sql.strip() for sql in
             self.sql_pool.get_workload(buckets).split('\n') if sql])
        proper_sql = 'WITH activity AS ( ' \
                     'SELECT activity.id AS id, spell.id AS activity_id, ' \
                     'extract (EPOCH FROM (coalesce(activity.date_scheduled,' \
                     ' activity.date_deadline) - now() AT TIME ZONE \'UTC\')' \
                     ')::INT/60 AS proximity, activity.summary AS summary, ' \
                     'activity.state AS state, activity.user_id AS user_id, ' \
                     'coalesce(activity.date_scheduled, ' \
                     'activity.date_deadline) AS date_scheduled, ' \
                     'activity.data_model AS data_model, ' \
                     'patient.other_identifier AS patient_other_id, ' \
                     'patient.patient_identifier AS nhs_number, ' \
                     'patient.family_name AS family_name, ' \
                     'CASE WHEN patient.given_name IS NULL THEN \'\' ELSE ' \
                     'upper(substring(patient.given_name FROM 1 FOR 1)) ' \
                     'END AS initial, ward.id AS ward_id FROM nh_activity ' \
                     'activity INNER JOIN nh_clinical_patient patient ' \
                     'ON activity.patient_id = patient.id INNER JOIN ' \
                     'nh_clinical_location bed ON activity.location_id = ' \
                     'bed.id INNER JOIN nh_clinical_location ward ON ' \
                     'bed.parent_id = ward.id INNER JOIN nh_activity spell ' \
                     'ON spell.data_model = \'nh.clinical.spell\' AND ' \
                     'spell.patient_id = activity.patient_id WHERE ' \
                     'activity.state != \'completed\' AND activity.state !=' \
                     ' \'cancelled\' AND spell.state = \'started\') SELECT ' \
                     'id, activity_id, CASE WHEN proximity > 46 THEN 1 ' \
                     'WHEN proximity BETWEEN 45 AND 31 THEN 2 ' \
                     'WHEN proximity < -16 THEN 3 ELSE NULL ' \
                     'END AS proximity_interval, summary, state, user_id, ' \
                     'date_scheduled, data_model, patient_other_id, ' \
                     'nhs_number, ward_id, family_name, initial FROM activity'
        self.assertEqual(test_sql, proper_sql)

    def test_workload_sql_view_no_cases(self):
        """
        Test that the SQL view renders the cases in the select
        """
        buckets = []
        test_sql = ' '.join(
            [sql.strip() for sql in
             self.sql_pool.get_workload(buckets).split('\n') if sql])
        proper_sql = 'WITH activity AS ( ' \
                     'SELECT activity.id AS id, spell.id AS activity_id, ' \
                     'extract (EPOCH FROM (coalesce(activity.date_scheduled,' \
                     ' activity.date_deadline) - now() AT TIME ZONE \'UTC\')' \
                     ')::INT/60 AS proximity, activity.summary AS summary, ' \
                     'activity.state AS state, activity.user_id AS user_id, ' \
                     'coalesce(activity.date_scheduled, ' \
                     'activity.date_deadline) AS date_scheduled, ' \
                     'activity.data_model AS data_model, ' \
                     'patient.other_identifier AS patient_other_id, ' \
                     'patient.patient_identifier AS nhs_number, ' \
                     'patient.family_name AS family_name, ' \
                     'CASE WHEN patient.given_name IS NULL THEN \'\' ELSE ' \
                     'upper(substring(patient.given_name FROM 1 FOR 1)) ' \
                     'END AS initial, ward.id AS ward_id FROM nh_activity ' \
                     'activity INNER JOIN nh_clinical_patient patient ' \
                     'ON activity.patient_id = patient.id INNER JOIN ' \
                     'nh_clinical_location bed ON activity.location_id = ' \
                     'bed.id INNER JOIN nh_clinical_location ward ON ' \
                     'bed.parent_id = ward.id INNER JOIN nh_activity spell ' \
                     'ON spell.data_model = \'nh.clinical.spell\' AND ' \
                     'spell.patient_id = activity.patient_id WHERE ' \
                     'activity.state != \'completed\' AND activity.state !=' \
                     ' \'cancelled\' AND spell.state = \'started\') SELECT ' \
                     'id, activity_id, 10 AS proximity_interval, summary, ' \
                     'state, user_id, date_scheduled, data_model, ' \
                     'patient_other_id, nhs_number, ward_id, family_name, ' \
                     'initial FROM activity'
        self.assertEqual(test_sql, proper_sql)
