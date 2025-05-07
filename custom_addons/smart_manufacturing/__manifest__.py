# -*- coding: utf-8 -*-
{
    'name': "Smart Manufacturing Tracker ",
    'version': "18.0.1.1",
    'license': "LGPL-3",
    'summary': "Üretim, stok ve ürün API servisleri",
    'category': "Manufacturing",
    'author': "Alfa Çözüm",
    'website': "alfacozum.com",
    'depends': ['base', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/manufacture_order_views.xml',
    ],
    'installable': True,
    'application': True,
}
