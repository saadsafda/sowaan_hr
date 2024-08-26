from __future__ import unicode_literals
from datetime import date, timedelta
import itertools
from tabnanny import check
import frappe
from frappe.utils import (
    nowdate, getdate, get_datetime, add_to_date
)
from frappe import _
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_end_date
from hrms.hr.utils import get_holiday_dates_for_employee
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp
from hrms.hr.doctype.shift_assignment.shift_assignment import (
    get_actual_start_end_datetime_of_shift, get_shifts_for_date
)
from erpnext.setup.doctype.employee.employee import is_holiday
from sowaan_hr.sowaan_hr.api.api import gen_response, sort_by_char_frequency


@frappe.whitelist()
def get_payroll_date(employee):
    today = getdate(nowdate())
    salary_slips = frappe.db.get_all(
        "Salary Slip",
        filters={
            'docstatus': ['!=', 2],
            'posting_date': ['<', today],
            'employee': ['=', employee]
        },

        fields=["start_date", "end_date", "payroll_frequency", "name"],
        order_by="end_date desc",
    )
    data = {}
    if len(salary_slips) > 0:
        salary_slip = salary_slips[0]
        # return salary_slip
        pay_start = getdate(salary_slip["start_date"])
        pay_end = getdate(salary_slip["end_date"])
        next_pay_start = add_to_date(pay_end, days=1)
        start_date = getdate(str(today.year)+'-' +
                             str(today.month)+'-'+str(next_pay_start.day))
        if (start_date > today):
            start_date = add_to_date(start_date, months=-1)

        end_date = get_end_date(
            frequency=salary_slip['payroll_frequency'], start_date=start_date)
        data["start_date"] = start_date
        data["end_date"] = end_date["end_date"]
    else:
        data["start_date"] = today.replace(day=1)
        data["end_date"] = today

    return data


@frappe.whitelist()
def get_attendance(employee, status, from_date, to_date, page):
    try:
        pageSize = 20
        page = int(page)

        if (page <= 0):
            return "Page should be greater or equal of 1"

        filters = {
            "docstatus": 1,
            "attendance_date": ["between", (getdate(from_date), getdate(to_date))]
        }

        allowed_employees = get_allowed_employees()

        if employee:
            if (len(allowed_employees) > 0 and employee in allowed_employees) or len(allowed_employees) == 0:
                filters["employee"] = employee
            else:
                filters["employee"] = get_current_emp()
        elif len(allowed_employees) > 0:
            filters["employee"] = ["in", allowed_employees]

        if status:
            filters["status"] = status

        attendance = frappe.db.get_all(
            "Attendance",
            filters=filters,
            fields=["name", "employee", "employee_name", "working_hours", "status",
                    "attendance_date", "in_time", "out_time", "late_entry", "early_exit"],
            order_by="attendance_date desc",
            start=(page-1)*pageSize,
            page_length=pageSize,
        )

        attendance_statuses = frappe.db.get_all(
            "Attendance",
            fields=["status"],
            distinct=True
        )
        shorted_attendance_statuses = sort_by_char_frequency(attendance_statuses)

        return [attendance, shorted_attendance_statuses]
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e) 


@frappe.whitelist()
def get_attendance_summary_statuswise(employee, from_date, to_date):
    filters = {
        "docstatus": 1,
        "attendance_date": ["between", (getdate(from_date), getdate(to_date))]
    }
    allowed_employees = get_allowed_employees()

    if employee:
        if (len(allowed_employees) > 0 and employee in allowed_employees) or len(allowed_employees) == 0:
            filters["employee"] = employee
        else:
            filters["employee"] = get_current_emp()
    elif len(allowed_employees) > 0:
        filters["employee"] = ["in", allowed_employees]

    att_list = frappe.db.get_all(
        "Attendance",
        filters=filters,
        fields=['status', 'attendance_date'],
        order_by="status desc",
    )
    att_group = itertools.groupby(
        att_list, key=lambda x: x["status"]
    )

    result = []
    for key, group in att_group:
        result.append({"status": key, "count": len(list(group))})

    # get late entries
    filters["status"] = "Present"
    filters["late_entry"] = 1
    filters["late_approved"] = 0
    lates = len(frappe.db.get_all(
        "Attendance",
        filters=filters
    ))

    # get early departures
    filters["status"] = "Present"
    filters["early_exit"] = 1
    early = len(frappe.db.get_all(
        "Attendance",
        filters=filters
    ))

    # get holidays
    holidays = get_holiday_dates_for_employee(employee, from_date, to_date)
    holidays = len(
        list(filter(lambda x: getdate(x) < getdate(nowdate()), holidays)))

    result.append({"status": "Late", "count": lates})
    result.append({"status": "Early", "count": early})
    result.append({"status": "Holiday", "count": holidays})

    return result

# the below method (get_attendance_summary) is deprecated and will be removed in next major release,
# please use (get_attendance_summary_statuswise) instead


@frappe.whitelist()
def get_attendance_summary(employee, from_date, to_date):
    filters = {
        "docstatus": 1,
        "attendance_date": ["between", (getdate(from_date), getdate(to_date))]
    }
    if (employee):
        filters["employee"] = employee

    filters["status"] = ["in", ["Present", "Half Day"]]
    presents = len(frappe.db.get_all(
        "Attendance",
        filters=filters
    ))

    filters["status"] = "Absent"
    absents = len(frappe.db.get_all(
        "Attendance",
        filters=filters

    ))

    filters["status"] = "Present"
    filters["late_entry"] = 1
    filters["late_approved"] = 0
    lates = len(frappe.db.get_all(
        "Attendance",
        filters=filters
    ))

    filters["status"] = "Present"
    filters["early_exit"] = 1
    early = len(frappe.db.get_all(
        "Attendance",
        filters=filters
    ))

    return {
        "presents": presents,
        "absents": absents,
        "lates": lates,
        "early": early
    }

@frappe.whitelist()
def get_monthly_hours(employee, from_date, to_date):

    # payroll_based_on = frappe.db.get_value("Payroll Settings", None, "payroll_based_on")
    standard_working_hours = float(frappe.db.get_value(
        "HR Settings", None, "standard_working_hours"))
    # if standard_working_hours <= 0:
    #     return ""
    include_holidays_in_total_working_days = frappe.db.get_single_value(
        "Payroll Settings", "include_holidays_in_total_working_days"
    )

    employee_detail = frappe.get_doc("Employee", employee)

    holidays = get_holiday_dates_for_employee(employee, from_date, to_date)

    joining_date, relieving_date = frappe.get_cached_value(
        "Employee", employee, ["date_of_joining", "relieving_date"]
    )

    if joining_date and (getdate(from_date) < joining_date <= getdate(to_date)):
        from_date = joining_date
    if relieving_date and (getdate(from_date) <= relieving_date < getdate(to_date)):
        to_date = relieving_date

    att = frappe.get_all("Attendance", filters={
        "employee": ["=", employee],
        "docstatus": 1,
        "attendance_date": ["between", (getdate(from_date), getdate(to_date))],
    }, fields=['*'])

    required_hours = 0
    provided_hours = 0

    working_dates = [getdate(from_date)+timedelta(days=x) for x in range(
        (add_to_date(getdate(to_date), days=1)-getdate(from_date)).days)]

    for idx, day in enumerate(working_dates):
        if not is_holiday(employee, day) or include_holidays_in_total_working_days:
           
            shifts = get_shifts_for_date(
                employee, get_datetime(day)
            )
            if len(shifts) == 0:
                current_shift = frappe.get_doc(
                    "Shift Type", employee_detail.default_shift)
            else:
                current_shift = frappe.get_doc("Shift Type", shifts[0].shift_type)

            if not current_shift == None and current_shift.required_hours > 0:
                required_hours += current_shift.required_hours
            else:
                required_hours += standard_working_hours

    # return provided_hours,required_hours

    # provided_hours = sum(c.working_hours for c in att)
    if include_holidays_in_total_working_days:
        holidays_before_today = list(
            filter(lambda x: getdate(x) < getdate(nowdate()), holidays))
        for idx, x in enumerate(holidays_before_today):
            
            shifts = get_shifts_for_date(
                employee, get_datetime(day)
            )
            if len(shifts) == 0:
                current_shift = frappe.get_doc(
                    "Shift Type", employee_detail.default_shift)
            else:
                current_shift = frappe.get_doc("Shift Type", shifts[0].shift_type)

            if not current_shift == None and current_shift.required_hours > 0:
                provided_hours += current_shift.required_hours
            else:
                provided_hours += standard_working_hours

        # provided_hours += len(holidays_before_today)*standard_working_hours

    for idx, x in enumerate(att):
        today_required_hours = standard_working_hours
        allow_monthly_flexible_hours = False
        if x.shift:
            current_shift = frappe.get_doc("Shift Type", x.shift)
            if current_shift.required_hours > 0:
                today_required_hours = current_shift.required_hours
            if current_shift.allow_to_complete_required_hours_during_the_whole_month == 1:
                allow_monthly_flexible_hours = True

        if x.working_hours > 0:
            if allow_monthly_flexible_hours:
                provided_hours += x.working_hours
            else:
                provided_hours += today_required_hours if x.working_hours > today_required_hours else x.working_hours

        # Half day and on leave hours logic
        if (x.status == "Half Day" or x.status == "On Leave") and x.leave_type != '' and x.leave_type != None:
            leave = frappe.get_doc("Leave Type", x.leave_type)
            if x.status == "Half Day" and leave and not leave.is_lwp:
                provided_hours += today_required_hours * 0.5
            elif x.status == "On Leave" and leave and leave.is_ppl:
                provided_hours += today_required_hours * \
                    (1-leave.fraction_of_daily_salary_per_leave)
            elif x.status == "On Leave" and leave and not leave.is_ppl and not leave.is_lwp:
                provided_hours += today_required_hours

        # Half days with no working hours logic
        if x.status == "Half Day" and x.working_hours == 0 and (x.leave_type == '' or x.leave_type == None):
            daily_wages_fraction_for_half_day = float(frappe.db.get_value(
                "Payroll Settings", None, "daily_wages_fraction_for_half_day"))
            if daily_wages_fraction_for_half_day:
                provided_hours += today_required_hours * daily_wages_fraction_for_half_day

    # return temp_required_hours,provided_hours,required_hours

    less_hours = round(required_hours-provided_hours, 2)

    result = []
    result.append({"status": "Required Hours", "count": round(
        required_hours, 2), "isOk": True, "code": "required_hours"})
    result.append({"status": "Provided Hours", "count": round(provided_hours, 2),
                  "isOk": True if less_hours <= 0 else False, "code": "provided_hours"})
    result.append({"status": "Less Hours", "count": less_hours if less_hours >
                  0 else 0, "isOk": True if less_hours <= 0 else False, "code": "less_hours"})

    return result
