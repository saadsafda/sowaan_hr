import frappe
from frappe import _
from sowaan_hr.sowaan_hr.api.attendance import get_monthly_hours

def validate(doc, method):
    monthly_hours = get_monthly_hours(doc.employee, doc.start_date, doc.end_date)
    required_hours = 0
    provided_hours = 0
    less_hours = 0
    for idx, x in enumerate(monthly_hours):
        if x["code"] == "required_hours":
            required_hours = x["count"]
        elif x["code"] == "provided_hours":
            provided_hours = x["count"]
        elif x["code"] == "less_hours":
            less_hours = x["count"]
    
    doc.required_hours = required_hours
    doc.provided_hours = provided_hours
    doc.less_hours = less_hours