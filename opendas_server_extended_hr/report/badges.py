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

import openerp.netsvc
from openerp.report import report_sxw
from openerp.osv import osv
import time
from openerp.tools.translate import _
from openerp.tools import ustr
import logging
import logging.handlers
logger = logging.getLogger(__name__)


class badges(report_sxw.rml_parse):

      
    def __init__(self, cr, uid, name, context):
        super(badges, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'time': time,
        })
        self.context = context
        
#report_sxw.report_sxw('report.hr.employee.badges','hr.employee','addons/opendas_server_extended_hr/report/badges.rml',parser=badges)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


