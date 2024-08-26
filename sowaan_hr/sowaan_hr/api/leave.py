import frappe
from frappe.desk.form.load import getdoc, getdoctype
from frappe.utils import date_diff, now
from sowaan_hr.sowaan_hr.api.workflow import apply_actions, get_doctype_workflow_status
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp, get_employee_info
from sowaan_hr.sowaan_hr.api.api import gen_response, sort_by_char_frequency


@frappe.whitelist()
def get_leaves(employee, status, page):
    try:
        workflow_status = get_doctype_workflow_status("Leave Application")
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
        # elif len(allowed_employees) > 0:
        #     filters["employee"] = ["in", allowed_employees]
        if status:
            if len(workflow_status) > 0:
                filters["workflow_state"] = status
            else:
                filters["status"] = status

        leaves = frappe.db.get_list(
            "Leave Application",
            filters=filters,
            fields=['*'],
            order_by="modified DESC",
            start=(page-1)*pageSize,
            page_length=pageSize
        )

        return leaves
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def create_leave(employee, from_date, to_date, leave_type, description, leave_approver, half_day=False, half_day_date=None):
    try:
        day = date_diff(to_date, from_date)
        if (day > 0 and half_day == True):
            if (half_day_date == None):
                raise Exception("Mandatory fields required in Leave Application")

        leave = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": employee,
            "from_date": from_date,
            "to_date":to_date,
            "leave_type": leave_type,
            "description": description,
            "half_day": half_day,
            "half_day_date": half_day_date,
            "leave_approver": leave_approver,
            "leave_approver_name": leave_approver
        }).insert()
        frappe.db.commit()

        return leave
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def update_leave(name, from_date, to_date, leave_type, description, half_day=False, half_day_date=None):
    try:
        day = date_diff(to_date, from_date)
        if (day > 0 and half_day == True):
            if (half_day_date == None):
                raise Exception("Mandatory fields required in Leave Application")

        nowTime = now()
        doc = frappe.get_doc('Leave Application',name)   
        doc.from_date=from_date
        doc.to_date=to_date
        doc.leave_type=leave_type
        doc.description=description
        doc.half_day=half_day
        doc.half_day_date=half_day_date if half_day == True else None
        doc.save()
        frappe.db.commit()
        
        return doc
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)
    
@frappe.whitelist()
def submit_leave(name):
    try:
        request = frappe.get_doc("Leave Application", name)
        request.status = "Approved"
        request.submit()
        frappe.db.commit()

        return request
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)

@frappe.whitelist()
def delete_leave(name):
    frappe.delete_doc('Leave Application', name)
    return "Leave Application deleted"


@frappe.whitelist()
def leave_up_sbm(name, action):
    try:
        doc = frappe.db.get_list("Leave Application", filters={
                                "name": name}, fields=["*"])

        doc[0].update({"doctype": "Leave Application"})
        val = apply_actions(frappe.parse_json(doc[0]), action)
        frappe.db.sql(f"""
            UPDATE `tabLeave Application` 
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
def leave_status():
    status = get_doctype_workflow_status("Leave Application")
    if len(status) > 0:
        return sort_by_char_frequency(status)
    else:
        return [{"status": "Open"}, {"status": "Approved"}, {"status": "Rejected"}, {"status": "Cancelled"}]

@frappe.whitelist()
def get_doctype(doctype):
    getdoctype(doctype)
