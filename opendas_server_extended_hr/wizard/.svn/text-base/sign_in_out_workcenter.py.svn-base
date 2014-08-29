# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2007-2013 ASPerience SARL (<http://www.asperience.fr>). 
#    All Rights Reserved
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
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
import wizard
import pooler

parameter_form_si = '''<?xml version="1.0"?>
<form string="Event" colspan="4">
    <field name="employee_id" colspan="4"/>
    <field name="model"/>
</form>'''

parameter_fields = {
    'model' : {'string':"model",'type':'reference', "selection":[('project.project','Project'),('mrp.workcenter','Workcenter'),('mrp.production.workcenter.line','Production'),('mrp.workcenter.maintenance','Maintenance'),('mrp.production.workcenter.line.subwork','Workcenter Line')]},
    'employee_id': {'string': 'Employee', 'type': 'many2one', 'relation': 'hr.employee', 'required': True},
    
}

class wiz_si_so_wc(wizard.interface):
    
    def _get_defaults(self, cr, uid, data, context):
        if 'ids' in data and data['ids']:
            emp_id = pooler.get_pool(cr.dbname).get('hr.employee').search(cr, uid, [('id','in',data['ids'])])
            if emp_id and isinstance(emp_id,list):
                emp_id = emp_id[0]
        elif 'id' in data and data['id']:
            emp_id = pooler.get_pool(cr.dbname).get('hr.employee').search(cr, uid, [('id','=',data['id'])])
            if emp_id and isinstance(emp_id,list):
                emp_id = emp_id[0]

        if not emp_id:
            emp_id = pooler.get_pool(cr.dbname).get('hr.employee').search(cr, uid, [('user_id', '=', uid)])
            if emp_id and isinstance(emp_id,list):
                emp_id = emp_id[0]
        data['form']['employee_id'] = emp_id
        data['form']['model'] = False
        return data['form']
    
    def _state_check(self, cr, uid, data, context):
        return 'si'
    
    def _sign(self, cr, uid, data, context):
        model = data['form']['model'].split(',')[0]
        id = eval(data['form']['model'].split(',')[1])
        pooler.get_pool(cr.dbname).get('hr.employee').work_change(cr,uid,data['form']['employee_id'],{"model":model , "id":id})
        return {}
    
    states = {
        'init' : {
                'actions' : [],
                'result' : {'type' : 'choice', 'next_state': _state_check}
        },
        'si': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch':parameter_form_si, 'fields': parameter_fields, 'state':[('done', 'Ok'),('end','Cancel')]}
        },
        'done': {
            'actions': [_sign],
            'result': {'type' : 'state', 'state':'init'}
        },

    }
wiz_si_so_wc('si_so_wc')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

