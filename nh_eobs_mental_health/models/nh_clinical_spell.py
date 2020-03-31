# -*- coding: utf-8 -*-
from openerp.osv import orm, fields


class NHClinicalSpell(orm.Model):
    """
    Override to add a boolean flag that indicates whether there are active
    patient monitoring exceptions on the spell.
    """
    _name = 'nh.clinical.spell'
    _inherit = 'nh.clinical.spell'

    _columns = {
        'obs_stop': fields.boolean('Stop Observations for patient?'),
        'rapid_tranq': fields.boolean('Patient on Rapid Tranquilisation?'),
        'refusing_obs': fields.boolean('Patient Refusing Observations?'),
        # DEBT, cannot move refusing obs flag to activity model
        # as the current data model (i.e wardboard) will not support this
        'refusing_obs_blood_glucose': fields.boolean('Patient Refusing Blood Glucose Observations?'),
    }

    _defaults = {
        'obs_stop': False,
        'rapid_tranq': False,
        'refusing_obs': False,
        'refusing_obs_blood_glucose': False,
    }
