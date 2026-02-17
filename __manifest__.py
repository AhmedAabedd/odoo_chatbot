# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Product Brand',
    'version' : '1.0',
    'summary': 'Product\'s Brand',
    'sequence': 10,
    'description': '"Adding brand to the proudtcs"',
    'category': 'Productivity',
    'website': 'https://www.proosoftcloud.com/',
    'depends' : ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_view.xml',
        'views/inherit_product_template_view.xml',
        'views/mail_message_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
}