from openerp.osv import fields, osv


class TransferPatientWizard(osv.TransientModel):
    """Wizard for transferring a patient."""
    _name = 'nh.clinical.transfer.wizard'
    _columns = {
        'patient_id': fields.many2one(
            'nh.clinical.patient', 'Patient', required=True),
        'nhs_number': fields.char('NHS Number', size=200),
        'ward_id': fields.many2one('nh.clinical.location', 'Current Ward'),
        'transfer_location_id': fields.many2one(
            'nh.clinical.location', 'Transfer Location')
    }

    def transfer(self, cr, uid, ids, context=None):
        """
        Button called by view_transfer_wizard view to transfer
        patient.
        """
        api = self.pool['nh.eobs.api']
        record = self.browse(cr, uid, ids, context=context)

        result = api.transfer(
            cr, uid, record.patient_id.other_identifier,
            {'location': record.transfer_location_id.code}, context=context
        )
        return result
