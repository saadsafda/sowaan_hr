import frappe
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp

@frappe.whitelist()
def get_loans_list(employee, page):
    try:
        pageSize = 15
        page = int(page)

        if(page <= 0):
            return "Page should be greater or equal of 1"

        filters = {}

        allowed_employees = get_allowed_employees()
        
        if employee:
            if (len(allowed_employees) > 0 and employee in allowed_employees) or len(allowed_employees) == 0:
                filters["applicant"] = employee
            else:
                filters["applicant"] = get_current_emp()
        elif len(allowed_employees) > 0:
            filters["applicant"] = ["in", allowed_employees]
        
        loans = frappe.db.get_list(
            "Loan",
            filters=filters,
            fields=['*'],
            order_by="modified DESC",
            start=(page-1)*pageSize,
            page_length=pageSize
        )
        print(loans, "check loans")
        return loans
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def get_single_loan(name):
    try:
        doc = frappe.get_doc("Loan", name, fields=["*"])

        return doc
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)