# -*- coding: utf-8 -*-
import logging
import requests
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class HagusOrientation(models.Model):
	_name = 'hagus.orientation'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'abbreviation'

	abbreviation = fields.Char(string='Abreviatura')
	description = fields.Char(string='Descripción')

	
	
	
