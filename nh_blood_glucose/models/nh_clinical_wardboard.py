# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp.addons.nh_eobs.wardboard import nh_clinical_wardboard


class NhClinicalWardboardBloodGlucose(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

    _columns = {
        'blood_glucose_ids': fields.function(
            nh_clinical_wardboard._get_data_ids_multi,
            multi='blood_glucose_ids', type='many2many',
            relation='nh.clinical.patient.observation.blood_glucose',
            string='Blood Glucose Obs')
    }

    def wardboard_blood_glucose_chart(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`wardboard<nh_clinical_wardboard>` for the view
        ``view_wardboard_blood_glucose_chart_form``.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(
            cr,
            uid,
            [
                ('name', '=', 'view_wardboard_blood_glucose_chart_form')
            ],
            context=context
        )
        view_id = model_data_pool.read(
            cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': int(view_id)
        }
