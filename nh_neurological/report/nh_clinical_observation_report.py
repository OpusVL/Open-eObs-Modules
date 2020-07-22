# -*- coding: utf-8 -*-
from openerp import models


class NhClinicalPatientObservationReport(models.AbstractModel):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    def get_report_data(self, data, ews_only=False):
        report_data = super(NhClinicalPatientObservationReport, self)\
            .get_report_data(data, ews_only=ews_only)
        neuro_data = self.get_neurological_observations(data)
        report_data['neurological'] = neuro_data

        self._register_graph_data('neurological', 'neurological_data')

        return report_data

    def _localise_and_format_datetimes(self, report_data):
        super(NhClinicalPatientObservationReport, self)._localise_and_format_datetimes(report_data)
        for obs in report_data.get('neurological', []):
            self._localise_dict_time(obs, 'date_started')
            self._localise_dict_time(obs, 'date_terminated')
            self._localise_dict_time(obs, 'effective_date_terminated')

    def get_neurological_observations(self, data):
        neuro_model = self.env['nh.clinical.patient.observation.neurological']
        neurological_observations = self.get_model_data(
            self.spell_activity_id, neuro_model._name,
            data.start_time, data.end_time
        )
        return neurological_observations
