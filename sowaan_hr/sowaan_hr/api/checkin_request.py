import frappe
from frappe.desk.form.load import getdoc
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp
from sowaan_hr.sowaan_hr.api.workflow import apply_actions
from sowaan_hr.sowaan_hr.api.api import gen_response, sort_by_char_frequency
from sowaan_hr.sowaan_hr.api.workflow import apply_actions, get_doctype_workflow_status


@frappe.whitelist()
def get_checkin_request(employee, status, page):
    try:
        workflow_status = get_doctype_workflow_status("Employee Checkin Request")
        pageSize = 20
        page = int(page)

        if (page <= 0):
            return "Page should be greater or equal of 1"

        filters = {}

        allowed_employees = get_allowed_employees()

        if employee:
            if (len(allowed_employees) > 0 and employee in allowed_employees) or len(allowed_employees) == 0:
                filters["employee"] = employee
            else:
                filters["employee"] = get_current_emp()
        elif len(allowed_employees) > 0:
            filters["employee"] = ["in", allowed_employees]

        if status:
            if len(workflow_status) > 0:
                filters["workflow_state"] = status
            else:
                filters["status"] = status

        getCheckinList = frappe.db.get_list(
            "Employee Checkin Request",
            filters=filters,
            fields=['*'],
            order_by="time DESC",
            start=(page-1)*pageSize,
            page_length=pageSize,
        )

        return getCheckinList
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def create_checkin_request(employee, log_type, time, reason):
    try:
        request = frappe.get_doc({
            "doctype": "Employee Checkin Request",
            "employee": employee,
            "log_type": log_type,
            "time": time,
            "reason": reason
        })
        request.insert()
        frappe.db.commit()

        return request
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def update_checkin_request(name, log_type, time, reason):
    try:
        frappe.db.sql(f"""
            UPDATE `tabEmployee Checkin Request` 
            SET log_type='{log_type}',
            time='{time}',
            reason="{reason}"
            WHERE name='{name}';
        """)
        frappe.db.commit()

        return name
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def submit_checkin_request(name):
    try:
        request = frappe.get_doc("Employee Checkin Request", name)
        request.submit()
        frappe.db.commit()

        return request
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def checkin_request_up_sbm(name, action):
    try:
        doc = frappe.db.get_list("Employee Checkin Request", filters={
                                "name": name}, fields=["*"])

        doc[0].update({"doctype": "Employee Checkin Request"})
        val = apply_actions(frappe.parse_json(doc[0]), action)
        frappe.db.sql(f"""
            UPDATE `tabEmployee Checkin Request` 
            SET workflow_state='{val.workflow_state}'
            WHERE name='{name}';
        """)
        frappe.db.commit()
        return val
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)



@frappe.whitelist()
def checkin_request_status():
    status = get_doctype_workflow_status("Employee Checkin Request")
    if len(status) > 0:
        return sort_by_char_frequency(status)
    else:
        return [{"status": "Draft"}, {"status": "Submitted"}, {"status": "Cancelled"}]


