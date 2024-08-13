# -*- coding: utf-8 -*-
from odoo import api, models, fields


class PosSession(models.Model):
    _inherit = "pos.session"

    def action_open_sales_details_wizard(self):
        self.ensure_one()
        return {
            "name": "Sales Details",
            "type": "ir.actions.act_window",
            "res_model": "pos.details.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_start_date": self.start_at,
                "default_end_date": self.stop_at,
                "default_pos_config_ids": [(6, 0, [self.config_id.id])],
            },
        }
