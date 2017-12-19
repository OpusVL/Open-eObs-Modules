from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import Session
import openerp.modules as addons
from openerp.tools.translate import _
import operator


class MainSession(Session):
    """
    A class to change the nh_eobs_api.controllers.routes method
    """

    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        """
        Override the change_password endpoint of the JSON-RPC API used by the
        Odoo frontend
        :param fields: submitted fields
        :return: the new password or an error
        """
        old_password, new_password, confirm_password = \
            operator.itemgetter('old_pwd', 'new_password', 'confirm_pwd')(
                dict(map(operator.itemgetter('name', 'value'), fields)))
        password_set = old_password.strip() and new_password.strip() and \
            confirm_password.strip()
        if not password_set:
            return {'error': _('You cannot leave any password empty.'),
                    'title': _('Change Password')}
        if new_password != confirm_password:
            return {
                'error': _('The new password and its confirmation '
                           'must be identical.'),
                'title': _('Change Password')
            }
        try:
            if request.session.model('res.users').change_password(
                    old_password, new_password):
                return {'new_password': new_password}
        except Exception as e:
            if 'Trust managed account' in e.value:
                return {'error': _(e.value),
                        'title': _(e.name)}
            return {'error': _(
                'The old password you provided is incorrect, '
                'your password was not changed.'),
                'title': _('Change Password')}
        return {'error': _('Error, password not changed !'),
                'title': _('Change Password')}

    def __init__(self):
        loaded = addons.module.loaded
        if 'nh_eobs_slam_ldap' in loaded:
            Session.change_password = self.change_password
        super(MainSession, self).__init__()
