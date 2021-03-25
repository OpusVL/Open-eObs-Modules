# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging
from functools import wraps

_logger = logging.getLogger(__name__)


def refresh_materialized_views(*views):
    """
    Decorator method to refresh materialized views passed
    as arguments.
    :param views: name(s) of materialized view(s) to refresh
    :return: True if activity is completed
    """
    def _refresh_materialized_views(f):
        @wraps(f)
        def _complete(*args, **kwargs):
            self, cr, uid = args[:3]
            result = f(*args, **kwargs)
            sql = ''
            for view in views:
                sql += 'refresh materialized view ' + view + ';\n'
            cr.execute(sql)
            _logger.debug('Materialized view(s) refreshed')
            return result
        return _complete
    return _refresh_materialized_views


def v8_refresh_materialized_views(*views):
    """
    Decorator method to refresh materialized views passed
    as arguments.
    :param views: name(s) of materialized view(s) to refresh
    :return: True if activity is completed
    """
    def _refresh_materialized_views(f):
        @wraps(f)
        def _complete(*args, **kwargs):
            self = args[0]
            result = f(*args, **kwargs)
            sql = ''
            for view in views:
                sql += 'refresh materialized view ' + view + ';\n'
            self._cr.execute(sql)
            _logger.debug('Materialized view(s) refreshed')
            return result
        return _complete
    return _refresh_materialized_views


def v7_materialized_queue(*views):

    def _add_to_queue(f):
        @wraps(f)
        def _complete(*args, **kwargs):
            self, cr, uid = args[:3]
            result = f(*args, **kwargs)
            for view in views:
                self.pool.get("nh.clinical.materialized.queue").create(cr, uid, {
                    "name": "Refresh {}".format(view),
                    "view_name": view
                }, context={})
            return result
        return _complete
    return _add_to_queue


def v8_materialized_queue(*views):
    def _add_to_queue(f):
        @wraps(f)
        def _complete(*args, **kwargs):
            self = args[0]
            result = f(*args, **kwargs)
            for view in views:
                self.env["nh.clinical.materialized.queue"].create({
                    "name": "Refresh {}".format(view),
                    "view_name": view,
                })
            return result
        return _complete
    return _add_to_queue
