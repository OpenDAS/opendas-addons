# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2007-2013 ASPerience SARL (<http://www.asperience.fr>). 
#    All Rights Reserved
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
#Data model definition
class das_data_model(osv.osv):
	_name = 'das.data.model'
	_columns = {
		'code': fields.char('Code', size=32, required=True),
		'name': fields.char('Name', size=255, required=True),
		'type_fct': fields.selection([('0',_('DAS Server internal')),('1',_('DAS Server external')),('2',_('Workstation internal'))], 'Localisation of data source', select=True),
		'type': fields.selection([('S',_('Static')),('D',_('Dynamic'))], 'Type of data source', select=True),
		#Only for local datas: source of data
		#das_generic, \home\data\fic.csv, ...
		'source': fields.char('Source data model (das_generic, /home/data/fic.csv, ...)', size=255),
		#Numeric, Alpha, EAN, ... 
		'ctrl': fields.selection([('int',_('Integer')),('num',_('Float')),('alpha',_('Numbers and characters')),('alphaMin',_('Lower and upper characters and numbers')),('ean13',_('EAN13')),('ean128',_('EAN 128')),('barre',_('Odoo Barcode'))], 'Validation method', select=True),
#		'ctrl': fields.char('Validation method', size=255),
		#Function name to call source
		'fct_name': fields.char('Function name to call source', size=32),
		'type_select': fields.selection([('0',_('Datas for workstation')),('1',_('Datas for workstation and datas for all workstations'))], 'Specialized datas or specialized and global datas?', select=True),
		#Acquisition methods 
		'acquisition_methods': fields.many2many('das.acquisition.method', 'das_data_model_acquisition_method_rel', 'data_model_id','acquisition_method_id',  'Acquisition methods'),
		'max_length': fields.integer('Maximum length for keyboards'),
		'qty_max': fields.integer('Maximum quantity'),
		'qty_min': fields.integer('Minimum quantity'),
		'parent_id': fields.many2one('das.data.model', 'Parent'),
		'child_ids': fields.one2many('das.data.model', 'parent_id', 'Childs'),
	}
	_defaults = {
		'type_fct': lambda *a: '0',
		'type': lambda *a: 'S',
		'qty_max': lambda *a: -1,
		'qty_min': lambda *a: -1,
	}
das_data_model()

class das_generic(osv.osv):
	_name = 'das.generic'
	_columns = {
		'code': fields.char('Code', size=255, required=True),
		'name': fields.char('Designation', size=255),
		'image': fields.char('Image', size=255),
		'page': fields.integer('Page'),
		'position': fields.integer('Position'),
		'qty_min': fields.integer('Qty min'),
		'qty_max': fields.integer('Qty max'),
		'data_model_id': fields.many2one('das.data.model', 'Data model', required=True),
		'workstation_id': fields.many2one('das.workstation', 'Workstation'),
		'dependencies': fields.many2many('das.generic', 'das_code_dependency', 'code_id','parent_code_id',  'Dependencies'),
	}
das_generic()

class das_consumer_config(osv.osv):
	_name = 'das.consumer.config'
	_columns = {
		#'DAS_Server' or ID of a Talend Server or ID of a workstation (for technical needs) 
		'consumer_id': fields.char('Consumer_id', size=32, required=True),
		#For DAS Server:
		#For a function:
		#For a data_model: fct_name
		'subject': fields.char('Subject_consumer_config', size=255, required=True),
	}
das_consumer_config()

class das_code_dependency(osv.osv):
	_name = 'das.code.dependency'
	_columns = {
#		'data_model_id': fields.many2one('das.data.model', 'Data model', required=True),
		'code_id': fields.many2one('das.generic', 'Code', required=True),
#		'code': fields.char('Code', size=255, required=True),
#		'parent_data_model_id': fields.many2one('das.data.model', 'Parent data model'),
		'parent_code_id': fields.many2one('das.generic', 'Parent Code', required=True),
#		'parent_code': fields.char('Parent code', size=255, required=True),
	}
das_code_dependency()
