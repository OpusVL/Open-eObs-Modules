# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv


def list_diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]


def list_intersect(a, b):
    b = set(b)
    return [aa for aa in a if aa in b]


class AllocationWizards(models.AbstractModel):

    _name = 'nh.clinical.allocation'

    create_uid = fields.Many2one(
        'res.users',
        'User Executing the Wizard')
    create_date = fields.Datetime('Create Date')

    def responsibility_allocation_activity(self, user_id, location_ids):
        """
        Create and complete a responsibility allocation activity for location
        :param location_ids: Ward ID
        :return: True
        """
        NhActivity = self.env['nh.activity']
        NhClinicalUserResponsibilityAllocation = self.env['nh.clinical.user.responsibility.allocation']
        activity_id = NhClinicalUserResponsibilityAllocation.create_activity({}, {
                'responsible_user_id': user_id,
                'location_ids': [[6, 0, location_ids]]
            })
        NhActivity.complete(activity_id)
        return True

    def unfollow_patients_in_locations(self, location_ids):
        """
        Unfollow any patients in the locations currently being reallocated
        :param location_ids: List of location ids
        :return: True
        """
        NhActivity = self.env['nh.activity']
        NhClinicalPatient = self.env['nh.clinical.patient']
        NhClinicalPatientUnfollow = self.env['nh.clinical.patient.unfollow']
        patient_ids = NhClinicalPatient.search([['current_location_id', 'in', location_ids]]).ids
        if patient_ids:
            unfollow_activity = NhClinicalPatientUnfollow.create_activity({}, {
                'patient_ids': [[6, 0, patient_ids]]})
            NhActivity.complete(unfollow_activity)
        return True

    @api.multi
    def complete(self):
        NhClinicalAllocating = self.env['nh.clinical.allocating']
        allocation = {u.id: [l.id for l in u.location_ids] for u in
                      self.user_ids}
        for allocating in self.allocating_ids:
            if allocating.nurse_id:
                allocation[allocating.nurse_id.id].append(allocating.location_id.id)
                if allocating.nurse_id.id == self.env.uid:
                    allocation[allocating.nurse_id.id].append(self.ward_id.id)
            for hca in allocating.hca_ids:
                allocation[hca.id].append(allocating.location_id.id)
        for key, value in allocation.iteritems():
            self.responsibility_allocation_activity(key, value)
        return {'type': 'ir.actions.act_window_close'}


class StaffAllocationWizard(models.TransientModel):
    _name = 'nh.clinical.staff.allocation'
    _inherit = 'nh.clinical.allocation'
    _rec_name = 'create_uid'

    _stages = [['wards', 'My Ward'], ['review', 'De-allocate'],
               ['users', 'Roll Call'], ['allocation', 'Allocation'],
               ['batch_allocation', 'Batch Allocation']]


    stage = fields.Selection(_stages, string='Stage')
    ward_id = fields.Many2one('nh.clinical.location',
                               string='Ward',
                               domain=[['usage', '=', 'ward']])
    location_ids = fields.Many2many('nh.clinical.location',
                                     'alloc_loc_rel', 'allocation_id',
                                     'location_id',
                                     string='Locations')
    user_ids = fields.Many2many('res.users', 'alloc_user_rel',
                                 'allocation_id', 'user_id',
                                 string='Users',
                                 domain=[
                                     ['groups_id.name', 'in',
                                      ['NH Clinical HCA Group',
                                       'NH Clinical Nurse Group']]
                                 ])
    allocating_ids = fields.Many2many('nh.clinical.allocating',
                                       'alloc_allocating_rel',
                                       'allocation_id',
                                       'allocating_id',
                                       string='Allocating Locations')
    # Clone the fields from nh.clinical.allocation to allow us to do the batch
    # operation on this model, instead of a new modal.
    nurse_id = fields.Many2one(
        'res.users', 'Responsible Nurse',
        domain=[['groups_id.name', 'in', ['NH Clinical Nurse Group']]])
    hca_ids = fields.Many2many(
        'res.users',
        string='Responsible HCAs',
        domain=[['groups_id.name', 'in', ['NH Clinical HCA Group']]])


    _defaults = {
        'stage': 'wards'
    }

    # We need to clone this function from nh.clinical.allocation to ensure
    # the values which show up in nurse_id and hca_ids are correct
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(StaffAllocationWizard, self).fields_view_get(cr, uid, view_id,
                                                           view_type, context,
                                                           toolbar, submenu)
        allocation_pool = self.pool['nh.clinical.staff.allocation']
        al_id = allocation_pool.search(cr, uid, [['create_uid', '=', uid]],
                                       order='id desc')
        allocation = True if al_id else False
        if not al_id or view_type != 'form':
            return res
        else:
            if allocation:
                allocation = allocation_pool.browse(cr, uid, al_id[0],
                                                    context=context)
                user_ids = [u.id for u in allocation.user_ids]
                res['fields']['nurse_id']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical Nurse Group']]
                ]
                res['fields']['hca_ids']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical HCA Group']]
                ]
        return res

    @api.multi
    def confirm_batch(self):
        self.write({'stage': 'allocation'})
        for record in [x for x in self.allocating_ids if x.selected == True]:
            record.write({
                'nurse_id': self.nurse_id.id,
                'hca_ids': [[6, 0, self.hca_ids.ids]]
            })
        # Clear the field
        self.write({'nurse_id': False, 'hca_ids': [[6, 0, []]]})
        # Clear the selected field
        self.allocating_ids.write({'selected': False})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def batch_allocate(self):
        self.write({'stage': 'batch_allocation'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def submit_ward(self):
        ward_ids = [self.ward_id.id]
        NhClinicalLocation = self.env['nh.clinical.location']
        location_ids = NhClinicalLocation.search([['id', 'child_of', ward_ids]]).ids
        self.write({'stage': 'review', 'location_ids': [[6, 0, location_ids]]})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def deallocate(self):
        ResUsers = self.env['res.users']
        NhClinicalAllocating = self.env['nh.clinical.allocating']
        location_ids = [location.id for location in self.location_ids]
        user_ids = ResUsers.search([
            ['groups_id.name', 'in',
             [
                 'NH Clinical HCA Group',
                 'NH Clinical Nurse Group',
                 'NH Clinical Shift Coordinator Group'
             ]],
            ['location_ids', 'in', location_ids]
        ])
        for location_id in location_ids:
            user_ids.write({'location_ids': [[3, location_id]]})
        self.responsibility_allocation_activity(self.env.uid, [self.ward_id.id])
        self.unfollow_patients_in_locations(location_ids)
        allocating_ids = []
        for location in self.location_ids:
            if location.usage == 'bed':
                allocating_ids.append(NhClinicalAllocating.create({'location_id': location.id}).id)
        self.write({
           'allocating_ids': [[6, 0, allocating_ids]],
           'stage': 'users'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def submit_users(self):
        self.write({'stage': 'allocation'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class StaffReallocationWizard(models.TransientModel):
    _name = 'nh.clinical.staff.reallocation'
    _inherit = 'nh.clinical.allocation'
    _rec_name = 'create_uid'

    _nursing_groups = ['NH Clinical Nurse Group', 'NH Clinical HCA Group']
    _stages = [['users', 'Current Roll Call'], ['allocation', 'Allocation'], ['batch_allocation', 'Batch Allocation']]

    @api.multi
    def _get_default_ward(self):
        NhClinicalLocation = self.env['nh.clinical.location']
        ward_ids = NhClinicalLocation.search([['usage', '=', 'ward'], ['user_ids', 'in', [self.env.uid]]])
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        return ward_ids[0]

    def get_users_for_locations(self, locations):
        ResUsers = self.env['res.users']
        if not isinstance(locations, list):
            locations = locations.ids
        return ResUsers.search([
            ['groups_id.name', 'in', self._nursing_groups],
            ['location_ids', 'in', locations]]
        )

    @api.multi
    def _get_default_users(self):
        locations = self._get_default_locations()
        return self.get_users_for_locations(locations)

    @api.multi
    def _get_default_locations(self):
        NhClinicalLocation = self.env['nh.clinical.location']
        ward_id = self._get_default_ward()
        locations = NhClinicalLocation.search([['id', 'child_of', ward_id.id]])
        return locations

    @api.model
    def _get_default_allocatings(self):
        NhClinicalLocation = self.env['nh.clinical.location']
        NhClinicalAllocating = self.env['nh.clinical.allocating']
        locations = self._get_default_locations()
        allocating_ids = []
        for l in locations:
            if l.usage != 'bed':
                continue
            nurse_id = False
            hca_ids = []
            for u in l.user_ids:
                groups = [g.name for g in u.groups_id]
                if 'NH Clinical Nurse Group' in groups and \
                        'NH Clinical Shift Coordinator Group' not in groups:
                    nurse_id = u.id
                if 'NH Clinical HCA Group' in groups:
                    hca_ids.append(u.id)
                if 'NH Clinical Shift Coordinator Group' in groups \
                        and not nurse_id:
                            nurse_id = u.id
            allocating_ids.append(NhClinicalAllocating.create({
                'location_id': l.id,
                'nurse_id': nurse_id,
                'hca_ids': [[6, 0, hca_ids]]
            }).id)
        return allocating_ids

    stage = fields.Selection(_stages, string='Stage')
    ward_id = fields.Many2one('nh.clinical.location',
                               string='Ward',
                               domain=[['usage', '=', 'ward']])
    location_ids = fields.Many2many('nh.clinical.location',
                                     'realloc_loc_rel', 'reallocation_id',
                                     'location_id',
                                     string='Locations')
    user_ids = fields.Many2many('res.users', 'realloc_user_rel',
                                 'allocation_id', 'user_id',
                                 string='Users',
                                 domain=[
                                     ['groups_id.name', 'in',
                                      ['NH Clinical HCA Group',
                                       'NH Clinical Nurse Group']]
                                 ])
    allocating_ids = fields.Many2many('nh.clinical.allocating',
                                       'real_allocating_rel',
                                       'reallocation_id',
                                       'allocating_id',
                                       string='Allocating Locations')
    # These fields are copied from nh.clinical.allocating, needed for our batch.
    # I would have put them in a new 'batch' model, but doing anything other than an edit
    # in a new modal closes the previous one, so instead we're just changing the stage of the existing one
    nurse_id = fields.Many2one(
        'res.users', 'Responsible Nurse',
        domain=[['groups_id.name', 'in', ['NH Clinical Nurse Group']]])
    hca_ids = fields.Many2many(
        'res.users',
        string='Responsible HCAs',
        domain=[['groups_id.name', 'in', ['NH Clinical HCA Group']]])

    _defaults = {
        'stage': 'users',
        'ward_id': _get_default_ward,
        'user_ids': _get_default_users,
        'location_ids': _get_default_locations,
        'allocating_ids': _get_default_allocatings
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(StaffReallocationWizard, self).fields_view_get(cr, uid, view_id,
                                                           view_type, context,
                                                           toolbar, submenu)
        allocation_pool = self.pool['nh.clinical.staff.allocation']
        reallocation_pool = self.pool['nh.clinical.staff.reallocation']
        al_id = allocation_pool.search(cr, uid, [['create_uid', '=', uid]],
                                       order='id desc')
        real_id = reallocation_pool.search(cr, uid, [['create_uid', '=', uid]],
                                           order='id desc')
        allocation = True if al_id else False
        if al_id and real_id:
            al = allocation_pool.browse(cr, uid, al_id[0], context=context)
            real = reallocation_pool.browse(cr, uid, real_id[0],
                                            context=context)
            allocation = True if al.create_date > real.create_date else False
        if not (al_id or real_id) or view_type != 'form':
            return res
        else:
            if allocation:
                allocation = allocation_pool.browse(cr, uid, al_id[0],
                                                    context=context)
                user_ids = [u.id for u in allocation.user_ids]
                res['fields']['nurse_id']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical Nurse Group']]
                ]
                res['fields']['hca_ids']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical HCA Group']]
                ]
            else:
                reallocation = reallocation_pool.browse(cr, uid, real_id[0],
                                                        context=context)
                user_ids = [u.id for u in reallocation.user_ids]
                res['fields']['nurse_id']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical Nurse Group']]
                ]
                res['fields']['hca_ids']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical HCA Group']]
                ]
        return res


    @api.multi
    def confirm_batch(self):
        self.write({'stage': 'allocation'})
        for record in [x for x in self.allocating_ids if x.selected == True]:
            record.write({
                'nurse_id': self.nurse_id.id,
                'hca_ids': [[6, 0, self.hca_ids.ids]]
            })
        # Clear the field
        self.write({'nurse_id': False, 'hca_ids': [[6, 0, []]]})
        # Clear the selected tickboxes
        self.allocating_ids.write({'selected': False})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Re-Allocation',
            'res_model': 'nh.clinical.staff.reallocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def batch_allocate(self):
        self.write({'stage': 'batch_allocation'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Re-Allocation',
            'res_model': 'nh.clinical.staff.reallocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


    @api.multi
    def reallocate(self):
        ResUsers = self.env['res.users']
        wiz = self.read(['location_ids', 'user_ids'])[0]
        location_ids = wiz.get('location_ids')
        loc_user_ids = self.get_users_for_locations(location_ids)
        user_ids = wiz.get('user_ids')
        recompute = False
        for u_id in loc_user_ids:
            if u_id.id not in user_ids and u_id.id != self.env.uid:
                recompute = True
                user = u_id.read(['location_ids'])[0]
                uloc_ids = user.get('location_ids')
                loc_ids = list_diff(uloc_ids, location_ids)
                self.responsibility_allocation_activity(u_id.id, loc_ids)
                # Remove patient followers
                loc_ids = list_intersect(uloc_ids, location_ids)
                self.unfollow_patients_in_locations(loc_ids)
        self.write({'stage': 'allocation'})
        if recompute:
            allocating_ids = self._get_default_allocatings()
            self.write({'allocating_ids': [[6, 0, allocating_ids]]})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Re-Allocation',
            'res_model': 'nh.clinical.staff.reallocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    
    @api.multi
    def complete(self):
        allocation = {
            u.id: [l.id for l in u.location_ids if l.id not
                   in self.location_ids.ids] for u in self.user_ids}
        for allocating in self.allocating_ids:
            if allocating.nurse_id:
                allocation[allocating.nurse_id.id].append(
                    allocating.location_id.id)
                if allocating.nurse_id.id == self.env.uid:
                    allocation[allocating.nurse_id.id].append(
                        self.ward_id.id)
            for hca in allocating.hca_ids:
                allocation[hca.id].append(allocating.location_id.id)
            if self.env.uid not in allocation:
                allocation[self.env.uid] = [self.ward_id.id]
            elif self.ward_id.id not in allocation.get(self.env.uid):
                allocation[self.env.uid].append(self.ward_id.id)
        for key, value in allocation.iteritems():
            self.responsibility_allocation_activity(key, value)
        return {'type': 'ir.actions.act_window_close'}


class doctor_allocation_wizard(models.TransientModel):
    _name = 'nh.clinical.doctor.allocation'
    _rec_name = 'create_uid'

    _stages = [['review', 'De-allocate'], ['users', 'Medical Roll Call']]
    _doctor_groups = ['NH Clinical Doctor Group',
                      'NH Clinical Junior Doctor Group',
                      'NH Clinical Consultant Group',
                      'NH Clinical Registrar Group']

    @api.multi
    def _get_default_ward(self):
        NhClinicalLocation = self.env['nh.clinical.location']
        ward_ids = NhClinicalLocation.search([['usage', '=', 'ward'], ['user_ids', 'in', [self.env.uid]]])
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        return ward_ids[0]

    @api.multi
    def _get_default_locations(self):
        NhClinicalLocation = self.env['nh.clinical.location']
        ward_ids = NhClinicalLocation.search([['usage', '=', 'ward'], ['user_ids', 'in', [self.env.uid]]])
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        location_ids = NhClinicalLocation.search([['id', 'child_of', ward_ids.ids]])
        return location_ids

    @api.multi
    def _get_current_doctors(self):
        NhClinicalLocation = self.env['nh.clinical.location']
        ResUsers = self.env['res.users']
        ward_ids = NhClinicalLocation.search([['usage', '=', 'ward'], ['user_ids', 'in', [self.env.uid]]])
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        doctor_ids = ResUsers.search([['groups_id.name', 'in', self._doctor_groups], ['location_ids', 'in', ward_ids.ids]])
        return doctor_ids


    create_uid = fields.Many2one('res.users',
                                  'User Executing the Wizard')
    create_date = fields.Datetime('Create Date')
    stage = fields.Selection(_stages, string='Stage')
    ward_id = fields.Many2one('nh.clinical.location', string='Ward',
                               domain=[['usage', '=', 'ward']])
    doctor_ids = fields.Many2many('res.users', 'docalloc_doc_rel',
                                   'allocation_id', 'user_id',
                                   string='Current Doctors')
    location_ids = fields.Many2many('nh.clinical.location',
                                     'docalloc_loc_rel', 'allocation_id',
                                     'location_id', string='Locations')
    user_ids = fields.Many2many(
        'res.users', 'docalloc_user_rel', 'allocation_id', 'user_id',
        string='Users', domain=[['groups_id.name', 'in', _doctor_groups]])

    _defaults = {
        'stage': 'review',
        'ward_id': _get_default_ward,
        'location_ids': _get_default_locations,
        'doctor_ids': _get_current_doctors
    }

    @api.multi
    def deallocate(self):
        deallocate_location_ids = self.location_ids.ids

        ResUsers = self.env['res.users']
        all_doctors = ResUsers.search([['groups_id.name', 'in', self._doctor_groups]])

        for doctor in all_doctors:
            doctor_current_location_ids = doctor.location_ids.ids
            doctor_new_location_ids = \
                set(doctor_current_location_ids) - set(deallocate_location_ids)
            doctor.write({'location_ids': [(6, 0, doctor_new_location_ids)]})

        self.write({'stage': 'users'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Shift Change',
            'res_model': 'nh.clinical.doctor.allocation',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def submit_users(self):
        NhClinicalUserResponsibilityAllocation = self.env[
            'nh.clinical.user.responsibility.allocation'
        ]
        NhActivity = self.env['nh.activity']
        for doctor in self.user_ids:
            activity = NhClinicalUserResponsibilityAllocation.create_activity({}, {
                'responsible_user_id': doctor.id,
                'location_ids': [[6, 0, [self.ward_id.id]]]
            })
            NhActivity.complete(activity)
        return {'type': 'ir.actions.act_window_close'}

class allocating_user(models.TransientModel):
    _name = 'nh.clinical.allocating'
    _rec_name = 'location_id'

    selected = fields.Boolean(string="Batch")
    location_id =  fields.Many2one('nh.clinical.location', 'Location',
                                   required=1)
    patient_ids = fields.Many2many(related='location_id.patient_ids',
                                  relation='nh.clinical.patient',
                                  string='Patient')
    nurse_id = fields.Many2one(
        'res.users', 'Responsible Nurse',
        domain=[['groups_id.name', 'in', ['NH Clinical Nurse Group']]])
    hca_ids = fields.Many2many(
        'res.users', 'allocating_hca_rel', 'allocating_id', 'hca_id',
        string='Responsible HCAs',
        domain=[['groups_id.name', 'in', ['NH Clinical HCA Group']]])
    nurse_name = fields.Char(related='nurse_id.name', size=100, string='Responsible Nurse')


    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(allocating_user, self).fields_view_get(cr, uid, view_id,
                                                           view_type, context,
                                                           toolbar, submenu)
        allocation_pool = self.pool['nh.clinical.staff.allocation']
        reallocation_pool = self.pool['nh.clinical.staff.reallocation']
        al_id = allocation_pool.search(cr, uid, [['create_uid', '=', uid]],
                                       order='id desc')
        real_id = reallocation_pool.search(cr, uid, [['create_uid', '=', uid]],
                                           order='id desc')
        allocation = True if al_id else False
        if al_id and real_id:
            al = allocation_pool.browse(cr, uid, al_id[0], context=context)
            real = reallocation_pool.browse(cr, uid, real_id[0],
                                            context=context)
            allocation = True if al.create_date > real.create_date else False
        if not (al_id or real_id) or view_type != 'form':
            return res
        else:
            if allocation:
                allocation = allocation_pool.browse(cr, uid, al_id[0],
                                                    context=context)
                user_ids = [u.id for u in allocation.user_ids]
                res['fields']['nurse_id']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical Nurse Group']]
                ]
                res['fields']['hca_ids']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical HCA Group']]
                ]
            else:
                reallocation = reallocation_pool.browse(cr, uid, real_id[0],
                                                        context=context)
                user_ids = [u.id for u in reallocation.user_ids]
                res['fields']['nurse_id']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical Nurse Group']]
                ]
                res['fields']['hca_ids']['domain'] = [
                    ['id', 'in', user_ids],
                    ['groups_id.name', 'in', ['NH Clinical HCA Group']]
                ]
        return res

class user_allocation_wizard(models.TransientModel):
    _name = 'nh.clinical.user.allocation'

    _stages = [['wards', 'Select Wards'], ['users', 'Select Users'],
               ['allocation', 'Allocation']]

    create_uid = fields.Many2one('res.users',
                                  'User Executing the Wizard')
    stage = fields.Selection(_stages, string='Stage')
    ward_ids = fields.Many2many('nh.clinical.location',
                                 'allocation_ward_rel', 'allocation_id',
                                 'location_id', string='Wards',
                                 domain=[['usage', '=', 'ward']])
    user_ids = fields.Many2many('res.users', 'allocation_user_rel',
                                 'allocation_id', 'user_id',
                                 string='Users')
    allocating_user_ids = fields.Many2many(
        'nh.clinical.allocating', 'allocating_allocation_rel',
        'allocation_id', 'allocating_user_id', string='Allocating Users')

    _defaults = {
        'stage': 'users'
    }
