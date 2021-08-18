from datetime import datetime as dt

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class DischargePatientWizard(osv.TransientModel):
    """Wizard for discharging a patient."""
    _name = 'nh.clinical.discharge.wizard'
    _columns = {
        'patient_id': fields.many2one(
            'nh.clinical.patient', 'Patient', required=True),
        'nhs_number': fields.char('NHS Number', size=200),
        'ward_id': fields.many2one('nh.clinical.location', 'Current Ward'),
    }

    def discharge(self, cr, uid, ids, context=None):
        """
        Button called by view_discharge_wizard view to discharge
        patient.
        """
        api = self.pool['nh.eobs.api']
        record = self.browse(cr, uid, ids, context=context)

        result = api.discharge(
            cr, uid, record.patient_id.other_identifier,
            {'discharge_date': dt.now().strftime(DTF)}, context=context
        )
        return result
