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

def _mask_get(self, cr, uid, context={}):
    obj = self.pool.get('das.mask')
    ids = obj.search(cr, uid, [])
    res = obj.read(cr, uid, ids, ['name','code'], context)
    return [(r['code'], r['name']) for r in res]
   
class das_mask(osv.osv):
    _name = 'das.mask'
    _columns = {
        'name': fields.char('Name', size=60),
        'code': fields.char('Code', size=32, required=True),
        'description': fields.text('Description'),
    }
das_mask()

class das_material(osv.osv):
    _name = 'das.material'
    _columns = {
		'code': fields.char('Code', size=32, required=True),
		'name': fields.char('Name', size=60, required=True),
		'model_material_id': fields.many2one('das.model.material', 'Material model'),
#		'description': fields.char('Description', size=255),
	}
das_material()

class das_graphical_configuration(osv.osv):
    _name = 'das.graphical.configuration'
    _columns = {
        'name': fields.char('Name', size=60),
#        'workstation_ids': fields.many2many('das.workstation', 'workstation_graphical_configuration_rel', 'graphical_configuration_id','workstation_id',  'Workstations'),
#TODO: à transformer en anglais et globaliser les noms
        'mask': fields.selection(_mask_get, 'Mask type', size=32),
        'graphical_xml': fields.text('Graphical_xml'),
    }
das_graphical_configuration()



class das_functional_configuration(osv.osv):
    _name = 'das.functional.configuration'
    _columns = {
        'name': fields.char('Name', size=60),
#        'workstation_ids': fields.many2many('das.workstation', 'workstation_functional_configuration_rel', 'functional_configuration_id','workstation_id',  'Workstations'),
#TODO: cf ci-dessus
        'mask': fields.selection(_mask_get, 'Mask type', size=32),
        'button_xml': fields.text('Buttons'),
        'button_bottom_xml': fields.text('Bottom Buttons'),
        'function_xml': fields.text('Functions'),
        'keyboard_xml': fields.text('Keyboard'),
    }
das_functional_configuration()



class das_workstation(osv.osv):
    _name = 'das.workstation'
    _columns = {
		'code': fields.char('Code', size=32, required=True),
		'name': fields.char('Name', size=60, required=True),
		'type_workstation_id': fields.many2one('das.type.workstation', 'Workstation type'),
		'constructor_material_id': fields.many2one('res.partner', 'Material constructor'), 
		'description': fields.text('Description'),
		'os_id': fields.many2one('das.os', 'Os'), 
		'os_user': fields.char('Os user', size=32),
		'os_password': fields.char('Os password', size=32),
		'ip_id': fields.char('Ip', size=32),
		'mac_address': fields.char('Mac address', size=32),
		'location': fields.char('Location', size=32),
		'phone_number': fields.char('Phone number', size=10),
		'hour_start_activity': fields.char('Hour of start activity', size=5),
		'hour_stop_activity': fields.char('Hour of stop activity', size=5),
		'force_pdf': fields.boolean('Force pdf'),
#A prior : à supprimer
#		'mask': fields.char('Mask', size=32),
#		'gui_xml': fields.text('Gui_xml'),
		'application_user': fields.char('Application user', size=32),
		'application_password': fields.char('Application password', size=32),
#		'activemq_user': fields.char('Activemq user', size=32),
#		'activemq_password': fields.char('Activemq password', size=32),
#		'activemq_url': fields.char('Activemq url', size=255),
        'config_ids':fields.one2many('das.config.material', 'workstation_id', 'Materials'),
		'graphical_configuration_ids': fields.many2many('das.graphical.configuration', 'das_workstation_das_graphical_configuration', 'workstation_id', 'graphical_configuration_id', 'Graphical configurations'),
		'functional_configuration_ids': fields.many2many('das.functional.configuration', 'das_workstation_das_functional_configuration', 'workstation_id', 'functional_configuration_id', 'Functional configurations'),
        }
das_workstation()

#Table permettant de définir les configs de appareils connectés sur les postes de travail
#Elle permet de définir une séquence de caractères ￃﾠ envoyer. Exemple demande de poids ￃﾠ une balance
#Receive Data est le métalangage du champ reￃﾧu d'un appareil. ex:  
#Les champs Start et Stop correspondent ￃﾠ la position début et Fin interessante, dans la chaￃﾮne de caratère reￃﾧue
class das_config_material(osv.osv):
    _name = 'das.config.material'
    _columns = {
        'code': fields.char('Code', size=32, required=True),
        'name': fields.char('Name', size=60, required=True),
        'workstation_id': fields.many2one('das.workstation', 'Workstation'),
        'material_id': fields.many2one('das.material', 'Material'),
        'config_type_material_id': fields.many2one('das.config.type.material', 'Configuration type'),
        'port': fields.char('Port', size=255),
        'description': fields.text('Description'),
    }
das_config_material()

class das_template_supervision(osv.osv):
    _name = 'das.template.supervision'
    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'mapping': fields.text('Mapping'),
        'nb_case_x': fields.integer('nb_case_x'),
        'nb_case_y': fields.integer('nb_case_y'),
        'width_case': fields.integer('width_case'),
        'height_case': fields.integer('height_case'),
        'image': fields.char('Image', size=60),
    }

das_template_supervision()