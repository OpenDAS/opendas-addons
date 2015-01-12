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

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
    }
    _defaults = {
    }
    
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
    
    def talend_get_report_production(self, cr, uid, context, filter):
        print "talend_get_report_production"
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
            temp.update({'file':[base64.encodestring(openerp.netsvc.LocalService('report.mrp.production.order').create(cr, uid, [this.id], {}, {})[0])]})
            result.append(temp)
        return {"code":0,"string":_("OK"),"object":result}
    
mrp_production()