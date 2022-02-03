from openerp import models, fields, api


class NhClinicalPatientMergeWizard(models.TransientModel):
    _name = "nh.clinical.patient.merge.wizard"
    _description = "NH Clinical Patient Merge Wizard"

    patient_id = fields.Many2one(
        comodel_name="nh.clinical.patient",
        readonly=True,
        default=lambda self: self.env.context.get("active_id", False),
        string="Source Patient"
    )
    other_identifier = fields.Char(
        related="patient_id.other_identifier",
        readonly=True,
        string="Source Hospital Number",
    )
    dest_patient_id = fields.Many2one(
        comodel_name="nh.clinical.patient",
        default=11352,
        # ^ Static value because permissions restrict m2o domain. For developer to change when required.
        string="Destination Patient",
    )
    dest_other_identifier = fields.Char(
        related="dest_patient_id.other_identifier",
        readonly=True,
        string="Destination Hospital Number",
    )

    @api.multi
    def _default_patient_id(self):
        return self.env.context.get("active_id", False)

    @api.multi
    def merge(self):
        self.env["nh.clinical.api"].merge(
            self.dest_other_identifier,
            {
                "from_identifier": self.other_identifier,
                "into_identifier": self.dest_other_identifier,
            }
        )
