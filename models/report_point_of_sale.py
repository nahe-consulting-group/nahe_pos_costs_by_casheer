import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class CustomReportSaleDetails(models.AbstractModel):
    _inherit = "report.point_of_sale.report_saledetails"

    def get_sale_details(
        self, date_start=False, date_stop=False, config_ids=False, session_ids=False
    ):
        result = super(CustomReportSaleDetails, self).get_sale_details(
            date_start, date_stop, config_ids, session_ids
        )
        orders = self.env["pos.order"].search(
            [
                ("date_order", ">=", date_start),
                ("date_order", "<=", date_stop),
                ("config_id", "in", config_ids),
                ("state", "in", ["paid", "invoiced", "done"]),
            ]
        )

        product_sales_by_cashier = {}
        for order in orders:
            cashier = order.employee_id.name or "Unknown"
            for line in order.lines:
                product_key = (line.product_id.id, line.product_id.name)
                if product_key not in product_sales_by_cashier:
                    product_sales_by_cashier[product_key] = {}
                if cashier not in product_sales_by_cashier[product_key]:
                    product_sales_by_cashier[product_key][cashier] = {
                        "quantity": 0,
                        "total_cost": 0.0,
                    }
                product_sales_by_cashier[product_key][cashier]["quantity"] += line.qty
                product_sales_by_cashier[product_key][cashier][
                    "total_cost"
                ] += line.total_cost

        # Formatear los datos para el reporte
        products_grouped_by_cashier = []
        for product, cashiers in product_sales_by_cashier.items():
            for cashier, data in cashiers.items():
                products_grouped_by_cashier.append(
                    {
                        "product_name": product[1],
                        "cashier": cashier,
                        "quantity": data["quantity"],
                        "total_cost": data["total_cost"],
                    }
                )

        result["products_grouped_by_cashier"] = products_grouped_by_cashier
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.info(f"Running _get_report_values with data: {data}")
        _logger.info(f"Running _get_report_values with docids: {docids}")
        data = super(CustomReportSaleDetails, self)._get_report_values(docids, data)
        _logger.info(
            f"Data for report including products_grouped_by_cashier: {data.get('products_grouped_by_cashier', [])}"
        )

        # Asegúrate de que las fechas y configuraciones están pasadas correctamente.
        date_start = data.get("date_start")
        date_stop = data.get("date_stop")
        config_ids = data.get("config_ids")

        # Buscar la sesión de POS basada en start_at, stop_at y config_id
        pos_session = self.env["pos.session"].search(
            [
                ("config_id", "in", config_ids),
                ("start_at", ">=", date_start),
                ("stop_at", "<=", date_stop),
            ],
            limit=1,
        )

        pos_session_id = pos_session.id if pos_session else None
        # Configura el dominio basado en fechas y configuraciones.
        domain = [("state", "in", ["paid", "invoiced", "done"])]
        if date_start and date_stop:
            domain += [
                ("date_order", ">=", date_start),
                ("date_order", "<=", date_stop),
            ]
        if config_ids:
            domain += [("config_id", "in", config_ids)]

        orders = self.env["pos.order"].search(domain)

        cashier_costs = []
        cashier_totals = {}
        for order in orders:
            cashier = order.employee_id.name or "Unknown"
            _logger.info(
                f"Processing order {order.id} for cashier {cashier} with total cost {getattr(order, 'total_cost', 0)}"
            )

            if cashier not in cashier_totals:
                cashier_totals[cashier] = 0.0
            cashier_totals[cashier] += getattr(order, "total_cost", 0)

        for cashier, total_cost in cashier_totals.items():
            cashier_costs.append({"name": cashier, "total_cost": total_cost})

        # Sum of cash payments
        total_cash_payments = sum(
            payment["total"]
            for payment in data["payments"]
            if payment["name"] == "Efectivo"
        )

        # Filtrar las comisiones por la sesión de POS específica.
        cashier_commissions = self.env["cashier.commission"].search(
            [("pos_session_id", "=", pos_session_id)]
        )

        total_cash_taken = sum(comm.cash_taken for comm in cashier_commissions)

        # Calculate remaining cash
        remaining_cash = total_cash_payments - total_cash_taken

        # Update the data dictionary with the new information
        data.update(
            {
                "cashier_costs": cashier_costs,
                "total_cash_payments": total_cash_payments,
                "total_cash_taken": total_cash_taken,
                "remaining_cash": remaining_cash,
                "cashier_commissions": cashier_commissions,
            }
        )

        _logger.info(f"Data after adding cashier_costs and commissions: {data}")
        return data
