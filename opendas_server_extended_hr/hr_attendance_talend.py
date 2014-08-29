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
import netsvc
from osv import osv
from tools.translate import _
logger = netsvc.Logger()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    _columns = {
    }
hr_attendance()

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def talend_get_employee(self, cr, uid, context, filter):
        return self.talend_get_employees_uid(cr, uid, context, filter)
        
    def talend_get_employees_uid(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_employees")
        result = []
        
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            if this.otherid:
                result.append({'id':str(this.otherid),'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_employee_barre(self, cr, uid, context, filter):
        return self.talend_get_employees(cr, uid, context, filter)

    def talend_get_employees(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_employees")
        result = []
        key = "EMPL"
        
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            if this.otherid:
                result.append({'id':key+","+this.otherid,'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_employee_in_barre(self, cr, uid, context, filter):
        return self.talend_get_employees_present(cr, uid, context, filter)

    def talend_get_employees_present(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_employees_present")
        result = []
        key = "EMPL"
        
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            if this.otherid and this.state == 'present':
                result.append({'id':key+","+this.otherid,'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_employee_out_barre(self, cr, uid, context, filter):
        return self.talend_get_employees_absent(cr, uid, context, filter)

    def talend_get_employees_absent(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_employees_absent")
        result = []
        key = "EMPL"
        
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            if this.otherid and this.state == 'absent':
                print "this.",this.state
                result.append({'id':key+","+this.otherid,'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}   
    
    def talend_get_employee_in_workcenter_barre(self, cr, uid, context, filter):
        return self.talend_get_active_employee_pool_in_workcenter(cr, uid, context, filter)

    def talend_get_active_employee_pool_in_workcenter(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_active_employee_pool_in_workcenter")
        result = []
        key = "EMPL"
        
        if 'workcenter_ext' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
    
        workcenter_ids = self.pool.get('mrp.workcenter').search(cr,uid,[('otherid','=',context['workcenter_ext'][0])])
        if len(workcenter_ids) == 0 :
            return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
        if len(workcenter_ids) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}
    
        workcenter = self.pool.get('mrp.workcenter').browse(cr,uid,workcenter_ids[0])
        for this in workcenter.employee_pool_ids:
            if this.otherid and this.active:
                result.append({'id':key+","+this.otherid,'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_employee_out_workcenter_barre(self, cr, uid, context, filter):
        return self.talend_get_active_employee_pool_in_workcenter_not_in(cr, uid, context, filter)
    
    def talend_get_active_employee_pool_in_workcenter_not_in(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_active_employee_pool_in_workcenter_not_in")
        result = []
        key = "EMPL"
        
        if 'workcenter_ext' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
    
        workcenter_ids = self.pool.get('mrp.workcenter').search(cr,uid,[('otherid','=',context['workcenter_ext'][0])])
        if len(workcenter_ids) == 0 :
            return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
        if len(workcenter_ids) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}
    
        workcenter = self.pool.get('mrp.workcenter').browse(cr,uid,workcenter_ids[0])
        employee_attendance_ids_set = set([employee.id for employee in workcenter.employee_attendance_ids])
        employee_ids_set = set([employee.id for employee in workcenter.employee_pool_ids])

        employee_ids = list(employee_ids_set-employee_attendance_ids_set)

        for this in self.browse(cr,uid,employee_ids):
            if this.otherid and this.active:
                result.append({'id':key+","+this.otherid,'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}   
    
    def talend_get_workcenter(self, cr, uid, context, filter):
        return self.talend_get_workcenters(cr, uid, context, filter)
    
    def talend_get_workcenters(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_workcenters")
        result = []
        workcenter_obj = self.pool.get('mrp.workcenter')
        for this in workcenter_obj.browse(cr,uid,workcenter_obj.search(cr,uid,filter)):
            result.append({'id':str(this.code),'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_workcenter_in(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_workcenter_in")
        result = []
        key = "EMPL"

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        
        tmp = context['employee'][0].split(',')
        if len(tmp) != 2 :
            return {"code":2,"string":_("Error, employee id"),"object":[]}
        if key != tmp[0] :
            return {"code":2,"string":_("Error, This is not an employee"),"object":[]}
         
        id = self.pool.get('hr.employee').search(cr, uid, [('otherid', '=', int(tmp[1]))])
        all_emp_actions = self.pool.get('hr.employee').get_action(cr,uid, id)
        actions = {}
        if id[0] in all_emp_actions :
            actions = all_emp_actions[int(id[0])]
        print "#"*50
        print actions
        print "#"*50
        workcenter_obj = self.pool.get('mrp.workcenter')
        for this in workcenter_obj.browse(cr,uid,workcenter_obj.search(cr,uid,filter)):
            idw = self.pool.get('mrp.workcenter').search(cr, uid, [('code', '=', this.code)])
            print "*"*50
            print idw
            print "*"*50
            if 'mrp.workcenter' in actions and idw[0] in actions['mrp.workcenter'] :
                result.append({'id':str(this.code),'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_workcenter_out(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_workcenter_out")
        result = []
        key = "EMPL"

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        
        tmp = context['employee'][0].split(',')
        if len(tmp) != 2 :
            return {"code":2,"string":_("Error, employee id"),"object":[]}
        if key != tmp[0] :
            return {"code":2,"string":_("Error, This is not an employee"),"object":[]}
         
        id = self.pool.get('hr.employee').search(cr, uid, [('otherid', '=', int(tmp[1]))])
        all_emp_actions = self.pool.get('hr.employee').get_action(cr,uid, id)
        actions = {}
        if id[0] in all_emp_actions :
            actions = all_emp_actions[int(id[0])]
        print "#"*50
        print actions
        print "#"*50
        workcenter_obj = self.pool.get('mrp.workcenter')
        for this in workcenter_obj.browse(cr,uid,workcenter_obj.search(cr,uid,filter)):
            idw = self.pool.get('mrp.workcenter').search(cr, uid, [('code', '=', this.code)])
            print "*"*50
            print idw
            print "*"*50
            if len(actions) == 0 or 'mrp.workcenter' in actions and idw[0] not in actions['mrp.workcenter']:
                result.append({'id':str(this.code),'name':this.name})
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_workcenter_line(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_workcenter_line")
        result = []
        
        if 'workcenter' in context and context['workcenter'] :
            workcenter_ids = self.pool.get('mrp.workcenter').search(cr,uid,[('code','=',context['workcenter'][0])])
            if len(workcenter_ids) == 0 :
                return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
            if len(workcenter_ids) > 1 :
                return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}  
        
            filter.append(('workcenter_id','in',workcenter_ids))
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for this in workcenter_line_obj.browse(cr,uid,workcenter_line_obj.search(cr,uid,filter)):
            result.append({'id':str(this.id),'name':this.name,'parent_id':str(this.workcenter_id.otherid) or False })

        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_groups_by_employee(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_get_groups_by_employee")        
        key = "EMPL"
        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if len(context['employee']) == 0:
            return {"code":2,"string":_("Error, no employee transmited"),"object":[]}
        if len(context['employee']) > 1:
            return {"code":2,"string":_("Error, more than one employee transmited"),"object":[]}

        tmp_context = []
        for i in context['employee']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, employee id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an employee"),"object":[]}
            tmp_context.append(str(tmp[1]))
        filter.append(('otherid','in',tmp_context))
        
        result = []
        temp = {}        
        employee_ids = self.search(cr,uid,filter)
        for this in self.browse(cr,uid,employee_ids):
            if this.user_id and this.user_id.active :
                for group in this.user_id.groups_id:
                    print "group.id :",group.name," group.name :",group.name
                    temp = {
                        "id":group.name,
                        "ean13":False,
                        "name":group.name,
                    }
                    result.append(temp)
        #TODO: retirer ceci
        temp = {
            "id":"userok",
            "name":"userok",
        }
        result.append(temp)
        return {"code":0,"string":_("OK"),"object":result}
        
    def talend_in_out(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_in_out")

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        
        employee_ids = self.pool.get('hr.employee').search(cr,uid,[('otherid','in',context['employee'])])
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        if len(employee_ids) > 1 :
            return {"code":2,"string":_("Error, more than one employee found "),"object":[]}
        
        result = ""
        for employee_id in employee_ids:
            employee = self.pool.get("hr.employee").browse(cr,uid,employee_id)
            if employee.state == 'present':
                employee.sign_out()
                result += employee.name+_(" : Output \n")
            else:
                employee.sign_in()
                result += employee.name+_(" : Input \n")
                
        return {"code":0,"string":result,"object":[]}
    
    def talend_in_out_barre(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_in_out_barre")
        key = "EMPL"

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}

        if len(context['employee']) == 0:
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        if len(context['employee']) > 1:
            return {"code":2,"string":_("Error, more than one employee found "),"object":[]}

        tmp_context = []
        for i in context['employee']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, employee id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an employee"),"object":[]}
            tmp_context.append(str(tmp[1]))
        filter.append(('otherid','in',tmp_context))
        
        employee_ids = self.pool.get('hr.employee').search(cr,uid,filter)
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        if len(employee_ids) > 1 :
            return {"code":2,"string":_("Error, more than one employee found "),"object":[]}
        
        result = ""
        for employee_id in employee_ids:
            employee = self.pool.get("hr.employee").browse(cr,uid,employee_id)
            if employee.state == 'present':
                employee.sign_out()
                result += employee.name+_(" : Output \n")
            else:
                employee.sign_in()
                result += employee.name+_(" : Input \n")
                
        return {"code":0,"string":result,"object":[]}
        
    def talend_login_workcenter_barre(self, cr, uid, context, filter):
        return self.talend_login_workcenter(cr, uid, context, filter)
    
    def talend_login_workcenter(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_login_workcenter")
        print context
        print filter
        key = "EMPL"
        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if len(context['employee']) == 0:
            return {"code":2,"string":_("Error, no employee transmited"),"object":[]}
        if len(context['employee']) > 1:
            return {"code":2,"string":_("Error, more than one employee transmited "),"object":[]}

        tmp_context = []
        for i in context['employee']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, employee id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an employee"),"object":[]}
            tmp_context.append(str(tmp[1]))
        filter.append(('otherid','in',tmp_context))
        
        if 'workcenter_ext' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
    
        employee_ids = self.pool.get('hr.employee').search(cr,uid,filter)
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        if len(employee_ids) > 1 :
            return {"code":2,"string":_("Error, more than one employee found"),"object":[]}        
        
        workcenter_ids = self.pool.get('mrp.workcenter').search(cr,uid,[('otherid','=',context['workcenter_ext'][0])])
        if len(workcenter_ids) == 0 :
            return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
        if len(workcenter_ids) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}        
                
        result = self.work_change(cr,uid,employee_ids,{'model':"mrp.workcenter",'id':workcenter_ids[0]})
        return {"code":0,"string":result,"object":[]}
     
    def talend_change_workcenter_barre(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_change_workcenter_barre")
        key = "EMPL"

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if len(context['employee']) == 0:
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        if len(context['employee']) > 1:
            return {"code":2,"string":_("Error, more than one employee found "),"object":[]}

        tmp_context = []
        for i in context['employee']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, employee id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an employee"),"object":[]}
            tmp_context.append(str(tmp[1]))
        filter.append(('otherid','in',tmp_context))
        
        if 'workcenter' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
    
        employee_ids = self.pool.get('hr.employee').search(cr,uid,filter)
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        
        workcenter_ids = self.pool.get('mrp.workcenter').search(cr,uid,[('code','=',context['workcenter'][0])])
        if len(workcenter_ids) == 0 :
            return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
        if len(workcenter_ids) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}        
         
        result = self.work_change(cr,uid,employee_ids,{'model':"mrp.workcenter",'id':workcenter_ids[0]})
        return {"code":0,"string":result,"object":[]}
    
    def talend_change_workcenter_line_barre(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_change_workcenter_line_barre")
        key = "EMPL"

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if len(context['employee']) == 0:
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        if len(context['employee']) > 1:
            return {"code":2,"string":_("Error, more than one employee found "),"object":[]}

        tmp_context = []
        for i in context['employee']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, employee id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an employee"),"object":[]}
            tmp_context.append(str(tmp[1]))
        filter.append(('otherid','in',tmp_context))
        
        if 'workcenter' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
        if 'production' not in context :
            return {"code":2,"string":_("Error, production not in context"),"object":[]}
        if 'adjustment' not in context :
            return {"code":2,"string":_("Error, adjustment not in context"),"object":[]}
    
        employee_ids = self.pool.get('hr.employee').search(cr,uid,filter)
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        
        workcenter_line_id = self.pool.get('mrp.production.workcenter.line').search(cr,uid,[('id','=',context['production'][0])])
        if len(workcenter_line_id) == 0 :
            return {"code":2,"string":_("Error, no workcenter line found"),"object":[]}
        if len(workcenter_line_id) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter line found"),"object":[]}  
        workcenter_line_id = workcenter_line_id[0]    
        
        result = self.work_change(cr,uid,employee_ids,{'model':"mrp.production.workcenter.line",'id':workcenter_line_id,'tps':eval(context['adjustment'][0])})
        return {"code":0,"string":result,"object":[]}
    
    def talend_change_workcenter(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_change_workcenter")
        
        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if 'workcenter' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
    
        employee_ids = self.pool.get('hr.employee').search(cr,uid,[('otherid','in',context['employee'])])
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        
        workcenter_ids = self.pool.get('mrp.workcenter').search(cr,uid,[('code','=',context['workcenter'][0])])
        if len(workcenter_ids) == 0 :
            return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
        if len(workcenter_ids) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}        
                
        result = self.work_change(cr,uid,employee_ids,{'model':"mrp.workcenter",'id':workcenter_ids[0]})
        return {"code":0,"string":result,"object":[]}
    
    def talend_change_workcenter_line(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_change_workcenter_line")

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if 'workcenter' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
        if 'production' not in context :
            return {"code":2,"string":_("Error, production not in context"),"object":[]}
        if 'adjustment' not in context :
            return {"code":2,"string":_("Error, adjustment not in context"),"object":[]}
    
        employee_ids = self.pool.get('hr.employee').search(cr,uid,[('otherid','in',context['employee'])])
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        
        workcenter_line_id = self.pool.get('mrp.production.workcenter.line').search(cr,uid,[('id','=',context['production'][0])])
        if len(workcenter_line_id) == 0 :
            return {"code":2,"string":_("Error, no workcenter line found"),"object":[]}
        if len(workcenter_line_id) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter line found"),"object":[]}  
        workcenter_line_id = workcenter_line_id[0]    
        
        result = self.work_change(cr,uid,employee_ids,{'model':"mrp.production.workcenter.line",'id':workcenter_line_id,'tps':eval(context['adjustment'][0])})
        return {"code":0,"string":result,"object":[]}
    
    def talend_maintenance(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_maintenance")

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if 'workcenter' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
    
        employee_ids = self.pool.get('hr.employee').search(cr,uid,[('otherid','in',context['employee'])])
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        
        workcenter_id = self.pool.get('mrp.workcenter').search(cr,uid,[('code','=',context['workcenter'][0])])
        if len(workcenter_id) == 0 :
            return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
        if len(workcenter_id) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}       
        workcenter_id = workcenter_id[0]
        
        all_emp_actions = self.pool.get('hr.employee').get_action(cr,uid,self.pool.get('hr.employee').search(cr,uid,[]))
        maintenance_ids_to_stop = []
        all_maintenance_ids_to_stop = []
        for emp_id in all_emp_actions :
            if 'mrp.workcenter.maintenance' in all_emp_actions[emp_id] :
                for line in all_emp_actions[emp_id]['mrp.workcenter.maintenance']:
                    maintenance = self.pool.get('mrp.workcenter.maintenance').browse(cr,uid,line)
                    if maintenance.workcenter_id and maintenance.workcenter_id.id == workcenter_id :
                        maintenance_ids_to_stop.append(line)
                    else:
                        all_maintenance_ids_to_stop.append(line)
                            
        result = ""
        
        for all_maintenance_id_to_stop in all_maintenance_ids_to_stop :
            result += self.work_change(cr,uid,employee_ids,{'model':"mrp.workcenter.maintenance",'id':all_maintenance_id_to_stop})+"\n"
        
        if len(maintenance_ids_to_stop) > 0 :
            for maintenance_id_to_stop in maintenance_ids_to_stop :
                result += self.work_change(cr,uid,employee_ids,{'model':"mrp.workcenter.maintenance",'id':maintenance_id_to_stop})+"\n"
        else :
            workcenter = self.pool.get('mrp.workcenter').browse(cr,uid,workcenter_id)[0]
            maintenance_id = self.pool.get('mrp.workcenter.maintenance').create(cr,uid,{'name': 'maintenance_'+workcenter.name ,'workcenter_id':workcenter.id})
            result += self.work_change(cr,uid,employee_ids,{'model':"mrp.workcenter.maintenance",'id':maintenance_id})+"\n"
        
        return {"code":0,"string":result,"object":[]}
    
    def talend_controle_iso(self, cr, uid, context, filter):
        logger.notifyChannel("opendas", netsvc.LOG_DEBUG,"talend_controle_iso")

        if 'employee' not in context :
            return {"code":2,"string":_("Error, employee not in context"),"object":[]}
        if 'workcenter' not in context :
            return {"code":2,"string":_("Error, workcenter not in context"),"object":[]}
        if 'production' not in context :
            return {"code":2,"string":_("Error, production not in context"),"object":[]}
        if 'qty_ok' not in context :
            return {"code":2,"string":_("Error, quantity ok not in context"),"object":[]}
        if 'qty_false' not in context :
            return {"code":2,"string":_("Error, quantity not ok not in context"),"object":[]}
        
        employee_ids = self.pool.get('hr.employee').search(cr,uid,[('otherid','in',context['employee'])])
        if len(employee_ids) == 0 :
            return {"code":2,"string":_("Error, no employee found"),"object":[]}
        
        workcenter_ids = self.pool.get('mrp.workcenter').search(cr,uid,[('code','=',context['workcenter'][0])])
        if len(workcenter_ids) == 0 :
            return {"code":2,"string":_("Error, no workcenter found"),"object":[]}
        if len(workcenter_ids) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter found"),"object":[]}        

        workcenter_id = workcenter_ids[0]
        
        workcenter_line_id = self.pool.get('mrp.production.workcenter.line').search(cr,uid,[('id','=',context['production'][0])])
        if len(workcenter_line_id) == 0 :
            return {"code":2,"string":_("Error, no workcenter line found"),"object":[]}
        if len(workcenter_line_id) > 1 :
            return {"code":2,"string":_("Error, more than one workcenter line found"),"object":[]}        

        workcenter_line_id = workcenter_line_id[0]

        qty_ok = eval(context['qty_ok'][0])
        qty_false = eval(context['qty_false'][0])   
        
        employee_ids = self.pool.get('hr.employee').search(cr,uid,[])
        all_emp_actions = self.pool.get('hr.employee').get_action(cr,uid,employee_ids)

        employee_ids_to_stop = []
        for emp_id in all_emp_actions :
            if 'mrp.workcenter' in all_emp_actions[emp_id] and workcenter_id in all_emp_actions[emp_id]['mrp.workcenter']:
                employee_ids_to_stop.append(emp_id)
        
        context_send = {
                        'model':"mrp.workcenter",
                        'id':workcenter_line_id
        }
        context_send["action_after"] = [
                "wf_service.trg_validate(uid, 'mrp.production.workcenter.line', "+str(workcenter_line_id)+", 'button_resume', cr)",
                "self.pool.get('mrp.production.workcenter.line').write(cr,uid,"+str(workcenter_line_id)+",{'qty_false':"+str(qty_false)+",'qty_ok':"+str(qty_ok)+"})",
                "wf_service.trg_validate(uid, 'mrp.production.workcenter.line', "+str(workcenter_line_id)+", 'button_done', cr)"
        ]
        result = self.work_change(cr,uid,employee_ids_to_stop,context_send)
        
        return {"code":0,"string":result,"object":[]}
    
hr_employee()

