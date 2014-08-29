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
import netsvc
from osv import fields, osv
from tools import config
from tools.translate import _
import tools
import datetime
import base64

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
    }
    _defaults = {
    }
    
    def talend_get_sale(self, cr, uid, context, filter):
        print "talend_get_sale"
#        print context
#        print filter
        result = []
#        filter.extend([('type','=','out'),('sale_id','!=',False),('state','in',('draft','auto','confirmed','assigned'))])
        key = "SALE"
        obj_ids = self.browse(cr,uid,self.search(cr,uid,filter))
        obj_ids = obj_ids[0:10]
        for this in obj_ids:
            vals = this.read([])[0]
            vals.update({'id':key+","+str(this.id),'name':this.name})
            result.append(vals)
        return {"code":0,"string":_("OK"),"object":result}

sale_order()

