from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def get_employee_list():
    employees = frappe.db.get_list(
        "Employee",
        filters={
            "status":"Active"
        },
        fields=["name","employee_name"],
        order_by="employee_name"
    )
    data = ""
    if len(employees) > 0:
        data = {}
        data["employees"] = employees
    return data

@frappe.whitelist()
def get_employee_info(email):
    roles =  frappe.get_roles()
    if ("Employee" in roles) == False:
        raise Exception("You are not allowed to login")

    employees = frappe.db.get_all(
        "Employee",
        filters={
            "user_id": frappe.session.user,
            "status": "Active",
        },
        fields=["name"]
    )
    data = ""
    if len(employees) > 0:
        data = {}
        data["employee"] = frappe.get_doc(
            "Employee", employees[0]["name"]
        )
    return data

@frappe.whitelist()
def get_allowed_locations(employee):
    locations = frappe.db.get_all(
        "Employee GPS Locations",
        filters={
            "employee": employee,
        },
        fields=["name"]
    )
    data = ""
    if len(locations) > 0:
        data = {}
        data["locations"] = frappe.db.sql("""
        select 
            name, 
            location_name, 
            location_gps, 
            allowed_radius 
            from 
            `tabGPS Locations` 
            where 
            name in (
                select 
                location 
                from 
                `tabEmployee GPS Locations Item` 
                where 
                parent =%(name) s
            )

        """, values=locations[0], as_dict=1)
        
    return data

def get_employee_devices(employee):
    devices = frappe.db.get_all(
        "Employee Device Registration",
        filters={
            "employee": employee,
        },
        fields=["name"]
    )
    data = ""
    if len(devices) > 0:
        data = {}
        data["devices"] = frappe.db.sql("""
        select 
            device_id
            from 
            `tabEmployee Device Registration Item` 
            where 
            parent =%(name) s

        """, values=devices[0], as_dict=1)
    return data

def get_allowed_employees():
    allowed_employees = frappe.db.get_all("User Permission", filters={
        "user" : frappe.session.user,
        "allow" : "Employee"
    }, pluck="for_value")

    return allowed_employees

def get_current_emp():
    return frappe.get_value("Employee", {'user_id':frappe.session.user}, 'name')