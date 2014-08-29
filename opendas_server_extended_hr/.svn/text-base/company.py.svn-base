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

from osv import fields, osv

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'auto_checking_delay': fields.boolean('Automatic delay when clocking in and out'),
        'clock_in_delay_min': fields.integer('delay when clocking in (Minutes)'),
        'clock_out_delay_min': fields.integer('delay when clocking out (Minutes)'),
        #TODO: à expliciter. clock_in_resolution et clock_out_resolution suffisent normalement
        'special_resolution': fields.boolean('Spécial resolution when clocking in and out'),
        'clock_in_resolution': fields.integer('Resolution when clocking in (Minutes)'),
        'clock_in_direction': fields.selection([('inferior', 'Inferior'), ('superior', 'Superior')], 'Direction of round when clocking in', required=True),
        'clock_out_resolution': fields.integer('Resolution when clocking out (Minutes)'),
        'clock_out_direction': fields.selection([('inferior', 'Inferior'), ('superior', 'Superior')], 'Direction of round when clocking out', required=True),
    }

res_company()