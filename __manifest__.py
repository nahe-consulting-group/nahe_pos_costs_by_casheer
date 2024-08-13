# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Custom Spa",
    "summary": """
        Modificaciones para agregar comisiones y reprotes del SPA""",
    "author": "Nahe Consulting Group",
    "maintainers": ["nahe-consulting-group"],
    "website": "https://nahe.com.ar/",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "version": "15.0.3.3.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": ["base", "point_of_sale", "pos_hr"],
    "data": [
        "views/pos_order_views.xml",
        "views/pos_session.xml",
        "views/report_pos_saledetails.xml",
    ],
}
