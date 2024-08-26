import frappe
from frappe.permissions import has_permission


@frappe.whitelist()
def update_user_image(name, image):
    frappe.db.sql(f"""
        UPDATE `tabEmployee` 
        SET
        image='{image}'
        WHERE name='{name}';
    """)
    frappe.db.commit()

    return frappe.get_doc('Employee', name)

@frappe.whitelist()
def add_face_id(name, bytesImage):
    frappe.db.sql(f"""
        UPDATE `tabEmployee` 
        SET
        employee_face_id='{bytesImage}'
        WHERE name='{name}';
    """)
    frappe.db.commit()
    data = {}
    data["employee"] = frappe.get_doc('Employee', name)

    return data

@frappe.whitelist()
def user_permission(doctype, action, user, docname=None):
    # Check if the user has permission to read a specific document
    # docname = "your_document_name"  # Replace with the actual document name
    # doctype = "Your DocType"  # Replace with the actual DocType
    # user = "user@example.com"  # Replace with the user's email address

    # if has_permission(doctype, ptype=action, doc=doc, user=user):
    #     # The user has permission to read the document
    #     return f"User has permission to {action} the document."
    # else:
    #     # The user does not have permission to read the document
    #     return "User does not have permission to read the document."
    doc=docname
    # doc = frappe.get_doc("Leave Application", docname)
    if has_permission(doctype, ptype=action, doc=doc, user=user):
        return True
    else:
        return False 
