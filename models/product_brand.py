from odoo import models, fields, api



class ProductBrand(models.Model):
    _name = 'product.brand'



    name = fields.Char(string="Brand Name", required=True)
    product_ids = fields.One2many('product.template', 'brand_id')