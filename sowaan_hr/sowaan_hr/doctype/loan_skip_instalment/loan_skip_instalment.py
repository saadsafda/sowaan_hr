# Copyright (c) 2023, Sowaan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class LoanSkipInstalment(Document):
    def validate(doc):
        doc.repayment_dates.clear()
        loan = frappe.get_doc("Loan", doc.loan)
        doc.applicant_name = loan.applicant_name
        doc.repayment_method = loan.repayment_method
        doc.repayment_periods = loan.repayment_periods
        doc.loan_amount = loan.loan_amount
        # payment_date = 0
        # for item in loan.repayment_schedule:
        #     if item.is_accrued == False:
        #         payment_date = item.payment_date
        #         break
        # days_count = date_diff(doc.repayment_date, payment_date)
        # month_count = int(days_count / 30.44)
        values = {'loan': doc.loan, 'month': doc.no_of_months_to_skip}
        if doc.loan:
            childTable = frappe.db.sql("""
				select date_add(payment_date, interval %(month)s month) as payment_date,
				principal_amount,
				interest_amount,
				total_payment,
				balance_loan_amount
				from `tabRepayment Schedule`
				where
				parent=%(loan)s and
				is_accrued=0
				order by
				payment_date;
			""", values=values, as_dict=1)
            for child in childTable:
                doc.append("repayment_dates", child)

    def on_submit(doc):
        update_childTable(doc)


def update_childTable(doc):
    # payment_date = 0
    # loan = frappe.get_doc("Loan", doc.loan)
    # for item in loan.repayment_schedule:
    #     if item.is_accrued == False:
    #         payment_date = item.payment_date
    #         break
    # days_count = date_diff(doc.repayment_date, payment_date)
    # month_count = int(days_count / 30.44)
    values = {'loan': doc.loan,
              'month': doc.no_of_months_to_skip}
    query = """
            UPDATE `tabRepayment Schedule`
            SET payment_date=date_add(payment_date, interval %(month)s month)
            WHERE parent = %(loan)s and is_accrued=0;
        """
    frappe.db.sql(query, values=values, as_dict=0)
