# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 OpenAgro (http://www.openagro.eu) All Rights Reserved.
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

from osv import osv, fields
import netsvc 
logger = netsvc.Logger()
class opendas_ean128(osv.osv):
	"ean128 definition"
	_name = 'das.ean128'
	_columns = {
		'code': fields.char("Code",required=True, size=4),
        'char_variable': fields.boolean('Char after code is a variable'),
		'name': fields.char("Name", required=True, size=255),
		'fixed_length': fields.boolean('Fixed length (false= variable length)'),
		'min_length': fields.integer("Min length (for variable field)", required=True, help='Minimum length of code'),
        'max_length': fields.integer("Length or max length (for variable field)", required=True, help='Maximum length of code'),
        'format': fields.selection([('date', 'Date'),
                                   ('char', 'Characters'),
                                   ('int', 'Integer'),
                                   ('float', 'Float')], 'Format',required=True),
        'needs_uom': fields.boolean('Needs UoM to be used'),
#        'uom_id': fields.many2one('product.uom', 'UoM'),
        'mapping': fields.char("Mapping", size=255),
        
        #TODO: créer parent_id + child_ids lien one2many vers plusieurs das.ean128
        }
	def code128(self,chaine):
		
		logger.notifyChannel("opendas", netsvc.LOG_DEBUG," ********** Passage par code128 %s %s"%(chaine))
		
		import string
		def testnum(chaine):
			for i in chaine:
				if not i in string.digits:
					return False
			return True
		Code128=''
		tableB=True
		i=0
		while i < len(chaine):
			if tableB==True:
				if i < len(chaine)-4:
					if testnum(chaine[i:4]):
						if i==0:
							Code128=chr(210)
						else: 
							Code128=Code128+chr(204)
						tableB=False
					else:
						if i==0:
							Code128=chr(209)
							tableB=True
				else:
					if i==0:
						Code128=chr(209)
						tableB=True
			if tableB==False:
				if testnum(chaine[i:i+2]) and i(len(chaine)-2):
					dummy=int(chaine[i:i+2])
					if dummy95:
						dummy+=32
					else:
						dummy+=100
					Code128=Code128+chr(dummy)
					i=i+2
				else:
					Code128=Code128+chr(205)
					tableB=True
			if tableB==True:
				Code128=Code128+chaine[i]
				i=i+1
		for i,dum in enumerate(Code128):
			dummy=ord(dum)
			if dummy127:
				dummy-=32
			else:
				dummy-=100
			if i==0:
				checksum=dummy
			checksum=(checksum + i*dummy)
			while checksum103:
				checksum-=103
		if checksum95:
			checksum+=32
		else:
			checksum+=100
			Code128=Code128+chr(checksum)+chr(211)
			
		return str(Code128)

opendas_ean128()

