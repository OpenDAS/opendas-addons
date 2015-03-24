# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 OpenDAS (http://www.opendas.org) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from mx import DateTime
import time
import openerp.netsvc
from openerp.osv import fields, osv
from openerp.tools import config
from openerp.tools.translate import _
import openerp.tools
import datetime
import base64
import logging
import logging.handlers
logger = logging.getLogger(__name__)

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    def talend_get_production(self, cr, uid, context, filter):
        print "talend_get_production"
#        print context
#        print filter
        result = []
#        filter.extend([('type','=','out'),('purchase_id','!=',False),('state','in',('draft','auto','confirmed','assigned'))])
        key = "PRODUCTION"
        obj_ids = self.browse(cr,uid,self.search(cr,uid,filter))
        obj_ids = obj_ids[0:10]
        for this in obj_ids:
            vals = this.read([])[0]
            vals.update({'id':key+","+str(this.id),'name':this.name})
            result.append(vals)
        return {"code":0,"string":_("OK"),"object":result}

    def talend_get_productions(self, cr, uid, context, filter):
        logger.debug("talend_get_productions")
#        print context
#        print filter
        result = []
#        filter.extend([('type','=','out'),('purchase_id','!=',False),('state','in',('draft','auto','confirmed','assigned'))])
        key = "PRODUCTION"
        obj_ids = self.browse(cr,uid,self.search(cr,uid,filter))
        for this in obj_ids:       
            vals = {
                    'id' : key+","+str(this.id),
                    'name' : this.name,
                    'min_date' : str(this.date_start),
                    'max_date' : str(this.date_finished),
            }
            result.append(vals)
        return {"code":0,"string":_("OK"),"object":result}

    def talend_synchro_mrp_production(self, cr, uid, context, filter):
        logger.debug("opendas hr : talend_synchro_mrp_production")

        if 'id' not in context :
            return {"code":2,"string":_("Error, production not in context"),"object":[]}
        
        obj = self.browse(cr,uid,context['id'])
       
        if obj :

            min_date = context['min_date_full']   
            max_date = context['max_date_full']           
            
            if context['delete']==True:
                if (obj.date_start==min_date) and (obj.date_finished==max_date) and (obj.name == context['name']):
                    osv.osv.unlink(self, cr, uid, context['id'], context=context)
                    return {"code":0,"string":_("Evenement supprimé."),"object":[]}
                else:
                    if context['override']==True:
                        osv.osv.unlink(self, cr, uid, context['id'], context=context)
                        return {"code":0,"string":_("Evenement supprimé."),"object":[]}
                    else:
                        return {"code":4,"string":_("Des modifications concurentes ont été effectuées. L'évement :\n"+obj.name+"("+str(obj.date_start)[:16]+" , "+str(obj.date_planned)[:16]+") sera supprimé. Valider la suppression ?"),"object":[]}          
            else:
                #Ecrasement de l'ancien
                if context['override']==True:
                    vals = {'date_start':min_date,'date_finished' :max_date, 'name':context['name']}
                    self.write(cr, uid, context['id'], vals)
                    return {"code":0,"string":_("Changement de date effectué."),"object":[]}
                else:
                    if (obj.date_start==context['init_min_date_full']) and (obj.date_finished==context['init_max_date_full']) and (obj.name == context['init_name']):
                        vals = {'date_start': min_date,'date_finished': max_date, 'name':context['name']}
                        self.write(cr, uid, context['id'], vals)
                        return {"code":0,"string":_("Changement de date effectué."),"object":[]}
                    else:
                        return {"code":4,"string":_("Des modifications concurentes ont été effectuées. L'évement :\n"+obj.name+"("+str(obj.date_start)[:16]+" , "+str(obj.date_planned)[:16]+") sera remplacé par\n"+context['name']+"("+str(context['min_date_full'])[:16]+" , "+str(context['max_date_full'])[:16]+")\nValider ces changements ?")}                                      
        else:
            return {"code":2,"string":_("Error, no picking found : wrong id"),"object":[]}


    def talend_get_report_production(self, cr, uid, context, filter):
        logger.debug("opendas mrp : talend_get_report_production")
#        print context
#        print filter
        result = []
        key = "PRODUCTION"
        if 'production_id' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['production_id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, production_id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not a production"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['production_id'] = tmp_context  
        filter.append(('id','in',context['production_id']))
        
        result = []
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            temp = {}
            temp.update({
                         'id':str(this.id),
                         'name':"Production Order",
                         "ean13":False,
            })         
            report_obj = this.env['report']
            pdf = report_obj.get_pdf(this,'mrp.report_mrporder')         
            temp.update({'file':base64.encodestring(pdf)})
            result.append(temp)

        return {"code":0,"string":_("OK"),"object":result}
    
mrp_production()

class mrp_production_workcenter_line(osv.osv):
    _inherit = "mrp.production.workcenter.line"

    def talend_get_mrp_production_workcenter_line(self, cr, uid, context, filter):
        logger.debug("opendas hr : talend_get_mrp_production_workcenter_line")
        result = []
        temp = {}

        if 'workcenter' in context:
            id = int(context['workcenter'][0])
            workcenter_id = self.pool.get('mrp.workcenter').search(cr,uid,[('otherid','=',id)])
            ids = self.pool.get('mrp.production.workcenter.line').search(cr,uid,[('workcenter_id','in',workcenter_id)])
            for this in self.read(cr,uid,ids,['id','name','production_id','date_start','date_planned']):
                temp[this['id']]= {
                    "id":"PPL"+","+str(this['id']),
                    "parent_id":str(this['production_id']) or False,
                    "name":this['name'],
                    "min_date":str(this['date_start']), 
                    "max_date":str(this['date_planned']),
                }

            if len(temp) > 0:
                for i in temp :
                    result.append(temp[i])
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_synchro_mrp_production_workcenter_line(self, cr, uid, context, filter):
        logger.debug("opendas hr : talend_synchro_mrp_production_workcenter_line")
  
        print context
  
        if 'id' not in context :
            return {"code":2,"string":_("Error, production workcenter line not in context"),"object":[]}
        
        obj = self.browse(cr,uid,context['id'])
        print obj       
        if obj :
            
#             min_date = datetime.datetime.strptime(context['min_date_full'], '%Y-%m-%d %H:%M:%S')   
#             max_date = datetime.datetime.strptime(context['max_date_full'], '%Y-%m-%d %H:%M:%S')
            
            min_date = context['min_date_full']   
            max_date = context['max_date_full']           
            
            if context['delete']==True:
                if (obj.date_start==min_date) and (obj.date_planned==max_date) and (obj.name == context['name']):
                    osv.osv.unlink(self, cr, uid, context['id'], context=context)
                    return {"code":0,"string":_("Evenement supprimé."),"object":[]}
                else:
                    if context['override']==True:
                        osv.osv.unlink(self, cr, uid, context['id'], context=context)
                        return {"code":0,"string":_("Evenement supprimé."),"object":[]}
                    else:
                        return {"code":4,"string":_("Des modifications concurentes ont été effectuées. L'évement :\n"+obj.name+"("+str(obj.date_start)[:16]+" , "+str(obj.date_planned)[:16]+") sera supprimé. Valider la suppression ?"),"object":[]}
            
            else:
                #Ecrasement de l'ancien
                if context['override']==True:
                    vals = {'date_start':min_date,'date_planned' :max_date, 'name':context['name']}
                    self.write(cr, uid, context['id'], vals)
                    return {"code":0,"string":_("Changement de date effectué."),"object":[]}
                else:
                    if (obj.date_start==context['init_min_date_full']) and (obj.date_planned==context['init_max_date_full']) and (obj.name == context['init_name']):
                        vals = {'date_start': min_date,'date_planned': max_date, 'name':context['name']}
                        self.write(cr, uid, context['id'], vals)
                        return {"code":0,"string":_("Changement de date effectué."),"object":[]}
                    else:
                        return {"code":4,"string":_("Des modifications concurentes ont été effectuées. L'évement :\n"+obj.name+"("+str(obj.date_start)[:16]+" , "+str(obj.date_planned)[:16]+") sera remplacé par\n"+context['name']+"("+str(context['min_date_full'])[:16]+" , "+str(context['max_date_full'])[:16]+")\nValider ces changements ?")}                                      
        else:
            return {"code":2,"string":_("Error, no picking found : wrong id"),"object":[]}                                                                                                                                                                                           

mrp_production_workcenter_line()
