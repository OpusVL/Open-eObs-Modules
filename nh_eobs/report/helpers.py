# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


class DataObj(object):
    def __init__(self, spell_id=None, start_time=None, end_time=None,
                 ews_only=None):
        self.spell_id = spell_id
        self.start_time = start_time
        self.end_time = end_time
        self.ews_only = ews_only


class BaseReport(object):
    def __init__(self, user, company_name, company_logo, time_generated):
        self.time_generated = time_generated
        self.footer_values = {
            'company_logo': company_logo,
            'time_generated': time_generated,
            'hospital_name': company_name,
            'user_name': user
        }


class ReportDates(object):
    def __init__(self, report_start, report_end, spell_start, spell_end):
        self.report_start = report_start
        self.report_end = report_end
        self.spell_start = spell_start
        self.spell_end = spell_end


def create_search_filter(spell_activity_id, model,
                         start_datetime, end_datetime,
                         states='completed',
                         date_field='effective_date_terminated'):
    if not spell_activity_id:
        raise ValueError('No spell activity id supplied.')
    if not model:
        raise ValueError('No model supplied.')

    domain = [('parent_id', '=', spell_activity_id),
              ('data_model', '=', model)]
    if states:
        operator = 'in' if isinstance(states, list) else '='
        domain.append(['state', operator, states])
    if start_datetime:
        if isinstance(start_datetime, datetime):
            domain.append([date_field, '>=', start_datetime.strftime(dtf)])
        elif isinstance(start_datetime, str):
            domain.append([date_field, '>=', start_datetime])

    if end_datetime:
        if isinstance(end_datetime, datetime):
            domain.append([date_field, '<=', end_datetime.strftime(dtf)])
        elif isinstance(end_datetime, str):
            domain.append([date_field, '<=', end_datetime])
    return domain


# TODO method only used in tests and lister now, can remove.
def convert_db_date_to_context_date(cr, uid, date_string, dformat,
                                    context=None):
    if dformat:
        return fields.datetime.context_timestamp(
            cr, uid, date_string, context=context).strftime(dformat)
    else:
        return fields.datetime.context_timestamp(
            cr, uid, date_string, context=context)


def data_dict_to_obj(data_dict):
    spell_id = None
    start = None
    end = None
    ews_only = None
    if 'spell_id' in data_dict and data_dict['spell_id']:
        spell_id = data_dict['spell_id']
    if 'start_time' in data_dict and data_dict['start_time']:
        start = data_dict['start_time']
    if 'end_time' in data_dict and data_dict['end_time']:
        end = data_dict['end_time']
    if 'ews_only' in data_dict and data_dict['ews_only']:
        ews_only = data_dict['ews_only']
    return DataObj(spell_id, start, end, ews_only)


def boolean_to_text(value):
    value_as_text = 'No'
    if value:
        value_as_text = 'Yes'
    return value_as_text
