# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
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
###############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _


class suppliers_assigner(osv.TransientModel):

    """
    M321 Customizations to assign suppliers in products
    """
    _name = "suppliers.assigner"

    _columns = {
        'sure': fields.boolean("Sure?", help="Check if are sure"),
        'are_sure': fields.boolean("Are Sure?",
            help="Check if really are sure"),
    }

    def assigner_supplier(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        purchase_obj = self.pool.get('purchase.order')
        product_obj = self.pool.get('product.template')
        company_id = self.pool.get(
            'res.users').browse(cr, uid, uid).company_id.id
        product_supp_obj = self.pool.get('product.supplierinfo')
        purchase_ids = purchase_obj.search(cr, uid, [], context=context)
        wz_brw = self.browse(cr, uid, ids and ids[0], context=context)
        if wz_brw.sure and wz_brw.are_sure:
            for po in purchase_obj.browse(cr, uid, purchase_ids,
                    context=context):
                partner_id = po.partner_id.id
                for line in po.order_line:
                    product_id = line.product_id.product_tmpl_id.id
                    if product_id and not product_supp_obj.search(cr, uid,
                            [('product_id', '=', product_id),
                            ('name', '=', partner_id)]):
                        product_obj.write(
                            cr, uid, [
                                product_id], {
                                    'seller_ids': [(0, 0,
                                        {'name': partner_id,
                                        'min_qty': 1.0,
                                        'delay': 1,
                                        'sequence': 10,
                                        'product_id': product_id,
                                        'company_id': company_id,
                                        'product_uom': line and
                                            line.product_id and
                                            line.product_id.uom_id and
                                            line.product_id.uom_id.id})]})
        else:
            raise osv.except_osv(_('Processing Error'), _(
                'Must select the 2 options to make sure the operation'))

        return {'type': 'ir.actions.act_window_close'}
