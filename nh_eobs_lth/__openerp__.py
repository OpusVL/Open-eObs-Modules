# -*- encoding: utf-8 -*-
{
    'name': 'Open e-Obs LTH Configuration',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs_mobile'],
    'data': ['lth_master_data.xml',
             'lth_user_data.xml'],
    'qweb': ['static/src/xml/nh_eobs_lth.xml'],
    'application': True,
    'installable': True,
    'active': False,
}