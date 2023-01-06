from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    date_birth_partner = fields.Date('Date de Naissance')
    def default_get(self, fields):
        res = super().default_get(fields)
        res['category_id'] = [(6, 0, [self.env.ref('adquat_rsp.res_partner_category_customer').id])]
        res['country_id'] = self.env.company.country_id
        return res
