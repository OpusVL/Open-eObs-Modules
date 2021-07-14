from openerp.osv import fields, osv


class CancelAdmitPatientWizard(osv.TransientModel):
    """Wizard for cancelling the admission of a patient."""
    _name = 'nh.clinical.cancel_admit.wizard'
    _columns = {
        'patient_id': fields.many2one(
            'nh.clinical.patient', 'Patient', required=True),
        'nhs_number': fields.char('NHS Number', size=200),
        'ward_id': fields.many2one('nh.clinical.location', 'Current Ward'),
        'transfer_location_id': fields.many2one(
            'nh.clinical.location', 'Transfer Location')
    }

    def cancel_admit(self, cr, uid, ids, context=None):
        """
        Button called by view_cancel_transfer_wizard to cancel the
        admissions of a patient.
        """
        api = self.pool['nh.eobs.api']
        record = self.browse(cr, uid, ids, context=context)

        result = api.cancel_admit(
            cr, uid, record.patient_id.other_identifier, context=context
        )
        return result
