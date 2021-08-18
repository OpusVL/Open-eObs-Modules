# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'NH eObs ADT GUI',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'Permits ADT Operations through the GUI',
    'description': """     """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': [
        "nh_eobs",
        "nh_clinical",
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Wizards
        'wizards/nh_clinical_patient_merge_wizard_views.xml',

        # Views
        'views/spell_management_views.xml',
        'views/menuitem.xml',
        'views/spell_patient_views.xml',
        'views/nh_clinical_patient_views.xml',
    ],
    'application': True,
    'installable': True,
    'active': False,
}
