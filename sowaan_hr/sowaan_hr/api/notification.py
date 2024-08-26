import frappe
from sowaan_hr.sowaan_hr.api.api import gen_response

@frappe.whitelist()
def get_notification_log(page):
    try:
        pageSize = 20
        page = int(page)
        
        if(page <= 0):
            return "Page should be greater or equal of 1"

        logs = frappe.db.get_list(
            "Notification Log",
            fields=["*"],
            order_by="creation desc",
            start=(page-1)*pageSize,
            page_length=pageSize,
        )

        return logs
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)

@frappe.whitelist()
def get_notification_length():
    logs = frappe.db.get_list(
        "Notification Log")
    total_count = len(logs)
    return total_count