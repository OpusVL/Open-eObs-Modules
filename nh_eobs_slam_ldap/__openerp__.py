# -*- coding: utf-8 -*-
# pylint: disable=manifest-required-author, manifest-deprecated-key
{
    'name': 'Open e-Obs SLAM Active Directory Configuration',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
    AD configuration module for South London & Maudsley NHS Foundation Trust
    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_eobs_slam', 'nh_clinical_ldap'],
    'data': ['data/slam_master_data.xml'],
    'demo': [],
    'qweb': [],
    'css': [],
    'application': True,
    'installable': True,
    'active': False,
}
