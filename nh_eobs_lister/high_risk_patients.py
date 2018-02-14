from openerp.osv import orm, fields

class nh_high_risk_patients(orm.Model):

    _name = 'nh.activity.high_risk'
    _inherits = {'nh.activity': 'activity_id'}
    _description = "High Risk Patients"
    _auto = False
    _table = "nh_high_risk_patients"

    # time elapsed since last observation
    _proximity_intervals = [
        (5, '0-5 minutes'),
        (15, '6-15 minutes'),
        (30, '16-30 minutes'),
        (45, '31-45 minutes'),
        (50, '46+ minutes')
    ]
    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'proximity_interval': fields.selection(_proximity_intervals, 'Proximity Interval', readonly=True),
        'clinical_risk': fields.text('Clinical Risk'),
        'summary': fields.text('Summary'),
        'state': fields.text('State'),
        'ews_score': fields.integer('Latest Score'),
        'ews_trend_string': fields.text('Score Trend String'),
        'user_id': fields.many2one('res.users', 'Assigned to'),
        'date_terminated': fields.datetime('Observation Date'),
        'data_model': fields.text('Data Model'),
        'initial': fields.text('Patient Name Initial'),
        'family_name': fields.text('Patient Family Name'),
        'age': fields.integer('Age'),
        'sex': fields.text('Sex'),
        'nhs_number': fields.text('NHS Number'),
        'current_location_id': fields.many2one('nh.clinical.location', 'Current Location'),
        'ward_id': fields.many2one('nh.clinical.location', 'Parent Location')
    }

    def _get_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        pi_copy = [(pi[0], pi[1]) for pi in self._proximity_intervals]
        groups = pi_copy
        groups.reverse()
        fold = {pi[0]: False for pi in pi_copy}
        return groups, fold

    _group_by_full = {'proximity_interval': _get_groups}

    def init(self, cr):
        """
        Gets patients with in open spells with "High" clinical risk
        then order patients by time since last observation.
        """
        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    with high_risk as (
                       select
                            ews_1.id as id,
                            ews_1.spell_id as activity_id,
                            extract (epoch from (now() at time zone 'UTC' - ews_1.date_terminated))::int/60 as proximity,
                            ews_1.clinical_risk as clinical_risk,
                            ews_1.state as state,
                            ews_1.score as ews_score,
                            ews_1.date_terminated as date_terminated,
                            case
                                when ews_1.id is not null and ews_2.id is not null and (ews_1.score - ews_2.score) = 0 then 'same'
                                when ews_1.id is not null and ews_2.id is not null and (ews_1.score - ews_2.score) > 0 then 'up'
                                when ews_1.id is not null and ews_2.id is not null and (ews_1.score - ews_2.score) < 0 then 'down'
                                when ews_1.id is null and ews_2.id is null then 'none'
                                when ews_1.id is not null and ews_2.id is null then 'first'
                                when ews_1.id is null and ews_2.id is not null then 'no latest' -- shouldn't happen.
                            end as ews_trend_string,
                            activity.summary as summary,
                            activity.user_id as user_id,
                            activity.data_model as data_model,
                            patient.patient_identifier as nhs_number,
                            patient.family_name as family_name,
                            patient.current_location_id as current_location_id,
                            patient.sex as sex,
                            case
                                when patient.given_name is null then ''
                                else upper(substring(patient.given_name from 1 for 1))
                            end as initial,
                            extract(year from age(now(), patient.dob)) as age,
                            ward.id as ward_id
                        from nh_clinical_spell as spell
                        inner join nh_activity activity on activity.id = spell.activity_id and activity.state = 'started'
                        inner join nh_clinical_location bed on activity.location_id = bed.id
                        inner join nh_clinical_location ward on bed.parent_id = ward.id
                        inner join ews1 ews_1 on ews_1.spell_activity_id = activity.id
                        inner join ews2 ews_2 on ews_2.spell_activity_id = activity.id
                        inner join nh_clinical_patient patient on ews_1.patient_id = patient.id
                        where ews_1.clinical_risk = 'High'
                        )
                        select
                            id,
                            activity_id,
                            case
                                when proximity < 5 then 5
                                when proximity between 5 and 14 then 15
                                when proximity between 15 and 29 then 30
                                when proximity between 30 and 44 then 45
                                when proximity > 45 then 50
                            else null end as proximity_interval,
                            clinical_risk,
                            ews_score,
                            ews_trend_string,
                            summary,
                            state,
                            user_id,
                            date_terminated,
                            data_model,
                            nhs_number,
                            family_name,
                            initial,
                            age,
                            sex,
                            current_location_id,
                            ward_id
                        from high_risk
                    )
                """ % (self._table, self._table))



