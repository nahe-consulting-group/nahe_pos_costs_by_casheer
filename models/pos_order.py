# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    total_cost = fields.Float(
        string="Total Cost", compute="_compute_total_cost", store=True
    )

    @api.depends("lines")
    def _compute_total_cost(self):
        for order in self:
            total_cost = 0.0
            for line in order.lines:
                total_cost += line.total_cost
            order.total_cost = total_cost
