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

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
    }
    _defaults = {
    }
    
    def talend_get_picking(self, cr, uid, context, filter):
        print "talend_get_picking"
#        print context
#        print filter
        result = []
#        filter.extend([('type','=','out'),('sale_id','!=',False),('state','in',('draft','auto','confirmed','assigned'))])
        key = "PICK"
        obj_ids = self.browse(cr,uid,self.search(cr,uid,filter))
        obj_ids = obj_ids[0:10]
        for this in obj_ids:
            vals = this.read(['origin','date_out','date_out_planned','date_done','state','min_date','date','serie_id'])[0]
            vals.update({'id':key+","+str(this.id),'name':this.name})
            result.append(vals)
        return {"code":0,"string":_("OK"),"object":result}

    def talend_get_report_by_picking(self, cr, uid, context, filter):
        print "talend_get_report_by_picking"
#        print context
#        print filter
        result = []
        key = "PICK"
        if 'picking' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['picking']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, picking id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an picking"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['picking'] = tmp_context  
        filter.append(('id','in',context['picking']))
        
        result = []
        temp = {}
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
#            dict = this.read(['origin','date_out','date_out_planned','date_done','state','min_date','date','serie_id'])[0]
#            dict.update({
#                         'id':str(this.id)+"1-------",
#                         'name':"Etiquettes",
#                         "ean13":False,
#            })
#            dict.update({'file':[base64.encodestring(netsvc.LocalService('report.stock.picking.labels').create(cr, uid, [this.id], {}, {})[0])]})
#            result.append(dict)
#            #####################################
#            dict2 = this.read(['origin','date_out','date_out_planned','date_done','state','min_date','date','serie_id'])[0]
#            dict2.update({
#                         'id':str(this.id)+"2",
#                         'name':"BL",
#                         "ean13":False,
#            })
#            dict2.update({'file':[base64.encodestring(netsvc.LocalService("report.sale.shipping3").create(cr, uid, [this.id], {}, {})[0])]})
#            result.append(dict2)
            
            #####################################
            vals = this.read(['origin','date_out','date_out_planned','date_done','state','min_date','date','serie_id'])[0]
            vals.update({
                         'id':str(this.id),
                         'name':"BL",
                         "ean13":False,
            })
            vals.update({'file':[base64.encodestring(netsvc.LocalService("report.stock.picking.list").create(cr, uid, [this.id], {}, {})[0])]})
            result.append(vals)
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_product_by_picking(self, cr, uid, context, filter):
        print "talend_get_product_by_picking"
#        print context
#        print filter
        
        key = "PICK"
        if 'picking' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['picking']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, picking id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an picking"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['picking'] = tmp_context  
        filter.append(('id','in',context['picking']))
        
        result = []
        temp = {}
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            for move in this.move_lines:
                if move.product_id.id not in temp :
                    temp[move.product_id.id] = {
                        "id":"MOVE"+","+str(move.product_id.id),
                        "ean13":move.product_id.ean13,
                        "name":move.product_id.name,
                        "qty":int(move.product_qty),
                    }
                else:
                    temp[move.product_id.id]["qty"]+=int(move.product_qty)
        for i in temp :
            result.append(temp[i])
            
            
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_get_packaging_by_product(self, cr, uid, context, filter):
#        print "talend_get_packaging_by_product"
#        print context
#        print filter
        result = []
        temp = {}
        
        key = "PICK"
        if 'id' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, picking id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an picking"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['id'] = tmp_context  
        filter.append(('id','in',context['id']))
        
        key = "MOVE"
        if 'product_id' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['product_id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, product id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an product"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['product_id'] = tmp_context  
        
        for this in self.browse(cr,uid,self.search(cr,uid,filter)):
            for move in this.move_lines:
                if move.product_id.id in context['product_id'] :
                    for move_packaging in move.move_packaging_ids:
                        if move_packaging.state == 'not_send':
                            result.append({
                                        "id":"PACK"+","+str(move_packaging.id),
                                        "ean13":False,
                                        "name":move.name+" <br/> "+move_packaging.name,
                                        })
        return {"code":0,"string":_("OK"),"object":result}
    
    def talend_controle_de_livraison(self, cr, uid, context, filter):
#        print "talend_controle_de_livraison"
#        print context
#        print filter
        
        key = "PICK"
        if 'picking_id' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['picking_id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, picking id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an picking"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['picking_id'] = tmp_context  
        
        key = "MOVE"
        if 'move_id' not in context :
            return {"code":2,"string":_("Error, move_id not in context"),"object":[]}
        tmp_context = []
        for i in context['move_id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, move id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an move"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['move_id'] = tmp_context  
        
        key = "PACK"
        if 'packaging_ids' not in context :
            return {"code":2,"string":_("Error, packaging_ids not in context"),"object":[]}
        tmp_context = []
        for i in context['packaging_ids']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, packaging id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an packaging"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['packaging_ids'] = tmp_context  
        
        if isinstance(context['picking_id'],list) :
            context['picking_id'] = [int(i) for i in context['picking_id']]
        if isinstance(context['move_id'],list) :
            context['move_id'] = [int(i) for i in context['move_id']]
        if isinstance(context['packaging_ids'],list) :
            context['packaging_ids'] = [int(i) for i in context['packaging_ids']]
            
        packaging_obj = self.pool.get('stock.move.packaging')
        for i in context['packaging_ids']:
            packaging_obj.write(cr,uid,i,{"state":"send"})
            self.action_partial_done(cr,uid,context['picking_id'])
        
        return {"code":0,"string":"ok","object":[]}
    
    def talend_controle_de_livraison_no_packaging(self, cr, uid, context, filter):
        print "talend_controle_de_livraison_no_packaging"
        print context
        print filter
        
        key = "PICK"
        if 'picking_id' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['picking_id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, picking id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an picking"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['picking_id'] = tmp_context  
        
        key = "MOVE"
        if 'move_ids' not in context :
            return {"code":2,"string":_("Error, move_id not in context"),"object":[]}
        tmp_context = []
        for i in context['move_ids']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, move id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an move"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['move_ids'] = tmp_context  
        
        if isinstance(context['picking_id'],list) :
            context['picking_id'] = [int(i) for i in context['picking_id']]
        if isinstance(context['move_ids'],list) :
            context['move_ids'] = [int(i) for i in context['move_ids']]
            
        if len(context['picking_id']) == 0 :
            return {"code":2,"string":_("Error, no picking found"),"object":[]}
        if len(context['picking_id']) > 1 :
            return {"code":2,"string":_("Error, more than one picking found"),"object":[]}

        picking = self.browse(cr,uid,context['picking_id'][0])   
        if not picking :
            return {"code":2,"string":_("Error, no picking found : wrong id"),"object":[]}
        
        
        move_obj = self.pool.get('stock.move')
        table_qty = {}
        for i in context['move_ids'] :
            move_ptr = move_obj.browse(cr,uid,i)
            product_id = move_ptr.product_id.id 
            if product_id not in table_qty :
                table_qty[product_id]=1
            else:
                table_qty[product_id]+=1
        
        self.do_split_all(cr,uid,[picking.id],table_qty,context)
        
        return {"code":0,"string":"ok","object":[]}
    
    
    def talend_picking_out(self, cr, uid, context, filter):
        print "talend_picking_out"
        print context
        print filter
        
        key = "PICK"
        if 'picking_id' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['picking_id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, picking id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an picking"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['picking_id'] = tmp_context  
#        
        key = "MOVE"
        if 'product_ids' not in context :
            return {"code":2,"string":_("Error, product_id not in context"),"object":[]}
        tmp_context = []
        for i in context['product_ids']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, product id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not a product"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['product_ids'] = tmp_context  
        
        if isinstance(context['picking_id'],list) :
            context['picking_id'] = [int(i) for i in context['picking_id']]
        if isinstance(context['product_ids'],list) :
            context['product_ids'] = [int(i) for i in context['product_ids']]
            
        if 'product_qty' in context and context['product_qty'] and len(context['product_ids']) == 1:
            context['product_ids'] = [context['product_ids'][0] for i in range(0,int(context['product_qty'][0]))]
        
        if len(context['picking_id']) == 0 :
            return {"code":2,"string":_("Error, no picking found"),"object":[]}
        if len(context['picking_id']) > 1 :
            return {"code":2,"string":_("Error, more than one picking found"),"object":[]}

        picking = self.browse(cr,uid,context['picking_id'][0])   
        if not picking :
            return {"code":2,"string":_("Error, no picking found : wrong id"),"object":[]}
        
        
        table_qty = {}
        for i in context['product_ids'] :
            if i not in table_qty :
                table_qty[i]=1
            else:
                table_qty[i]+=1
        
        self.do_split_all(cr,uid,[picking.id],table_qty,context)
        
        return {"code":0,"string":"ok","object":[]}
    
    def talend_picking_in(self, cr, uid, context, filter):
        print "talend_picking_in"
        print context
        print filter
        
        key = "PICK"
        if 'picking_id' not in context :
            return {"code":2,"string":_("Error, picking not in context"),"object":[]}
        tmp_context = []
        for i in context['picking_id']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, picking id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not an picking"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['picking_id'] = tmp_context  
#        
        key = "MOVE"
        if 'product_ids' not in context :
            return {"code":2,"string":_("Error, product_id not in context"),"object":[]}
        tmp_context = []
        for i in context['product_ids']:
            tmp = i.split(',')
            if len(tmp) != 2 :
                return {"code":2,"string":_("Error, product id"),"object":[]}
            if key != tmp[0] :
                return {"code":2,"string":_("Error, This is not a product"),"object":[]}
            tmp_context.append(int(tmp[1]))
        context['product_ids'] = tmp_context  
        
        if isinstance(context['picking_id'],list) :
            context['picking_id'] = [int(i) for i in context['picking_id']]
        if isinstance(context['product_ids'],list) :
            context['product_ids'] = [int(i) for i in context['product_ids']]
        
        if 'product_qty' in context and context['product_qty'] and len(context['product_ids']) == 1:
            context['product_ids'] = [context['product_ids'][0] for i in range(0,int(context['product_qty'][0]))]
        
        if len(context['picking_id']) == 0 :
            return {"code":2,"string":_("Error, no picking found"),"object":[]}
        if len(context['picking_id']) > 1 :
            return {"code":2,"string":_("Error, more than one picking found"),"object":[]}

        picking = self.browse(cr,uid,context['picking_id'][0])   
        if not picking :
            return {"code":2,"string":_("Error, no picking found : wrong id"),"object":[]}
        
        
        table_qty = {}
        for i in context['product_ids'] :
            if i not in table_qty :
                table_qty[i]=1
            else:
                table_qty[i]+=1
        
        self.do_split_all(cr,uid,[picking.id],table_qty,context)
        
        return {"code":0,"string":"ok","object":[]}

    
    
    def do_split_all(self, cr, uid, ids, datas, context):
        for picking in self.browse(cr,uid,ids):
            new_picking = None
            new_moves = []
            complete = []
            too_many = []
            too_few = []
            
            if not datas:
                data = {}
                for move in picking.move_lines :
                    data[move.product_id.id] = move.product_qty
            else:
                data = datas.copy()
                    
            for move in picking.move_lines :
                if move.product_id.id in data:
                    qty = data[move.product_id.id]
                else:
                    qty = 0
                    
                if move.product_qty == qty:
                    complete.append(move)
                elif move.product_qty > qty:
                    too_few.append(move)
                else:
                    too_many.append(move)
                    
                if (picking.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = self.pool.get('product.product').browse(cr, uid, [move.product_id.id])[0]
                    user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
                    qty = qty
                    uom = product.uom_id.id
                    price = move.purchase_line_id.price_unit
                    currency = picking.purchase_id.pricelist_id.currency_id.id
        
                    qty = self.pool.get('product.uom')._compute_qty(cr, uid, uom, qty, product.uom_id.id)
        
                    if (qty > 0):
                        new_price = self.pool.get('res.currency').compute(cr, uid, currency,user.company_id.currency_id.id, price)
                        new_price = self.pool.get('product.uom')._compute_price(cr, uid, uom, new_price, product.uom_id.id)
                        if product.qty_available<=0:
                            new_std_price = new_price
                        else:
                            new_std_price = ((product.standard_price * product.qty_available) + (new_price * qty))/(product.qty_available + qty)
        
                        self.pool.get('product.product').write(cr, uid, [product.id],{'standard_price': new_std_price})
                        self.pool.get('stock.move').write(cr, uid, [move.id], {'price_unit': new_price})
            
            for move in too_few:
                if not new_picking:
                    new_picking = self.copy(cr, uid, picking.id,
                            {
                                'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking'),
                                'move_lines' : [],
                                'state':'draft',
                            })
                    
                if move.product_id.id in data:
                    qty = data[move.product_id.id]
                else:
                    qty = 0
                    
                if qty != 0:
                    #ASPerience: gérer product_pack_qty dans la gestion du reliquat et ici
                    new_obj = self.pool.get('stock.move').copy(cr, uid, move.id,
                        {
                            'product_qty' : qty,
                            'product_uos_qty':qty,
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                        })
                self.pool.get('stock.move').write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - qty,
                            'product_uos_qty':move.product_qty - qty,
                        })
                
            if new_picking:
                self.pool.get('stock.move').write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
                for move in too_many:
                    self.pool.get('stock.move').write(cr, uid, [move.id],
                            {
                                'product_qty' : qty,
                                'product_uos_qty': qty,
                                'picking_id': new_picking,
                            })
            else:
                for move in too_many:
                    if move.product_id.id in data:
                        qty = data[move.product_id.id]
                    else:
                        qty = 0
                    #ASPerience: gérer product_pack_qty ici aussi
                    self.pool.get('stock.move').write(cr, uid, [move.id],
                            {
                                'product_qty': qty,
                                'product_uos_qty': qty,
                            })
            
            wf_service = netsvc.LocalService("workflow")
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                self.write(cr, uid, [picking.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', picking.id, cr)
            else:
                self.action_move(cr, uid, [picking.id])
                wf_service.trg_validate(uid, 'stock.picking', picking.id, 'button_done', cr) 
            bo_name = ''
            if new_picking:
                bo_name = self.read(cr, uid, [new_picking], ['name'])[0]['name']
            return {'new_picking':new_picking or False, 'back_order':bo_name}
stock_picking()

  



