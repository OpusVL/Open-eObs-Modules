# -*- coding: utf-8 -*-

from openerp import models, fields, api


class NhClinicalMaterializedQueue(models.Model):
    _name = 'nh.clinical.materialized.queue'
    _description = "NH Clinical Materialized Queue"

    name = fields.Char()
    view_name = fields.Char()
