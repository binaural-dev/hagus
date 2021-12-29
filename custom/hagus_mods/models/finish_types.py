# -*- coding: utf-8 -*-
import logging
import requests
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class HagusFinishTypes(models.Model):
	_name = 'hagus.finish.types'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'description'

	description = fields.Char(string='Descripción')

	
	
	
