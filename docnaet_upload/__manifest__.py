# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Docnaet: Partner upload document',
    'version': '0.1',
    'category': 'Document / Partner',
    'description': '''        
        Integrate docnaet document in Partner form
        Used for activate a page in Partner for have docnaet document available
        there
        ''',
    'author': 'Micronaet S.r.l. - Nicola Riolini',
    'website': 'http://www.micronaet.it',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'docnaet',
        ],
    'init_xml': [],
    'demo': [],
    'data': [
        'upload_view.xml',
        'wizard/upload_document_view.xml',
        ],
    'active': False,
    'installable': True,
    'auto_install': False,
    }
