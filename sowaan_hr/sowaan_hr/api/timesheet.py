import frappe
from sowaan_hr.sowaan_hr.api.workflow import apply_actions, get_doctype_workflow_status
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp
from sowaan_hr.sowaan_hr.api.api import gen_response


@frappe.whitelist()
def get_timesheet_list(employee, page):
    try:
        pageSize = 20
        page = int(page)

        if(page <= 0):
            return "Page should be greater or equal of 1"

        filters = {}

        allowed_employees = get_allowed_employees()
        if employee:
            if (len(allowed_employees) > 0 and employee in allowed_employees) or len(allowed_employees) == 0:
                filters["employee"] = employee
            else:
                filters["employee"] = get_current_emp()
        
        timesheet = frappe.db.get_list(
            "Timesheet",
            filters=filters,
            fields=['*'],
            order_by="modified DESC",
            start=(page-1)*pageSize,
            page_length=pageSize
        )
        
        return timesheet
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)

@frappe.whitelist()
def get_single_timesheet(timesheet):
    try:
        return frappe.get_doc("Timesheet", timesheet)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)

@frappe.whitelist()
def create_timesheet(employee, time_logs):
    try:
        request = frappe.get_doc({
            "doctype": "Timesheet",
            "employee": employee,
            "time_logs": time_logs
        })
        request.insert()
        frappe.db.commit()

        return request
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)