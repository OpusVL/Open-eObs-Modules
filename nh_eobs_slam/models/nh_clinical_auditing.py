from openerp.osv import orm


class NHClinicalUserRespAllocation(orm.Model):
    """
    Overrides for user responsibility code in the nh_clinical/auditing.py file
    """

    _name = 'nh.clinical.user.responsibility.allocation'
    _inherit = 'nh.clinical.user.responsibility.allocation'

    def get_allocation_locations(self, cr, uid, allocation_obj, context=None):
        """
        Override the get_allocation_locations method to take into account the
        way SLaM wants Doctors to be allocated
        :param cr: Odoo cursor
        :param uid: User ID for user performing operation
        :param allocation_obj: Allocation activity data ref object
        :param context: Odoo context
        :return: list of location ids
        """
        location_pool = self.pool.get('nh.clinical.location')
        locations = []
        groups = [g.name for g in allocation_obj.responsible_user_id.groups_id]
        clinical_groups = ['NH Clinical {0} Group'.format(g) for g in
                           ['HCA', 'Nurse', 'Doctor']]
        if not any([g in clinical_groups for g in groups]):
            for loc in allocation_obj.location_ids:
                if loc.usage == 'ward':
                    locations.append(loc.id)
                else:
                    locations += location_pool.search(
                        cr, uid, [['id', 'child_of', loc.id]], context=context)
        elif 'NH Clinical Doctor Group' in groups:
            for loc in allocation_obj.location_ids:
                if loc.usage == 'ward':
                    locations.append(loc.id)
                locations += location_pool.search(
                    cr, uid, [['id', 'child_of', loc.id]], context=context)
        else:
            for loc in allocation_obj.location_ids:
                locations += location_pool.search(
                    cr, uid, [['id', 'child_of', loc.id]], context=context)
        return locations
