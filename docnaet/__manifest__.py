# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Docnaet',
    'version': '0.0.1',
    'category': 'Document Management',
    'description': '''
        Micronaet - Docnaet Document Manager
        Default module for create structure to integrare Docnaet Management    
        ''',
    'author': 'Micronaet s.r.l.',
    'website': 'http://www.micronaet.it',
    'depends': [
        'base',
        ],
    'init_xml': [],
    'data': [
        'security/docnaet_group.xml',
        'security/ir.model.access.csv',

        'data/config.xml',
        # 'data/counter.xml',

        'wizard/document_duplication_view.xml',
        'docnaet_view.xml',
        # 'alternative_view.xml',
        # 'docnaet_workflow.xml',

        'wizard/search_view.xml',

        # Security:
        # 'security_docnaet.xml',
        ],
    'demo_xml': [],
    'active': False,
    'installable': True,
    'application': True,
    }
