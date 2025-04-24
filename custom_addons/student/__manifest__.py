# -*- coding: utf-8 -*-
{
    'name': "Student Module",
    'version': "18.0.1.1",
    'license': "LGPL-3",
    'summary': "Short (1 phrase/Line) summary of the module's purpose",
    'description': """Long description of modules@s purpose""",
    'author': "Alfa Çözüm",
    'category': "Education",
    'website': "alfacozum.com",
    'maintainer': "Alfa Çözüm <info@alfacozum.com>",
    'sequence': 1,
    'depends': ['base', 'account', 'stock'],
    'data': [
    "views/student_view.xml",
    "views/school_view.xml",
    "views/hobby_view.xml",
    "security/ir.model.access.csv",
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}
