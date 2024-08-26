import frappe
from frappe.desk.form.load import getdoc
from frappe.utils import now
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp
from sowaan_hr.sowaan_hr.api.workflow import apply_actions

@frappe.whitelist()
def get_late_approver(employee, page):
    pageSize = 15
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

    lateApproverList = frappe.db.get_list(
        "Late Approval Request",
        filters=filters,
        fields=['name', 'employee', 'employee_name', 'late_date',
                'docstatus', 'workflow_state', 'reason'],
        order_by="modified DESC",
        start=(page-1)*pageSize,
        page_length=pageSize,
    )

    return lateApproverList


@frappe.whitelist()
def get_single_doc(name):
    doc = frappe.db.get_list(
        "Late Approval Request",
        filters={
            'name': ["=", name]
        },
        fields=['*'],
    )

    return doc


@frappe.whitelist()
def create_late_approver(employee, late_date, reason):
    request = frappe.get_doc({
        "doctype": "Late Approval Request",
        "employee": employee,
        "late_date": late_date,
        "reason": reason,
    })
    request.insert()
    frappe.db.commit()

    return request


@frappe.whitelist()
def update_late_approver(name, late_date, reason):
    nowTime = now()
    frappe.db.sql(f"""
        UPDATE `tabLate Approval Request` 
        SET
        late_date='{late_date}',
        reason="{reason}",
        modified="{nowTime}"
        WHERE name='{name}';
    """)
    frappe.db.commit()

    return name


@frappe.whitelist()
def late_approval_up_sbm(name, action):
    doc = frappe.db.get_list("Late Approval Request", filters={
                             "name": name}, fields=["*"])

    doc[0].update({"doctype": "Late Approval Request"})
    val = apply_actions(frappe.parse_json(doc[0]), action)
    frappe.db.sql(f"""
        UPDATE `tabLate Approval Request` 
        SET workflow_state='{val.workflow_state}'
        WHERE name='{name}';
    """)
    frappe.db.commit()
    return val
