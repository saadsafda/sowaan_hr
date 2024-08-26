import frappe
from frappe import utils
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp
from hrms.hr.doctype.leave_application.leave_application import get_leave_details
from sowaan_hr.sowaan_hr.api.api import gen_response

@frappe.whitelist()
def get_leave_list(employee):
    doc = get_leave_details(employee, frappe.utils.nowdate())
    response = dict(
        doc["leave_allocation"]
    )

    return doc

@frappe.whitelist()
def get_leave_types(employee):
    leaveAllocation = frappe.db.get_list(
    "Leave Allocation",
    filters={"employee": employee, "docstatus": 1},
    fields=["leave_type", "total_leaves_allocated"]
    )
   
    array_of_strings = [obj["leave_type"] for obj in leaveAllocation]
    leaveTypeList = frappe.db.get_list(
        "Leave Type",
        filters=[['name', 'in', array_of_strings]]
    )
    
    return leaveTypeList

@frappe.whitelist()
def get_leave_allocation(employee):
    try:
        if not employee:
            employee = get_current_emp()
        leave_details = get_leave_details(employee, frappe.utils.nowdate())
        leave_allocation = leave_details["leave_allocation"]
        response = [
                {
                    "leave_type": leave_type,
                    **leave_data
                } for leave_type, leave_data in leave_allocation.items()
            ]

        return response
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)

@frappe.whitelist()
def get_leave_allocation_details(employee, leaveType):
    leaveAllocationDetails = frappe.db.get_list(
        "Leave Allocation",
        filters={"leave_type": leaveType},
        fields=["to_date"]
    )
    doc = get_leave_details(employee, frappe.utils.nowdate())
    response = doc["leave_allocation"][leaveType]
    response.update(leaveAllocationDetails[0])

    return response
