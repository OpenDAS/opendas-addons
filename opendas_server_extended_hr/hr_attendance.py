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
import datetime
import time
import openerp.netsvc
import logging
import logging.handlers
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import ustr

logger = logging.getLogger(__name__)

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    _columns = {
        'object_id' : fields.reference('Object', selection=[('project.project','Project'),('project.task.work','Project task work'),('mrp.workcenter','Workcenter'),('mrp.production.workcenter.line','Production'),('mrp.production.workcenter.line.subwork','Workcenter Line'),('mrp.workcenter.maintenance','Maintenance'),('hr.subwork','HR Subwork')], size=64),
    }
    
    def _altern_si_so(self, cr, uid, ids):
        logger.debug("opendas hr : _altern_si_so %s",(ids,))
        for id in ids:
            sql = '''
            select action, name, id
            from hr_attendance as att
            where employee_id = (select employee_id from hr_attendance where id=%s)
            and action in ('sign_in','sign_out')
            and name <= (select name from hr_attendance where id=%s)
            order by name desc
            limit 2
            ''' % (id, id)

            cr.execute(sql)
            atts = cr.fetchall()
            logger.debug("opendas hr : _altern_si_so %s", (atts,))
            
            print "*"*60
            
#              if len(atts > 0):        
#                 if (len(atts) == 1 and atts[0][0] == 'sign_in') or (len(atts) == 2 and atts[0][2] == id and atts[0][0] != atts[1][0]) or (len(atts) == 2 and atts[0][2] != id and atts[0][0] != atts[1][0] and atts[1][0] == 'sign_in'):
#                     return False
# ???                    
            if len(atts > 0):        
                if (len(atts) == 1 and atts[0][0] == 'sign_in') or (len(atts) == 2 and atts[0][2] == id and atts[0][0] != atts[1][0]) or (len(atts) == 2 and atts[0][2] != id and atts[0][0] != atts[1][0] and atts[1][0] == 'sign_in'):
                    return False
        return True
    _constraints = [(_altern_si_so, 'Error: Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]
    _order = 'id desc'
   
hr_attendance()

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def _state(self, cr, uid, ids, name, args, context={}):
        logger.debug("opendas hr : _state")
        result = {}
        for id in ids:
            result[id] = 'absent'
        cr.execute('SELECT hr_attendance.action, hr_attendance.employee_id \
                FROM ( \
                    SELECT MAX(name) AS name, employee_id \
                    FROM hr_attendance \
                    WHERE action in (\'sign_in\', \'sign_out\') \
                    GROUP BY employee_id \
                ) AS foo \
                LEFT JOIN hr_attendance \
                    ON (hr_attendance.employee_id = foo.employee_id \
                        AND hr_attendance.name = foo.name) \
                WHERE action in (\'sign_in\', \'sign_out\') and hr_attendance.employee_id \
                    in (' + ','.join([str(x) for x in ids]) + ')')
        # OFICIEL :                 WHERE hr_attendance.employee_id \
        for res in cr.fetchall():
            result[res[1]] = res[0] == 'sign_in' and 'present' or 'absent'
        return result

    def _get_workcenter(self, cr, uid, ids, field_name, arg, context={}):
        logger.debug("opendas hr : _get_workcenter")
        all_emp_actions = self.pool.get('hr.employee').get_action(cr, uid, ids)
        result = {}
        for emp_id in ids:
            result[emp_id] = (emp_id in all_emp_actions and 'mrp.workcenter' in all_emp_actions[emp_id] and all_emp_actions[emp_id]['mrp.workcenter'] and isinstance(all_emp_actions[emp_id]['mrp.workcenter'], list) and all_emp_actions[emp_id]['mrp.workcenter'][0]) or False 
        return result

    _columns = {
        "sign_in_auto" : fields.boolean("Sign in Auto"),
        'workcenter_id' : fields.many2one('mrp.workcenter', 'Human resource workcenter', domain=[('resource_type', '=', 'hr')]),
        'workcenter_id_current': fields.function(_get_workcenter, method=True, type="many2one", relation="mrp.workcenter", string='Current workcenter'),
        'workcenter_ids' : fields.many2many('mrp.workcenter', 'mrp_workcenter_hr_employee_rel', 'employee_id', 'workcenter_id', 'Available Workcenters'),
        'state': fields.function(_state, method=True, type='selection', selection=[('absent', 'Absent'), ('present', 'Present')], string='Attendance'),
    }
    _defaults = {
        "sign_in_auto": lambda *args: True,
    }
    
    def _action_check(self, cr, uid, emp_id, dt=False, context={}):
        logger.debug("opendas hr : _action_check")
        cr.execute('select max(name) from hr_attendance where employee_id=%s', (emp_id,))
        res = cr.fetchone()
        return True or not (res and (res[0] >= (dt or time.strftime('%Y-%m-%d %H:%M:%S'))))
    
    def work_change(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : work_change")
        # TODO all_emp_action doit être rechargé après chaque fin de récursion
        if ids and not isinstance(ids, list):
            ids = [ids]
        result = u""
        context_sauv = context.copy()
        wf_service = openerp.workflow
        
        if "action_after" in context :
            del context["action_after"]
            
#        context['tps'] = 1
        
        model = context['model']
        id = context['id']
        from_model = 'from_model' in context and context['from_model'] or False
        from_id = 'from_id' in context and context['from_id'] or False
        tps = 'tps' in context and context['tps'] or 0
        
        print "="*50
        print ids, context_sauv
        print "="*50
        
        accepted_model = [
               "project.project",
               "project.task",
               "mrp.workcenter",
               "mrp.production.workcenter.line",
               "mrp.workcenter.maintenance",
               "mrp.production.workcenter.line.subwork",
        ]
        
        translation = {
            "project.project":_("Project"),
            "project.task":_("Task"),
            "mrp.workcenter":_("Workcenter"),
            "mrp.production.workcenter.line" : _("Production line"),
            "mrp.workcenter.maintenance":_("Maintenance"),
            "mrp.production.workcenter.line.subwork":_("Production line sub-work")
        }
        
        deps_lost_time = {
            "project.project": False,
            "project.task": "project.project",
            "mrp.workcenter": "hr.employee",
            "mrp.production.workcenter.line" : "mrp.workcenter",
            "mrp.workcenter.maintenance": "mrp.workcenter",
            "mrp.production.workcenter.line.subwork": "mrp.production.workcenter.line",
        }
        error_before_start = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line" : [],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        error_before_stop = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter" : [('mrp.workcenter.maintenance', _('Forbidden action : Maintenance in progress'))],
            "mrp.production.workcenter.line" : [('mrp.workcenter.maintenance', _('Forbidden action : Maintenance in progress'))],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        
        exec_and_start_before_start = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line" : [],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        exec_and_start_after_start = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line" : [("mrp.production.workcenter.line.subwork", "dep_id = self.pool.get('mrp.production.workcenter.line.subwork').create(cr,uid,{'name':model_inst.name+'_subwork','workcenter_line_id':model_inst.id})")],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        exec_and_start_after_stop = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter": [],
            "mrp.production.workcenter.line" : tps != 0 and [("mrp.workcenter.maintenance", tps != 0 and "dep_id = self.pool.get('mrp.workcenter.maintenance').create(cr,uid,{'name': 'maintenance_'+model_inst.name ,'workcenter_line_id':model_inst.id})" or False)] or [],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        deps_start_before_start = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line" : [('mrp.workcenter', 'workcenter_id')],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        deps_start_after_start = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line":[],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        deps_start_before_stop = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line":[],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        deps_start_after_stop = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line":[],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        
        deps_stop_before_start = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":["mrp.workcenter"],
            "mrp.production.workcenter.line":["mrp.production.workcenter.line"],
            "mrp.workcenter.maintenance":["mrp.workcenter.maintenance"],
            "mrp.production.workcenter.line.subwork":[],
        }
        deps_stop_after_start = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line":[],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
        deps_stop_before_stop = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":["mrp.production.workcenter.line"],
            "mrp.production.workcenter.line":["mrp.production.workcenter.line.subwork"],
            "mrp.production.workcenter.line.subwork":[],
            "mrp.workcenter.maintenance":[],
        }
        deps_stop_after_stop = {
            "project.project":[],
            "project.task":[],
            "mrp.workcenter":[],
            "mrp.production.workcenter.line":[],
            "mrp.workcenter.maintenance":[],
            "mrp.production.workcenter.line.subwork":[],
        }
                
        employee_search = self.pool.get('hr.employee').search(cr,uid,[('id','in',ids)])
        if len(employee_search) != len(ids):
            raise osv.except_osv(_('Error'), _('Unknown employee : %s --> %s')%(ids,employee_search,))
        
        all_emp_actions = self.pool.get('hr.employee').get_action(cr,uid,ids)
        
        for employee in self.pool.get('hr.employee').browse(cr,uid,ids):
            try:
                context['employee'] = employee.id
                context['from_model'] = model
                context['from_id'] = id
                
                print "Passage boucle"
                
                if employee.state != 'present':
                    if employee.sign_in_auto:
                        print "Passage après signin"
                        employee.sign_in()
                    else:
                        raise osv.except_osv(_('Error'), _('Employee is Out'))
                
                if not model in accepted_model :
                    raise osv.except_osv(_('Error'), _('Unknown model : %s') % (model,))
                
                if employee.id in all_emp_actions:
                    actions = all_emp_actions[employee.id]
                else:
                    actions = {}
                    
                print "actions :", actions    
                
                in_model = False
                
                if model in actions and id in actions[model]:
                    in_model = True
                    
                model_inst = self.pool.get(model).browse(cr, uid, id)
                               
                print "in_model :"+str(in_model)
                
                #-------------------------------------------------------
                # ENTREE
                if not in_model  :
                    for error_model, error_msg in error_before_start[model]:
                        print "--> error_before_start"
                        if error_model in actions :
                            raise osv.except_osv(_(error_model), _('%s') % (error_msg,))
                    
                    for dep_model, dep_eval  in exec_and_start_before_start[model]:
                        print "--> exec_and_start_before_start"          
                        dep_id = False
                        exec dep_eval
                        if dep_model in actions: 
                            if dep_id in actions[dep_model]:
                                continue
                        if dep_model:
                            dsb_context = context.copy()
                            dsb_context['model'] = dep_model
                            dsb_context['id'] = dep_id
                            result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"

                    for dep in deps_stop_before_start[model]:
                        print "--> deps_stop_before_start"
                        if dep in actions:
                            for line in actions[dep]:
                                if not (dep == model and line == id) and not (from_model == dep and from_id == line):
                                    dsb_context = context.copy()
                                    dsb_context['model'] = dep
                                    dsb_context['id'] = line
                                    result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"
                    
                    for dep_model, dep_field  in deps_start_before_start[model]:
                        print "--> deps_start_before_start"          
                        dsb_id = model_inst[dep_field].id
                        if dep_model in actions: 
                            if dsb_id in actions[dep_model]:
                                continue
                        dsb_context = context.copy()
                        dsb_context['model'] = dep_model
                        dsb_context['id'] = dsb_id
                        result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"

                    lost_time_delta = self.get_last_delta(cr, uid, ids)
                    if employee.id in lost_time_delta and lost_time_delta[employee.id]:
                        print "--> deps_lost_time"
                        lost_time_delta = lost_time_delta[employee.id]
                        dsb_context = context.copy()
                        dsb_context['time_delta'] = lost_time_delta['float']
                        if "hr.employee" == lost_time_delta["model"]: 
                            self.pool.get("hr.employee").lost_time(cr,uid,ids,dsb_context)
                        if model == lost_time_delta["model"] and deps_lost_time[model]: 
                            if deps_lost_time[model] in actions:
                                self.pool.get(deps_lost_time[model]).lost_time(cr, uid, actions[deps_lost_time[model]], dsb_context)
         
                    print "ENTREE ", model, id, translation[model], model_inst.name
                    logger.debug("opendas_hr_attendance work_change INCOMING %s %s %s %s" % (model, id, translation[model], model_inst.name))
                    result += _("INCOMING") + u" " + ustr(translation[model]) + u" " + model_inst.name+ "\n"
                    
                    print "CONTEXT :", context
                    logger.debug("opendas_hr_attendance work_change CONTEXT %s" % (str(context)))
                    attendance_id = self.sign_in_action(cr,uid,[employee.id],context)
                    
                    for dep in deps_stop_after_start[model]:
                        print "--> deps_stop_after_start"
                        if dep in actions:
                            for line in actions[dep]:
                                if not (dep == model and line == id) and not (from_model == dep and from_id == line):
                                    dsb_context = context.copy()
                                    dsb_context['model'] = dep
                                    dsb_context['id'] = line
                                    result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"

                    for dep_model, dep_field  in deps_start_after_start[model]:
                        print "--> deps_start_after_start"          
                        dsb_id = model_inst[dep_field].id
                        if dep_model in actions: 
                            if dsb_id in actions[dep_model]:
                                continue
                        dsb_context = context.copy()
                        dsb_context['model'] = dep_model
                        dsb_context['id'] = dsb_id
                        result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"
                    
                    for dep_model, dep_eval  in exec_and_start_after_start[model]:
                        print "--> exec_and_start_after_start"          
                        dep_id = False
                        exec dep_eval
                        if dep_model in actions: 
                            if dep_id in actions[dep_model]:
                                continue
                        if dep_model:
                            dsb_context = context.copy()
                            dsb_context['model'] = dep_model
                            dsb_context['id'] = dep_id
                            result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"
                # SORTIE
                else :
                    for error_model, error_msg in error_before_stop[model]:
                        print "--> error_before_stop"
                        if error_model in actions:
                            raise osv.except_osv(_(error_model), _('%s') % (error_msg))
                    
                    for dep in deps_stop_before_stop[model]:
                        print "--> deps_stop_before_stop"
                        if dep in actions:
                            for line in actions[dep]:
                                if not (dep == model and line == id) and not (from_model == dep and from_id == line):
                                    dsb_context = context.copy()
                                    dsb_context['model'] = dep
                                    dsb_context['id'] = line
                                    result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"
                    
                    for dep_model, dep_field  in deps_start_before_stop[model]:
                        print "--> deps_start_before_stop"          
                        dsb_id = model_inst[dep_field].id
                        if dep_model in actions: 
                            if dsb_id in actions[dep_model]:
                                continue
                        dsb_context = context.copy()
                        dsb_context['model'] = dep_model
                        dsb_context['id'] = dsb_id
                        result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"
                        
                    lost_time_delta = self.get_last_delta(cr, uid, ids)
                    if employee.id in lost_time_delta and lost_time_delta[employee.id]:
                        print "--> deps_lost_time"
                        lost_time_delta = lost_time_delta[employee.id]
                        dsb_context = context.copy()
                        dsb_context['time_delta'] = lost_time_delta['float']
                        if "hr.employee" == lost_time_delta["model"]: 
                            self.pool.get("hr.employee").lost_time(cr, uid, ids, dsb_context)
                    
                    print "SORTIE ", model, id, translation[model], model_inst.name
                    result += _("OUTGOING") + u" " + ustr(translation[model]) + u" " + model_inst.name
                    attendance_id = self.sign_out_action(cr,uid,[employee.id],context)
                    context['time_delta'] = employee.get_time_delta()[employee.id]['float']
                    context['alone'] = True
                    all_emp = self.pool.get('hr.employee').search(cr, uid, [])
                    all_emp.remove(employee.id)
                    actions_all = self.pool.get('hr.employee').get_action(cr, uid, all_emp)
                    for emp_id in actions_all:
                        if model in actions_all[emp_id] and id in actions_all[emp_id][model]:
                            context['alone'] = False
                    employee.sign_out()
                    for dep_model, dep_eval  in exec_and_start_after_stop[model]:
                        print "--> exec_and_start_after_stop"
                        dep_id = False 
                        exec dep_eval
                        if dep_model in actions: 
                            if dep_id in actions[dep_model]:
                                continue
                        if dep_model :
                            dsb_context = context.copy()
                            dsb_context['model'] = dep_model
                            dsb_context['id'] = dep_id
                            result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"  
                    for dep in deps_stop_after_stop[model]:
                        print "--> deps_stop_after_stop"
                        if dep in actions:
                            for line in actions[dep]:
                                if not (dep == model and line == id) and not (from_model == dep and from_id == line):
                                    dsb_context = context.copy()
                                    dsb_context['model'] = dep
                                    dsb_context['id'] = line
                                    result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"
                    for dep_model, dep_field  in deps_start_after_stop[model]:
                        print "--> deps_start_after_stop"          
                        dsb_id = model_inst[dep_field].id
                        if dep_model in actions: 
                            if dsb_id in actions[dep_model]:
                                continue
                        dsb_context = context.copy()
                        dsb_context['model'] = dep_model
                        dsb_context['id'] = dsb_id
                        result += self.work_change(cr, uid, [employee.id], dsb_context) + "\n"
            except osv.except_osv, e:
                print "*"*10, e
                if e[1] == "mrp.workcenter.maintenance" :
                    if "from_model" not in context_sauv :
                        actions = self.pool.get('hr.employee').get_action(cr, uid, ids)[employee.id]
                        for line in actions["mrp.workcenter.maintenance"]:
                            maintenance = self.pool.get("mrp.workcenter.maintenance").browse(cr, uid, line)
                            cron = maintenance.id_cron  #    
                            if cron :
                                print "cron", cron
                                args = eval(cron.args)
                                if not "action_after" in args[1] :
                                    args[1]["action_after"] = []
                                args[1]["action_after"].append("self.work_change(cr, uid, " + str(ids) + ", " + str(context_sauv) + ")")
                                self.pool.get("ir.cron").write(cr, uid, cron.id, {'args':str(args)})
                                result += _("Maintenance in progress. End at ") + ustr(cron.nextcall) + "\n" 
                                result += _("and sign in at ") + ustr(translation[context_sauv['model']])
                                return result
                raise e
        print "*"*70
        if 'action_after' in context_sauv:
            for action_after in context_sauv['action_after']:
                print "---", action_after
                exec(action_after)
        print "="*50
        
        print result
        
        return result
        
    def get_action(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : get_action")
        result = {}
        if ids == [] :
            return result
#                    
        cr.execute("SELECT count(object_id), object_id, employee_id\
                    FROM hr_attendance \
                    WHERE action = 'action' AND employee_id in (" + ','.join([str(x) for x in ids]) + ") \
                    GROUP BY object_id, action, employee_id"
                    )
        res = cr.fetchall()
        for count, object, emp_id in res:
            model = object.split(',')[0]
            id = eval(object.split(',')[1])
            if count % 2 != 0:
                if emp_id not in result :
                    result[emp_id] = {}
                if model not in result[emp_id] :
                    result[emp_id][model] = []
                if id not in result[emp_id][model] :
                    result[emp_id][model].append(id)
        return result
    
    def get_time_delta(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : get_time_delta")
        result = {}
        if 'model' in context and 'id' in context :
            object_id = str(context['model']) + ',' + str(context['id'])
        else:
            object_id = False
        for emp in self.browse(cr, uid, ids):
            if object_id:
                cr.execute("SELECT name\
                            FROM hr_attendance \
                            WHERE action = 'action' AND employee_id in (" + ','.join([str(x) for x in ids]) + ") AND object_id = '" + object_id + "'\
                            ORDER BY id \
                            DESC LIMIT 2"
                )
            else:
                cr.execute("SELECT name\
                            FROM hr_attendance \
                            WHERE employee_id in (" + ','.join([str(x) for x in ids]) + ")\
                            ORDER BY id \
                            DESC LIMIT 2"
                )
            res = cr.fetchall()
            res.reverse()
            start = datetime.datetime.strptime(res[0][0], '%Y-%m-%d %H:%M:%S')
            stop = datetime.datetime.strptime(res[1][0], '%Y-%m-%d %H:%M:%S')
            delta = stop - start
            result[emp.id] = { "hours":delta.seconds / 3600,
                                "minutes":(delta.seconds % 3600) / 60,
                                "seconds":(delta.seconds % 3600) % 60,
                                "days":  delta.days,
                            }
            result[emp.id]['float'] = result[emp.id]['hours'] + (result[emp.id]['minutes'] / 60.0) + (result[emp.id]['seconds'] / 3600.0) + (result[emp.id]['days'] * 24.0)
        return result

    def get_last_delta(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : get_last_delta")
        result = {}
        for emp in self.browse(cr, uid, ids):
            cr.execute("SELECT name,object_id\
                        FROM hr_attendance \
                        WHERE employee_id in (" + ','.join([str(x) for x in ids]) + ")\
                        ORDER BY id \
                        DESC LIMIT 1"
            )
            res = cr.fetchall()
            start = datetime.datetime.strptime(res[0][0], '%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()
            delta = now - start
            if res[0][1] and ',' in res[0][1]:
                model = res[0][1].split(',')[0]
                ids2 = res[0][1].split(',')[1]
            else:
                model = "hr.employee"
                ids2 = [emp.id]
            result[emp.id] = { "hours": delta.seconds / 3600,
                                "minutes": (delta.seconds % 3600) / 60,
                                "seconds": (delta.seconds % 3600) % 60,
                                "days": delta.days,
                                "model": model,
                                "ids": ids2,
                            }
            result[emp.id]['float'] = float(result[emp.id]['hours']) + (result[emp.id]['minutes'] / 60.0) + (result[emp.id]['seconds'] / 3600.0) + (result[emp.id]['days'] * 24.0)
        return result
    
    def lost_time(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : lost_time")
        employee = self.pool.get('hr.employee').browse(cr, uid, context['employee'])
        if employee.workcenter_id:
            vals = {
                'name': employee.otherid + _('(LOST)'),
                'amount': context['time_delta'] * employee.workcenter_id.costs_hour,
                'account_id': employee.workcenter_id.costs_hour_account_id and employee.workcenter_id.costs_hour_account_id.id or False,
                'general_account_id': employee.workcenter_id.costs_general_account_id and employee.workcenter_id.costs_general_account_id.id or False,
                'journal_id': employee.workcenter_id.costs_journal_id and employee.workcenter_id.costs_journal_id.id or False,
                'code': _("LOST"),
                'object_id':"mrp.workcenter," + str(employee.workcenter_id.id),
            }
            self.pool.get('account.analytic.line').create(cr, uid, vals)
        else:
            logger.debug("opendas hr : workcenter was not found")

    def sign_in(self, cr, uid, ids, context={}, dt=False, *args):
        logger.debug("opendas hr : sign_in ")
        """
        Temps d'entrée arrondi à special_resolution
        """
        id = False
        for emp in self.browse(cr, uid, ids):
            if not self._action_check(cr, uid, emp.id, dt, context):
                raise osv.except_osv(_('Warning'), _('You tried to sign in with a date anterior to another event !\nTry to contact the administrator to correct attendances.'))
            res = {'action':'sign_in', 'employee_id':emp.id}

            if dt :
                res['name'] = dt
            else :
                if emp.company_id and emp.company_id.special_resolution:
                    if emp.company_id.clock_in_resolution != 0:
                        delay = emp.company_id.clock_in_resolution
                        now = datetime.datetime.now()
                        now_round = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
                        if now.minute % delay != 0 :
                            if emp.company_id.clock_in_direction == "superior":
                                now_round = now_round + datetime.timedelta(seconds=(delay - (now.minute % delay)) * 60)
                            else :
                                now_round = now_round - datetime.timedelta(seconds=(now.minute % delay) * 60)
                        print "now      ", now
                        print "now_round", now_round
                        res['name'] = now_round
                
            id = self.pool.get('hr.attendance').create(cr, uid, res, context=context)
        return id
       
    def sign_out(self, cr, uid, ids, context={}, dt=False, *args):
        logger.debug("opendas hr : sign_out")
        """
        Temps de sortie arrondi à special_resolution
        """
        print "sign_out"
        id = False
        for emp in self.browse(cr, uid, ids):
            if not self._action_check(cr, uid, emp.id, dt, context):
                raise osv.except_osv(_('Warning'), _('You tried to sign out with a date anterior to another event !\nTry to contact the administrator to correct attendances.'))
            res = {'action':'sign_out', 'employee_id':emp.id}

            actions = emp.get_action()
            if emp.id in actions:
                actions = actions[emp.id]
            else:
                actions = []
            for i in actions:
                dsb_context = {
                        'model':i,
                        'id':actions[i][0]
                }
                self.work_change(cr, uid, [emp.id], dsb_context)
                
            lost_time_delta = self.get_last_delta(cr, uid, ids)
            if emp.id in lost_time_delta and lost_time_delta[emp.id]:
                lost_time_delta = lost_time_delta[emp.id]
                dsb_context = context.copy()
                dsb_context['time_delta'] = lost_time_delta['float']
                dsb_context['employee'] = emp.id
                self.pool.get("hr.employee").lost_time(cr, uid, ids, dsb_context)
            
            if dt:
                res['name'] = dt
            else:
                if emp.company_id and emp.company_id.special_resolution:
                    if emp.company_id.clock_out_resolution != 0:
                        delay = emp.company_id.clock_out_resolution
                        now = datetime.datetime.now()
                        now_round = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
                        if now.minute % delay != 0 :
                            if emp.company_id.clock_out_direction == "superior":
                                now_round = now_round + datetime.timedelta(seconds=(delay - (now.minute % delay)) * 60)
                            else :
                                now_round = now_round - datetime.timedelta(seconds=(now.minute % delay) * 60)
                        print "now      ", now
                        print "now_round", now_round
                        res['name'] = now_round
                
            att_id = self.pool.get('hr.attendance').create(cr, uid, res, context=context)
            id = att_id
            print "hr_attendance id :",att_id
        return id
    
    def sign_in_action(self, cr, uid, ids, context={}, dt=False, *args):
        logger.debug("opendas hr : sign_in_action ids :%s %s" % (str(ids), str(context)))
        logger.debug("opendas hr : sign_in_action args :%s " % (str(args)))
        if 'model' in context and 'id' in context:
            object_id = str(context['model']) + ',' + str(context['id'])
            result = {}
            print "sign_in_action :", ids
            for emp in self.browse(cr, uid, ids):
                res = {'action':'action', 'employee_id':emp.id, 'object_id':object_id}
                if dt :
                    res['name'] = dt
                result[emp.id] = self.pool.get('hr.attendance').create(cr, uid, res, context=context)
            return result
        else:
            return False
    
    def sign_out_action(self, cr, uid, ids, context={}, dt=False, *args):
        logger.debug("opendas hr : sign_out_action :%s %s" % (str(ids), str(context)))
        
        if 'model' in context and 'id' in context:
            object_id = str(context['model']) + ',' + str(context['id'])
            result = {}
            for emp in self.browse(cr, uid, ids):
                res = {'action':'action', 'employee_id':emp.id, 'object_id':object_id}
                if dt:
                    res['name'] = dt
                result[emp.id] = self.pool.get('hr.attendance').create(cr, uid, res, context=context)
            return result
        else:
            return False
       
hr_employee()

