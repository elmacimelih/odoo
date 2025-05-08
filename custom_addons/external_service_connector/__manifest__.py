# -*- coding: utf-8 -*-
{
    'name': "External Service Connector",
    'version': "18.0.1.1",
    'license': "LGPL-3",
    'summary': "Üçüncü parti servislere katmanlı entegrasyon",
    'category': "Tools",
    'author': "Alfa Çözüm",
    'website': "alfacozum.com",
    'depends': ['base'],
    'external_dependencies': {
        'python': [
            'requests',
            'PyJWT',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}