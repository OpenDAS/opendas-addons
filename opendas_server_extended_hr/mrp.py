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
from openerp.osv import fields
from openerp.osv import osv

import logging
import logging.handlers

import openerp.netsvc
from openerp.tools.translate import _
import datetime

logger = logging.getLogger(__name__)

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns = {
        'production_costs_account_id': fields.many2one('account.analytic.account', 'Production costs'),
    }
    
    def talend_get_mrp_production(self, cr, uid, context, filter):
        logger.debug("opendas hr : talend_get_mrp_production")
        result = []
        temp = {}
        
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            temp[this.id] = {
                "id":str(this.id),
                "name":this.name,
            }
               
        for i in temp :
            result.append(temp[i])           
        
        return {"code":0,"string":_("OK"),"object":result}
    
mrp_production()

class mrp_production_product_line(osv.osv):
    _inherit = 'mrp.production.product.line'
    _columns = {
           'min_date': fields.datetime('Min Date'),
           'max_date': fields.datetime('Max Date'),
    }
    
    def talend_get_mrp_production_product_line(self, cr, uid, context, filter):
        logger.debug("opendas hr : talend_get_mrp_production_product_line")
        result = []
        temp = {}

        if 'workcenter' in context:
            id = int(context['workcenter'][0])
            workcenter_id = self.pool.get('mrp.workcenter').search(cr,uid,[('otherid','=',id)])
            ids = self.pool.get('mrp.production.workcenter.line').search(cr,uid,[('workcenter_id','in',workcenter_id)])
            for this in self.pool.get('mrp.production.workcenter.line').read(cr,uid,ids,['id','name','production_id','date_start','date_planned']):
                temp[this['id']]= {
                    "id":"PPL"+","+str(this['id']),
                    "parent_id":str(this['production_id']) or False,
                    "name":this['name'],
                    "date_start":str(this['date_start']), 
                    "date_planned":str(this['date_planned']),
                }

            if len(temp) > 0:
                for i in temp :
                    result.append(temp[i])
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_synchro_mrp_production_product_line(self, cr, uid, context, filter):
        logger.debug("opendas hr : talend_synchro_mrp_production_product_line")
  
        if 'id' not in context :
            return {"code":2,"string":_("Error, production product line not in context"),"object":[]}
        
        ids = self.pool.get('mrp.workcenter').search(cr,uid,[('otherid','=', context['workstation_code'])])
        
        for i in self.pool.get('mrp.workcenter').read(cr,uid,ids,['date_start','date_stop']):
            
            minSec = int(context['min_date'].split(':',1)[0])*60*60 + int(context['min_date'].split(':',1)[1])*60
            maxSec = int(context['max_date'].split(':',1)[0])*60*60 + int(context['max_date'].split(':',1)[1])*60
            
            if i['date_start']==False:
                startSec = minSec
            else:
                startSec = int(i['date_start'].split(':',1)[0])*60*60 + int(i['date_start'].split(':',1)[1])*60

           
            if i['date_stop']==False:
                stopSec = maxSec 
            else:
                stopSec = int(i['date_stop'].split(':',1)[0])*60*60 + int(i['date_stop'].split(':',1)[1])*60
            
            if startSec <= minSec and maxSec <= stopSec and stopSec >= minSec and maxSec >= startSec:
                obj = self.browse(cr,uid,context['id'])
                if obj : 
       
                    if context['delete']==True:
                        if (obj.min_date==context['init_min_date_full']) and (obj.max_date==context['init_max_date_full']) and (obj.name == context['name']):
                            osv.osv.unlink(self, cr, uid, context['id'], context=context)
                            return {"code":0,"string":_("Evenement supprimé."),"object":[]}
                        else:
                            if context['override']==True:
                                osv.osv.unlink(self, cr, uid, context['id'], context=context)
                                return {"code":0,"string":_("Evenement supprimé."),"object":[]}
                            else:
                                return {"code":4,"string":_("Des modifications concurentes ont été effectuées. L'évement :\n"+obj.name+"("+str(obj.min_date)[:16]+" , "+str(obj.max_date)[:16]+") sera supprimé. Valider la suppression ?"),"object":[]}
                    
                    else:
                        #Ecrasement de l'ancien
                        if context['override']==True:
                            vals = {'min_date': datetime.datetime.strptime(context['min_date_full'], '%Y-%m-%d %H:%M:%S'),'max_date': datetime.datetime.strptime(context['max_date_full'], '%Y-%m-%d %H:%M:%S'), 'name':context['name']}
                            self.write(cr, uid, context['id'], vals)
                            return {"code":0,"string":_("Changement de date effectué."),"object":[]}
                        else:
                            if (obj.min_date==context['init_min_date_full']) and (obj.max_date==context['init_max_date_full']) and (obj.name == context['init_name']):
                                vals = {'min_date': datetime.datetime.strptime(context['min_date_full'], '%Y-%m-%d %H:%M:%S'),'max_date': datetime.datetime.strptime(context['max_date_full'], '%Y-%m-%d %H:%M:%S'), 'name':context['name']}
                                self.write(cr, uid, context['id'], vals)
                                return {"code":0,"string":_("Changement de date effectué."),"object":[]}
                            else:
                                return {"code":4,"string":_("Des modifications concurentes ont été effectuées. L'évement :\n"+obj.name+"("+str(obj.min_date)[:16]+" , "+str(obj.max_date)[:16]+") sera remplacé par\n"+context['name']+"("+str(context['min_date_full'])[:16]+" , "+str(context['max_date_full'])[:16]+")\nValider ces changements ?"),"object":[]}
                else :
                    return {"code":2,"string":_("Error, no picking found : wrong id"),"object":[]}
            else:
                return {"code":2,"string":_("Error, this workstation works only between : "+i['date_start']+" and "+i['date_stop']),"object":[]}
            
        return {"code":2,"string":_("Error during the date update."),"object":[]}
    
mrp_production_product_line()

###### POSTE ########
class mrp_workcenter(osv.osv):
    _inherit = "mrp.workcenter"
    
    def _get_employee_ids(self, cr, uid, ids, name, arg, context=None):
        logger.debug("opendas hr : mrp workcenter _get_employee_ids")
        res = {}
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(cr,uid,[])
        all_emp_actions = self.pool.get('hr.employee').get_action(cr,uid,employee_ids)
        for employee_id in all_emp_actions:
            all_emp_actions[employee_id]
            if 'mrp.workcenter' in all_emp_actions[employee_id]:
                if all_emp_actions[employee_id]['mrp.workcenter'][0] not in res:
                    res[all_emp_actions[employee_id]['mrp.workcenter'][0]] = []
                res[all_emp_actions[employee_id]['mrp.workcenter'][0]].append(employee_id) 
        return res
    
    _columns = {
        'otherid': fields.integer('Other id'),
        'date_start': fields.char('Date Start', size=5),
        'date_stop': fields.char('Date Stop',size=5),
	    'workcenter_lines': fields.one2many('mrp.production.workcenter.line', 'workcenter_id', 'Workcenter Line'),
	    'maintenance_costs_account_id': fields.many2one('account.analytic.account', 'Maintenance costs'),
	    'maintenance_lines': fields.one2many('mrp.workcenter.maintenance', 'workcenter_id', 'Maintenance'),
        'employee_attendance_ids': fields.function(_get_employee_ids, method=True, type="one2many", relation="hr.employee", string='Employees in work'),
        'employee_ids': fields.one2many('hr.employee', 'workcenter_id', 'Employees linked'),
        'employee_pool_ids' : fields.many2many('hr.employee', 'mrp_workcenter_hr_employee_rel', 'workcenter_id', 'employee_id', 'Employees possible for this workcenter'),
    }

    #JSH: je ne vois pas quand on a besoin de ces 2 fonctions
    #Quand on est sur une machine, on est soit sur une maintenance, soit sur une production
    
    def lost_time(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp workcenter lost_time")
        employee = self.pool.get('hr.employee').browse(cr,uid,context['employee'])
        for i in self.browse(cr,uid,ids):
            print i,ids
            code = i.code or i.name or "workcenter"
            vals = {
                'name': employee.name+' (LOST '+code+')',
                'amount': context['time_delta'] * i.costs_hour,
                'account_id': i.costs_hour_account_id and i.costs_hour_account_id.id or False,
                'general_account_id': i.costs_general_account_id and i.costs_general_account_id.id or False,
                'journal_id': i.costs_journal_id and i.costs_journal_id.id or False,
                'code': code,
                'object_id':"mrp.workcenter,"+str(i.id),
            }
            self.pool.get('account.analytic.line').create(cr, uid, vals)
         
    def sign_in(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp workcenter sign_in")
        print "----> sign_in mrp_workcenter",context
    
    def sign_out(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp workcenter sign_out")
        print "----> sign_out mrp_workcenter",context,ids
        for i in self.browse(cr, uid, ids):
            if i.costs_journal_id and i.costs_general_account_id:
                vals = {
                    'name': i.name+_(' (Workcenter time)'),
                    'amount': context['time_delta'] * i.costs_hour,
                    'account_id': i.costs_hour_account_id and i.costs_hour_account_id.id or False,
                    'general_account_id': i.costs_general_account_id and i.costs_general_account_id.id or False,
                    'journal_id': i.costs_journal_id and i.costs_journal_id.id or False,
                    'code': i.code,
                    'object_id':"mrp.workcenter,"+str(i.id),
                }
                self.pool.get('account.analytic.line').create(cr, uid, vals)
    
mrp_workcenter()

###### DOSSIER ########
class mrp_production_workcenter_line(osv.osv):
    _inherit = "mrp.production.workcenter.line"
    _columns = {
	    'subwork_ids': fields.one2many('mrp.production.workcenter.line.subwork', 'workcenter_line_id', 'Subwork'),
        'maintenance_lines': fields.one2many('mrp.workcenter.maintenance', 'workcenter_line_id', 'Maintenance'),
        'qty_false':fields.integer('Quantity false'),
        'qty_ok':fields.integer('Quantity ok'),
    }
    
    def lost_time(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_production_workcenter_line lost_time")
        employee = self.pool.get('hr.employee').browse(cr,uid,context['employee'])
        for i in self.browse(cr,uid,ids):
            code = i.name or ""
            vals = {
                'name': employee.name+_(' (LOST ')+code+u')',
                'amount': context['time_delta'] * i.workcenter_id.costs_hour,
                'account_id': i.workcenter_id.costs_hour_account_id and i.workcenter_id.costs_hour_account_id.id or False,
                'general_account_id': i.workcenter_id.costs_general_account_id and i.workcenter_id.costs_general_account_id.id or False,
                'journal_id': i.workcenter_id.costs_journal_id and i.workcenter_id.costs_journal_id.id or False,
                'code': code,
                'object_id':"mrp.production.workcenter.line,"+str(i.id),
            }
            self.pool.get('account.analytic.line').create(cr, uid, vals)
        
    def sign_in(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_production_workcenter_line sign_in")
        print "----> sign_in mrp_production_workcenter_line",context
        wf_service = openerp.netsvc.LocalService('workflow')
        for i in self.browse(cr, uid, ids):
            if i.state in ("draft","startworking"):
                wf_service.trg_validate(uid, 'mrp.production.workcenter.line', i.id, 'button_start_working', cr)
            else:
                wf_service.trg_validate(uid, 'mrp.production.workcenter.line', i.id, 'button_resume', cr)
    
    def sign_out(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_production_workcenter_line sign_out")
        
        print "----> sign_out mrp_production_workcenter_line",context
        
        employee = self.pool.get('hr.employee').browse(cr,uid,context['employee'])
        wf_service = openerp.netsvc.LocalService('workflow')
        for i in self.browse(cr, uid, ids):
            vals = {
                'name': i.name+_('(WKC)'),
                'amount': context['time_delta'] * i.workcenter_id.costs_hour,
                'account_id': (i.production_id.production_costs_account_id and i.production_id.production_costs_account_id.id) or 
                              (i.workcenter_id.costs_hour_account_id and i.workcenter_id.costs_hour_account_id.id) or False,
                'general_account_id': i.workcenter_id.costs_general_account_id and i.workcenter_id.costs_general_account_id.id or False,
                'journal_id': i.workcenter_id.costs_journal_id and i.workcenter_id.costs_journal_id.id or False,
                'code': i.workcenter_id.code,
                'object_id': 'mrp.production.workcenter.line,'+str(i.id),
            }
            self.pool.get('account.analytic.line').create(cr, uid, vals)
            vals = {
                'name': i.name+_('(HR)'),
                'amount': context['time_delta'] * employee.workcenter_id.costs_hour,
                'account_id': employee.workcenter_id.costs_hour_account_id and employee.workcenter_id.costs_hour_account_id.id or False,
                'general_account_id': employee.workcenter_id.costs_general_account_id and employee.workcenter_id.costs_general_account_id.id or False,
                'journal_id': employee.workcenter_id.costs_journal_id and employee.workcenter_id.costs_journal_id.id or False,
                'code': employee.workcenter_id.code,
                'object_id': 'mrp.production.workcenter.line,'+str(i.id),
            }
            self.pool.get('account.analytic.line').create(cr, uid, vals)
            vals['amount'] = -vals['amount']
            self.pool.get('account.analytic.line').create(cr, uid, vals)
            
            vals = {
                    'cycle': i.cycle + 1,
                    'hour': context['time_delta'],
            }
            self.write(cr, uid, i.id, vals)
            
            if context['alone']:
                wf_service.trg_validate(uid, 'mrp.production.workcenter.line', i.id, 'button_pause', cr)
               
mrp_production_workcenter_line()

###### TRAVAIL ########
class mrp_production_workcenter_line_subwork(osv.osv):
    _name = "mrp.production.workcenter.line.subwork"
    _columns = {
		'name': fields.char('Name', size=64, required=True),
        'workcenter_line_id': fields.many2one('mrp.production.workcenter.line', 'Workcenter Line', ondelete='cascade', required=True),
        'date_start': fields.datetime('Start Date'),
        'date_stop': fields.datetime('Stop Date'),
        'qty': fields.integer('Quantité produite'),
    }
    
    def lost_time(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_production_workcenter_line_subwork lost_time")
        print "----> lost_time mrp.production.workcenter.line.subwork",context
        employee = self.pool.get('hr.employee').browse(cr,uid,context['employee'])
        for i in self.browse(cr,uid,ids):
            vals = {
                'name': employee.name+' (LOST '+i.code+')',
                'amount': context['time_delta'] * i.costs_hour,
                'account_id': i.costs_hour_account_id and i.costs_hour_account_id.id or False,
                'general_account_id': i.costs_general_account_id and i.costs_general_account_id.id or False,
                'journal_id': i.costs_journal_id and i.costs_journal_id.id or False,
                'code': i.code,
                'object_id':"mrp.production.workcenter.line.subwork,"+str(i.id),
            }
            self.pool.get('account.analytic.line').create(cr, uid, vals)
            
    def sign_in(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_production_workcenter_line_subwork sign_in")
        print "----> sign_in mrp_production_workcenter_line_subwork",context
        self.write(cr,uid,ids,{'date_start':datetime.datetime.now()})
    
    def sign_out(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_production_workcenter_line_subwork sign_out")        
        print "----> sign_out mrp_production_workcenter_line_subwork",context
        self.write(cr,uid,ids,{'date_stop':datetime.datetime.now()})
    
mrp_production_workcenter_line_subwork()

class mrp_workcenter_maintenance_type(osv.osv):
    _name = "mrp.workcenter.maintenance.type"
    _columns = {
		    'name': fields.char('Name', size=64, required=True),
		    'code': fields.char('Code', size=16, required=True),
		    'maintenance_time': fields.float('Maintenance Time (Minuts)', help="Time in Minuts for the maintenance."),
    }
mrp_workcenter_maintenance_type()

class mrp_workcenter_maintenance(osv.osv):
    _name = "mrp.workcenter.maintenance"
    _columns = {
		   'name': fields.char('Name', size=64, required=True),
		   'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
           'workcenter_line_id': fields.many2one('mrp.production.workcenter.line', 'Workcenter Line'),
		   'type_id': fields.many2one('mrp.workcenter.maintenance.type', 'Maintenance type'),
           'date_start': fields.datetime('Start Date'),
           'date_stop': fields.datetime('Stop Date'),
           'id_cron': fields.many2one('ir.cron', 'Cron'),
    }
    
    def sign_in(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_workcenter_maintenance sign_in")
        if 'tps' in context and context['tps'] and context['tps']!= 0:
            start = datetime.datetime.now()
            stop = start + datetime.timedelta(seconds=context['tps']*60)
            for i in self.browse(cr, uid, ids):
                vals = {
                        'name':i.name,
                        'nextcall': stop.strftime('%Y-%m-%d %H:%M:%S'),
                        'numbercall':1,
                        'model':"hr.employee",
                        'function':"work_change",
                        'args' : ( [context['employee']], {'model':context['model'],'id':context['id']} ),
                }
                id_cron = self.pool.get('ir.cron').create(cr,uid,vals)
                self.write(cr,uid,i.id,{'date_start':start,'date_stop':stop,'id_cron':id_cron})
        else:
            self.write(cr,uid,ids,{'date_start':datetime.datetime.now()})
                
        
    
    def sign_out(self, cr, uid, ids, context={}):
        logger.debug("opendas hr : mrp_workcenter_maintenance sign_out")
        employee = self.pool.get('hr.employee').browse(cr,uid,context['employee'])
        for i in self.browse(cr, uid, ids):
            if i.id_cron and i.id_cron.active :
                self.pool.get('ir.cron').write(cr,uid,i.id_cron.id,{"active":False})
            self.write(cr,uid,i.id,{'date_stop':datetime.datetime.now()})
            
            if(i.workcenter_line_id):
                vals = {
                    'name': i.name+_(' (Maintenance)'),
                    'amount': context['time_delta'] * i.workcenter_line_id.costs_hour,
                    'account_id': i.workcenter_line_id.production_id.production_costs_account_id and i.workcenter_line_id.production_id.production_costs_account_id.id or False,
                    'general_account_id': i.workcenter_line_id.workcenter_id.costs_general_account_id and i.workcenter_line_id.workcenter_id.costs_general_account_id.id or False,
                    'journal_id': i.workcenter_line_id.workcenter_id.costs_journal_id and i.workcenter_line_id.workcenter_id.costs_journal_id.id or False,
                    'code': i.workcenter_line_id.workcenter_id.code,
                    'object_id': 'mrp.workcenter.maintenance,'+str(i.id),
                }
                self.pool.get('account.analytic.line').create(cr, uid, vals)
            elif(i.workcenter_id):
                vals = {
                    'name': i.name+_(' (Maintenance)'),
                    'amount': context['time_delta'] * i.workcenter_id.costs_hour,
                    'account_id': i.workcenter_id.costs_hour_account_id and i.workcenter_id.costs_hour_account_id.id or False,
                    'general_account_id': i.workcenter_id.costs_general_account_id and i.workcenter_id.costs_general_account_id.id or False,
                    'journal_id': i.workcenter_id.costs_journal_id and i.workcenter_id.costs_journal_id.id or False,
                    'code': i.workcenter_id.code,
                    'object_id': 'mrp.workcenter.maintenance,'+str(i.id),
                }
                self.pool.get('account.analytic.line').create(cr, uid, vals)
            
            vals = {
                'name': i.name+_(' (Employee)'),
                'amount': context['time_delta'] * employee.workcenter.costs_hour,
                'account_id': employee.workcenter.costs_hour_account_id and employee.workcenter.costs_hour_account_id.id or False,
                'general_account_id': employee.workcenter.costs_general_account_id and employee.workcenter.costs_general_account_id.id or False,
                'journal_id': employee.workcenter.costs_journal_id and employee.workcenter.costs_journal_id.id or False,
                'code': employee.workcenter.code,
                'object_id': 'mrp.workcenter.maintenance,'+str(i.id),
            }
            self.pool.get('account.analytic.line').create(cr, uid, vals)
            vals['amount'] = -vals['amount']
            self.pool.get('account.analytic.line').create(cr, uid, vals)
                
mrp_workcenter_maintenance()
