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

class das_type_material(osv.osv):
    _name = 'das.type.material'
    _columns = {
        'code': fields.char('Material type', size=6, required=True),
        'name': fields.char('Name type material', size=60, required=True),
#        'description': fields.char('Description', size=255),
    }
das_type_material()

class das_model_material(osv.osv):
    _name = 'das.model.material'
    _columns = {
        'code': fields.char('Material model', size=32, required=True),
        'name': fields.char('Name material model', size=60, required=True),
        'type_material_id': fields.many2one('das.type.material', 'Material type'),
        'constructor_material_id': fields.many2one('res.partner', 'Material constructor'), 
        'description': fields.text('Description'),
    }
das_model_material()

class das_acquisition_method(osv.osv):
    _name = 'das.acquisition.method'
    _columns = {
        'code': fields.selection([('displayScreen',_('Display screen')),('displayKeyboard',_('Display keyboard')),('listenTypeMaterial',_('Listen material type'))], 'Acquisition method', required=True, select=True),
        #TODO: type_material_id devient required si code = listenTypeMaterial
        'type_material_id': fields.many2one('das.type.material', 'Material type'),
        'name': fields.char('Designation', size=255),
    }
das_acquisition_method()

#class das_data_model(osv.osv):
#    _inherit = 'das.data.model'
#    _columns = {
#        #Acquisition methods
#       'acquisition_methods': fields.many2many('das.acquisition.method', 'das_data_model_acquisition_method_rel', 'data_model_id','acquisition_method_id',  'Acquisition methods'),
#    }
#das_data_model()

class das_type_workstation(osv.osv):
    _name = 'das.type.workstation'
    _columns = {
        'code': fields.char('Type workstation', size=6, required=True),
        'name': fields.char('Name', size=60, required=True),
        'description': fields.char('Description', size=255),
    }
das_type_workstation()

class das_transmit_protocol(osv.osv):
    _name = 'das.transmit.protocol'
    _columns = {
        'code': fields.char('Code', size=32, required=True),
        'name': fields.char('Name', size=60, required=True),
        'description': fields.text('Description'),
    }
das_transmit_protocol()

class das_dialog(osv.osv):
    _name = 'das.dialog'
    _columns = {
        #'dialog_id': fields.many2one('das.config.material', 'Dialog', required=True),
        'name': fields.char('Name', size=60, required=True),
        'send_receive_data': fields.char('Send/receive data', size=255),
        'header_code': fields.char('header_code', size=255),
        'priority': fields.integer('Priority', required=True),
        'waiting_second': fields.integer('Waiting seconds'),
        'send': fields.integer('Send'),
        'start_char_position': fields.integer('Start charposition'),
        'stop_char_position': fields.integer('Stop char position'),
        'description': fields.text('Description'),
        #'das_config_type_material_ids': fields.many2many('das.config.type.material', 'das_config_type_material_dialog_rel', 'dialog_id', 'config_type_material_id', 'Configuration types'),
    }
das_dialog()

class das_label (osv.osv):
    _name = 'das.label'
    _columns = {
        'code': fields.char("Code",required=True, size=32),
        'name': fields.char("Name", required=True, size=255),
        'label_source': fields.text("Label source", required=True),       
    }
das_label()

class das_config_type_material(osv.osv):
    _name = 'das.config.type.material'
    _columns = {
        'code': fields.char('Code', size=32, required=True),
        'name': fields.char('Description', size=255, required=True),
        'issimple': fields.boolean('Is simple'),
        'iscumulative': fields.boolean('Is cumulative'),
        'transmit_protocol_id': fields.many2one('das.transmit.protocol', 'Transmit protocol'),
        'dialog_ids': fields.many2many('das.dialog', 'das_config_type_material_dialog_rel', 'config_type_material_id','dialog_id',  'Dialogs'),
        'port_type': fields.selection([('rj45','RJ45'),('com','COM'),('usb','USB')], 'Type port', required=True, select=True),
        'speed': fields.char('Speed', size=10),
        'parity': fields.char('Parity', size=10),
        'stop_bit': fields.char('Stop_bit', size=10),
        'databit': fields.char('Databit', size=2),
        'flow_control': fields.char('Flow_control', size=10),
        'type_transmit_protocol_line': fields.one2many('das.type.transmit.protocol','config_type_material_id','Config type material id'),
    }
    
    _defaults = {
                 
    }

das_config_type_material()

class das_type_transmit_protocol(osv.osv):
    _name = 'das.type.transmit.protocol'
    _columns = {
        'sequence': fields.integer('Sequence',required=True),
        'config_type_material_id' : fields.many2one('das.config.type.material','Config type material'),
        'type': fields.selection([('e','Emission'),('r','Reception'),('c','Calcul')], 'Transmit type', required=True, select=True),
        'name': fields.text('Expression',required=True),
        'language': fields.selection([('JavaScript','JavaScript'),('JRuby','JRuby'),('Jython','Jython')], 'Language'),
    }
    _defaults = {
        'sequence': lambda *a:1,
    }
    _order='sequence'
    
    
das_type_transmit_protocol()