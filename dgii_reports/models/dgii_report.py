# -*- coding: utf-8 -*-

import calendar
import logging

from odoo import api, models, exceptions

_logger = logging.getLogger(__name__)

class dgiireport(models.Model):
    _inherit = "dgii.report"

    @api.multi
    def generate_report(self):

        try:
            month, year = self.name.split("/")
            last_day = calendar.monthrange(int(year), int(month))[1]
            start_date = "{}-{}-01".format(year, month)
            end_date = "{}-{}-{}".format(year, month, last_day)
        except:
            raise exceptions.ValidationError(u"Período inválido")

        self.purchase_report.unlink()
        self.sale_report.unlink()
        self.cancel_report.unlink()
        self.exterior_report.unlink()

        self.it_filename = False
        self.it_binary = False
        self.ir17_filename = False
        self.ir17_binary = False

        self.sale_binary = False
        self.sale_filename = False
        self.purchase_binary = False
        self.purchase_filename = False
        self.cancel_binary = False
        self.cancel_filename = False

        xls_dict = {"it1": {}, "ir17": {}}
        purchase_report = []
        sale_report = []
        ext_report = []
        sale_line = 1
        purchase_line = 1
        ext_line = 1

        sale_except_tax_id = self.env.ref("l10n_do.{}_tax_0_sale".format(self.company_id.id))
        purchase_except_tax_id = self.env.ref("l10n_do.{}_tax_0_purch".format(self.company_id.id))
        untax_ids = (sale_except_tax_id.id, purchase_except_tax_id.id)

        journal_ids = self.env["account.journal"].search(
            ['|', ('ncf_control', '=', True), ('ncf_remote_validation', '=', True)])

        invoice_ids = self.env["account.invoice"].search(
            [('date_invoice', '>=', start_date), ('date_invoice', '<=', end_date),
             ('journal_id', 'in', journal_ids.ids),('journal_id.fiscal', '=', True)])

        error_list = self.get_invoice_in_draft_error(invoice_ids.filtered(lambda x: x.state == "draft"))

        self.create_cancel_invoice_lines(invoice_ids.filtered(lambda x: x.state == 'cancel' and
                                                                        x.type in ("out_invoice", "out_refund") and
                                                                        x.move_name))

        invoice_ids = invoice_ids.filtered(lambda x: x.state in ('open', 'paid'))

        invoice_ids |= self.get_late_informal_payed_invoice(start_date, end_date)

        count = len(invoice_ids)
        for invoice_id in invoice_ids:

            RNC_CEDULA, TIPO_IDENTIFICACION = self.get_identification_info(invoice_id.partner_id.vat)

            error_msg = self.validate_fiscal_information(RNC_CEDULA, invoice_id.number, invoice_id.type,
                                                         invoice_id.origin_invoice_ids)
            if error_msg:
                for error in error_msg:
                    if not error_list.get(invoice_id.id, False):
                        error_list.update({invoice_id.id: [(invoice_id.type, invoice_id.number, error)]})
                    else:
                        error_list[invoice_id.id].append((invoice_id.type, invoice_id.number, error))
                continue

            NUMERO_COMPROBANTE_FISCAL = invoice_id.number
            FECHA_COMPROBANTE = invoice_id.date_invoice

            NUMERO_COMPROBANTE_MODIFICADO = AFFECTED_NVOICE_ID = False

            if invoice_id.type in ("out_refund", "in_refund"):
                NUMERO_COMPROBANTE_MODIFICADO, AFFECTED_NVOICE_ID = self.get_numero_de_comprobante_modificado(
                    invoice_id)

            FECHA_PAGO = ITBIS_RETENIDO = RETENCION_RENTA = False
            if invoice_id.state == "paid":
                FECHA_PAGO, ITBIS_RETENIDO, RETENCION_RENTA = self.get_payment_date_and_retention_data(invoice_id)

            commun_data = {
                "RNC_CEDULA": RNC_CEDULA,
                "TIPO_IDENTIFICACION": TIPO_IDENTIFICACION,
                "NUMERO_COMPROBANTE_FISCAL": NUMERO_COMPROBANTE_FISCAL,
                "NUMERO_COMPROBANTE_MODIFICADO": NUMERO_COMPROBANTE_MODIFICADO,
                "FECHA_COMPROBANTE": FECHA_COMPROBANTE,
                "FECHA_PAGO": FECHA_PAGO and FECHA_PAGO or None,
                "invoice_id": invoice_id.id,
                "inv_partner": invoice_id.partner_id.id,
                "affected_nvoice_id": AFFECTED_NVOICE_ID,
                "nc": True if AFFECTED_NVOICE_ID else False,
                "MONTO_FACTURADO_EXCENTO": 0,
                "MONTO_FACTURADO": 0,
                "ITBIS_FACTURADO": 0,
                "ITBIS_FACTURADO_SERVICIOS": 0,
                "ITBIS_RETENIDO": ITBIS_RETENIDO and ITBIS_RETENIDO or 0,
                "RETENCION_RENTA": RETENCION_RENTA and RETENCION_RENTA or 0,
                "TIPO_BIENES_SERVICIOS_COMPRADOS": invoice_id.purchase_fiscal_type
            }

            no_tax_line = invoice_id.invoice_line_ids.filtered(lambda x: not x.invoice_line_tax_ids)

            if no_tax_line:
                if invoice_id.type in ("out_invoice", "out_refund"):
                    no_tax_line.write({"invoice_line_tax_ids": [(4, sale_except_tax_id.id, False)]})
                else:
                    no_tax_line.write({"invoice_line_tax_ids": [(4, purchase_except_tax_id.id, False)]})

            untaxed_lines = invoice_id.invoice_line_ids.filtered(lambda x: x.invoice_line_tax_ids[0].id in untax_ids)

            untaxed_move_lines = []
            for untaxed_line in untaxed_lines:
                if invoice_id.type in ("in_invoice", 'out_refund'):
                    domain = [('move_id', '=', invoice_id.move_id.id), ('product_id', '=', untaxed_line.product_id.id),
                              ('debit', '=', abs(untaxed_line.price_subtotal_signed))]
                else:
                    domain = [('move_id', '=', invoice_id.move_id.id), ('product_id', '=', untaxed_line.product_id.id),
                              ('credit', '=', abs(untaxed_line.price_subtotal_signed))]

                move_lines = self.env["account.move.line"].search(domain)
                if move_lines:
                    untaxed_move_lines.append(move_lines)

            if untaxed_move_lines:
                if invoice_id.type in ("out_invoice", "out_refund"):
                    if not sale_except_tax_id in [t.tax_id for t in invoice_id.tax_line_ids]:
                        invoice_id.write({"tax_line_ids": [(0, 0, {"tax_id": sale_except_tax_id.id,
                                                                   "name": sale_except_tax_id.name,
                                                                   "account_id": untaxed_move_lines[
                                                                       0].account_id.id})]})
                else:
                    if not purchase_except_tax_id in [t.tax_id for t in invoice_id.tax_line_ids]:
                        invoice_id.write({"tax_line_ids": [(0, 0, {"tax_id": purchase_except_tax_id.id,
                                                                   "name": purchase_except_tax_id.name,
                                                                   "account_id": untaxed_move_lines[
                                                                       0].account_id.id})]})

                commun_data["MONTO_FACTURADO_EXCENTO"] = self.env.user.company_id.currency_id.round(
                    sum(abs(rec.debit - rec.credit) for rec in untaxed_move_lines))

            taxed_lines = invoice_id.invoice_line_ids.filtered(lambda x: x.invoice_line_tax_ids[0].id not in untax_ids)

            taxed_lines_name = [rec.product_id.id for rec in taxed_lines]

            if commun_data["MONTO_FACTURADO_EXCENTO"]:
                taxed_lines_amount = self.env["account.move.line"].search(
                    [('move_id', '=', invoice_id.move_id.id), ('product_id', 'in', taxed_lines_name),
                     ("id", 'not in', [x.id for x in untaxed_move_lines])])
            else:
                taxed_lines_amount = self.env["account.move.line"].search([('move_id', '=', invoice_id.move_id.id),
                                                                           ('product_id', 'in', taxed_lines_name)])

            commun_data["MONTO_FACTURADO"] = self.env.user.company_id.currency_id.round(
                sum(abs(rec.debit - rec.credit) for rec in taxed_lines_amount))

            commun_data["MONTO_FACTURADO"] += commun_data["MONTO_FACTURADO_EXCENTO"]

            for tax in invoice_id.tax_line_ids:
                tax_base_amount = commun_data["MONTO_FACTURADO"]
                untax_base_amount = commun_data["MONTO_FACTURADO_EXCENTO"]

                tax_line = self.env["account.move.line"].search(
                    [('move_id', '=', invoice_id.move_id.id), ('tax_line_id', '=', tax.tax_id.id)])

                if tax_line:
                    tax_amount = self.env.user.company_id.currency_id.round(
                        sum(abs(rec.debit - rec.credit) for rec in tax_line))

                    if tax.tax_id.type_tax_use == "sale" or (
                            tax.tax_id.type_tax_use == "purchase" and tax.tax_id.purchase_tax_type in ("itbis")):
                        commun_data["ITBIS_FACTURADO"] += tax_amount

                    if tax.tax_id.type_tax_use == "purchase" and tax.tax_id.purchase_tax_type == "itbis_servicio":
                        commun_data["ITBIS_FACTURADO_SERVICIOS"] += tax_amount
                else:
                    tax_amount = 0

                if invoice_id.type in ("out_refund", "in_refund"):
                    tax_base_amount = tax_base_amount * -1
                    untax_base_amount = untax_base_amount * -1
                    tax_amount = tax_amount * -1

                if tax.tax_id.base_it1_cels:
                    xls_cels = tax.tax_id.base_it1_cels.split(",")

                    for xls_cel in xls_cels:
                        if tax.tax_id.amount == 0:
                            if not xls_dict["it1"].get(xls_cel, False):
                                xls_dict["it1"].update({xls_cel: untax_base_amount})
                            else:
                                xls_dict["it1"][xls_cel] += untax_base_amount
                        else:
                            if not xls_dict["it1"].get(xls_cel, False):
                                xls_dict["it1"].update({xls_cel: tax_base_amount})
                            else:
                                xls_dict["it1"][xls_cel] += tax_base_amount

                if tax.tax_id.base_ir17_cels:
                    xls_cels = tax.tax_id.base_ir17_cels.split(u",")

                    for xls_cel in xls_cels:
                        xls_cel = xls_cel.split(u"%")

                        if len(xls_cel) == 1:
                            if not xls_dict["ir17"].get(xls_cel[0], False):
                                xls_dict["ir17"].update({xls_cel[0]: commun_data["MONTO_FACTURADO"]})
                            else:
                                xls_dict["ir17"][xls_cel[0]] += commun_data["MONTO_FACTURADO"]
                        elif len(xls_cel) == 2:
                            if not xls_dict["ir17"].get(xls_cel[0], False):
                                xls_dict["ir17"].update(
                                    {xls_cel[0]: round(commun_data["MONTO_FACTURADO"] * (float(xls_cel[1]) / 100), 2)})
                            else:
                                xls_dict["ir17"][xls_cel[0]] += round(
                                    commun_data["MONTO_FACTURADO"] * (float(xls_cel[1]) / 100), 2)

                if tax.tax_id.tax_it1_cels:
                    xls_cels = tax.tax_id.tax_it1_cels.split(",")
                    for xls_cel in xls_cels:
                        if not xls_dict["it1"].get(xls_cel, False):
                            xls_dict["it1"].update({xls_cel: tax_amount})
                        else:
                            xls_dict["it1"][xls_cel] += tax_amount

                if tax.tax_id.tax_ir17_cels:
                    xls_cels = tax.tax_id.tax_ir17_cels.split(",")
                    for xls_cel in xls_cels:
                        if not xls_dict["ir17"].get(xls_cel, False):
                            xls_dict["ir17"].update({xls_cel: tax_amount})
                        else:
                            xls_dict["ir17"][xls_cel] += tax_amount

            if invoice_id.type in ("out_invoice", "out_refund") and commun_data["MONTO_FACTURADO"]:
                sale_report.append((self.id,
                                    sale_line,
                                    commun_data["RNC_CEDULA"],
                                    commun_data["TIPO_IDENTIFICACION"],
                                    commun_data["NUMERO_COMPROBANTE_FISCAL"],
                                    commun_data["NUMERO_COMPROBANTE_MODIFICADO"] and commun_data[
                                        "NUMERO_COMPROBANTE_MODIFICADO"] or None,
                                    commun_data["FECHA_COMPROBANTE"],
                                    commun_data["ITBIS_FACTURADO"],
                                    commun_data["MONTO_FACTURADO"],
                                    commun_data["MONTO_FACTURADO_EXCENTO"],
                                    invoice_id.id,
                                    AFFECTED_NVOICE_ID and AFFECTED_NVOICE_ID or None,
                                    AFFECTED_NVOICE_ID and True or False))
                sale_line += 1
            elif invoice_id.type in ("in_invoice", "in_refund") and commun_data["MONTO_FACTURADO"]:
                purchase_report.append((self.id,
                                        purchase_line,
                                        commun_data["RNC_CEDULA"],
                                        commun_data["TIPO_IDENTIFICACION"],
                                        commun_data["NUMERO_COMPROBANTE_FISCAL"],
                                        commun_data["NUMERO_COMPROBANTE_MODIFICADO"] and commun_data[
                                            "NUMERO_COMPROBANTE_MODIFICADO"] or None,
                                        commun_data["FECHA_COMPROBANTE"],
                                        commun_data["FECHA_PAGO"] and commun_data["FECHA_PAGO"] or None,
                                        commun_data["TIPO_BIENES_SERVICIOS_COMPRADOS"],
                                        commun_data["ITBIS_FACTURADO"],
                                        commun_data["ITBIS_RETENIDO"],
                                        commun_data["MONTO_FACTURADO"],
                                        commun_data["RETENCION_RENTA"],
                                        invoice_id.id,
                                        AFFECTED_NVOICE_ID and AFFECTED_NVOICE_ID or None,
                                        AFFECTED_NVOICE_ID and True or False,
                                        commun_data["ITBIS_FACTURADO_SERVICIOS"]))
                purchase_line += 1

            _logger.info("DGII report {} - - {}".format(count, invoice_id.type))
            count -= 1

        if purchase_report:
            self.create_purchase_lines(purchase_report)

        if sale_report:
            self.create_sales_lines(sale_report)

        self.generate_txt_files()
        from pprint import pprint as pp
        pp(xls_dict)
        self.generate_xls_files(xls_dict)

        self.post_error_list(error_list)