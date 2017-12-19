from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


class SLaMResUsers(osv.osv):
    """ User class. A res.users record models an OpenERP user and is different
        from an employee.

        res.users class now inherits from res.partner. The partner model is
        used to store the data related to the partner: lang, name, address,
        avatar, ... The user model is now dedicated to technical data.
    """
    _name = "res.users"
    _inherit = "res.users"

    _columns = {
        'ldap_authenticated': fields.boolean(
            'User account is authenticated via LDAP/AD?')
    }

    _defaults = {
        'ldap_authenticated': False
    }

    def change_password(self, cr, uid, old_passwd, new_passwd, context=None):
        """Change current user password. Old password must be provided
        explicitly to prevent hijacking an existing user session, or for cases
        where the cleartext password is not used to authenticate requests.

        :return: True
        :raise: openerp.exceptions.AccessDenied when old password is wrong
        :raise: except_osv when password change is attemped on an account
        setup via Active Directory
        :raise: except_osv when new password is not set or empty
        """
        user = self.read(cr, SUPERUSER_ID, uid, ['ldap_authenticated'],
                         context=context)
        if user and user.get('ldap_authenticated'):
            raise osv.except_osv(_('Warning!'), _(
                "Cannot change password for Trust managed account. "
                "Please contact IT to change your password."
            ))
        return super(SLaMResUsers, self).change_password(
            cr, uid, old_passwd, new_passwd, context=context)
