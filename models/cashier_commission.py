from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CashierCommission(models.Model):
    _name = "cashier.commission"
    _description = "Cashier Commission Preferences"

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    commission_amount = fields.Float(
        string="Commission Amount", compute="_compute_commission_amount", store=True
    )
    cash_taken = fields.Float(string="Cash Taken", required=True)
    remaining_cash = fields.Float(
        string="Remaining Cash", compute="_compute_remaining_cash"
    )
    pos_session_id = fields.Many2one("pos.session", string="POS Session", required=True)

    @api.depends("pos_session_id", "employee_id")
    def _compute_commission_amount(self):
        for record in self:
            total_cost = 0.0
            if record.employee_id and record.pos_session_id:
                orders = self.env["pos.order"].search(
                    [
                        ("session_id", "=", record.pos_session_id.id),
                        ("employee_id", "=", record.employee_id.id),
                        ("state", "in", ["paid", "invoiced", "done"]),
                    ]
                )
                total_cost = sum(order.total_cost for order in orders)
            record.commission_amount = total_cost

    @api.depends("commission_amount", "cash_taken")
    def _compute_remaining_cash(self):
        for record in self:
            record.remaining_cash = record.commission_amount - record.cash_taken

    @api.constrains("cash_taken")
    def _check_cash_taken(self):
        for record in self:
            # Obtener el total de pagos en efectivo en la sesión
            session_total_cash = sum(
                payment.amount
                for payment in record.pos_session_id.order_ids.mapped("payment_ids")
                if payment.payment_method_id.name == "Efectivo"
            )

            # Obtener el total de efectivo ya retirado en la sesión, excluyendo la línea actual
            total_cash_taken = sum(
                comm.cash_taken
                for comm in self.search(
                    [
                        ("pos_session_id", "=", record.pos_session_id.id),
                        ("id", "!=", record.id),
                    ]
                )
            )

            # Calcular el efectivo disponible
            available_cash = session_total_cash - total_cash_taken

            if record.cash_taken > available_cash:
                raise ValidationError(
                    f"El monto de efectivo retirado no puede exceder {available_cash}, porque no hay tanto efectivo disponible. El monto ingresado es {record.cash_taken}."
                )

    @api.onchange("pos_session_id")
    def _onchange_pos_session_id(self):
        if self.pos_session_id:
            orders = self.env["pos.order"].search(
                [("session_id", "=", self.pos_session_id.id)]
            )
            employee_ids = orders.mapped("employee_id.id")
            if not employee_ids:
                employee_ids = self.pos_session_id.config_id.employee_ids.ids
            return {"domain": {"employee_id": [("id", "in", employee_ids)]}}


class PosSession(models.Model):
    _inherit = "pos.session"

    cashier_commission_ids = fields.One2many(
        "cashier.commission", "pos_session_id", string="Cashier Commissions"
    )
