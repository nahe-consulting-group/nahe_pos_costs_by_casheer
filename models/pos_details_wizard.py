# -*- coding: utf-8 -*-
from odoo import api, models, fields


class PosDetailsWizard(models.TransientModel):
    _name = "pos.details.wizard"
    _description = "POS Details Wizard"

    start_date = fields.Datetime("Start Date", required=True)
    end_date = fields.Datetime("End Date", required=True)
    pos_config_ids = fields.Many2many(
        "pos.config", string="Point of Sale Configs", required=True
    )

    def generate_report(self):
        self.ensure_one()
        data = {
            "date_start": self.start_date,
            "date_stop": self.end_date,
            "config_ids": self.pos_config_ids.ids,
        }
        report = self.env["ir.actions.report"]._get_report_from_name(
            "point_of_sale.report_saledetails"
        )
        return report.report_action([], data=data)
