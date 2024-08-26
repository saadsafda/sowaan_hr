from __future__ import unicode_literals
import json
import frappe
from frappe.utils import nowdate, flt, cstr
from frappe import _

@frappe.whitelist()
def get_salary_months(employee):
    months = frappe.db.get_list(
        "Salary Slip",
        filters={
            "employee":employee,
            "docstatus":1
        },
        fields=["name","start_date","end_date"],
        order_by="end_date desc",
    )

    for idx, x in enumerate(months):
        x["month"] = x.end_date.strftime("%b %Y")

    return months

@frappe.whitelist()
def get_salary_slip(salary_slip):
    slip = frappe.get_doc(
        "Salary Slip",
        salary_slip
    )
    result = {}
    result["net_pay"] = slip.net_pay
    result["gross_pay"] = slip.gross_pay
    result["total_in_words"] = slip.total_in_words
    
    result["earnings"] = []
    for idx, x in enumerate(slip.earnings):
        earnings = {}
        earnings["salary_component"] = x.salary_component
        earnings["amount"] = x.amount
        result["earnings"].append(earnings)

    result["deductions"] = []
    for idx, x in enumerate(slip.deductions):
        deductions = {}
        deductions["salary_component"] = x.salary_component
        deductions["amount"] = x.amount
        result["deductions"].append(deductions)

    if hasattr(slip, 'loans') and slip.loans:
        result["loans"] = []
        for idx, x in enumerate(slip.loans):
            loans = {}
            loan_doc = frappe.get_doc("Loan", x.loan)
            loans["loan_type"] = loan_doc.loan_type
            loans["total_payment"] = x.total_payment
            result["loans"].append(loans)

    if hasattr(slip, 'leave_details') and slip.leave_details:
        result["leave_details"] = []
        for idx, x in enumerate(slip.leave_details):
            leave_details = {}
            leave_details["leave_type"] = x.leave_type
            leave_details["allocated"] = x.total_allocated_leaves
            leave_details["used"] = x.used_leaves
            leave_details["pending"] = x.pending_leaves
            leave_details["expired"] = x.expired_leaves
            leave_details["available"] = x.available_leaves
            result["leave_details"].append(leave_details)
    print(result, "cjecking result")
    
    return result