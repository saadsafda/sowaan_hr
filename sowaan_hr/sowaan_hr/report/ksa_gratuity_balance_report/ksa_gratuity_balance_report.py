# Copyright (c) 2023, Sowaan and contributors
# For license information, please see license.txt

import datetime
from dateutil import relativedelta

import frappe
from sowaan_hr.sowaan_hr.doctype.ksa_gratuity.ksa_gratuity import calculate_gratuity_amount, calculate_employee_total_workings_days, get_last_salary_slip
from frappe import _
from frappe.utils import flt, get_datetime

def execute(filters=None):
	employee_list = frappe.db.get_list('Employee', pluck='name')
	data = []
	for employee in employee_list:
		gratuity_rule = filters.gratuity_rule
		result = calculate_work_experience_and_amount(employee, gratuity_rule, filters.relieving_date)
		data.append({"employee": employee, "gratuity_rule": gratuity_rule,  **result})

	columns, data = [
        {
            'fieldname': 'employee',
            'label': _('Employee'),
            'fieldtype': 'Link',
            'options': 'Employee'
        },
        {
            'fieldname': 'gratuity_rule',
            'label': _('Gratuity Rule'),
            'fieldtype': 'Link',
            'options': 'Gratuity Rule'
        },
        {
            'fieldname': 'current_work_experience',
            'label': _('Current Work Experience'),
            'fieldtype': 'Float',
			'precision': 2,
            'options': ''
        },
		{
            'fieldname': 'years',
            'label': _('Years'),
            'fieldtype': 'Int',
            'options': ''
        },
		{
            'fieldname': 'months',
            'label': _('months'),
            'fieldtype': 'Int',
            'options': ''
        },
		{
            'fieldname': 'days',
            'label': _('days'),
            'fieldtype': 'Int',
            'options': ''
        },
		{
            'fieldname': 'amount',
            'label': _('Amount'),
            'fieldtype': 'Float',
			'precision': 2,
            'options': ''
        }
    ], data
	return columns, data

def calculate_work_experience_and_amount(employee, gratuity_rule, relieving_date):
	gratuity_amount = 0
	data = calculate_work_experience(employee, gratuity_rule, relieving_date)
	sal_slip = get_last_salary_slip(employee)
	if data["current_work_experience"] != 0 and sal_slip != None:
		gratuity_amount = calculate_gratuity_amount(employee, gratuity_rule, data) or 0

	return {
		"current_work_experience": data["current_work_experience"], 
		"years": data["years"],
		"months": data["months"],
		"days": data["days"],
		"amount": gratuity_amount}


def calculate_work_experience(employee, gratuity_rule, relieving_date):

	total_working_days_per_year, minimum_year_for_gratuity = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, ["total_working_days_per_year", "minimum_year_for_gratuity"]
	)

	date_of_joining = frappe.db.get_value(
		"Employee", employee, ["date_of_joining"]
	)
	if not relieving_date:
		frappe.throw(
			_("Please set Relieving Date for employee: {0}")
		)

	method = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, "work_experience_calculation_function"
	)
	data = calculate_employee_total_workings_days(
		employee, date_of_joining, relieving_date
	)

	employee_total_workings_days = data["employee_total_workings_days"]
	non_working_days = data["non_working_days"]
	
	print(employee_total_workings_days, non_working_days)
	# days_per_year = 365.2 if consider_exact_days_per_year == 1 else total_working_days_per_year

	current_work_experience = employee_total_workings_days / total_working_days_per_year or 1
	current_work_experience = get_work_experience_using_method(
		method, current_work_experience, minimum_year_for_gratuity, employee
	)
	# days_in_month = days_per_year/12
	# years = floor(employee_total_workings_days/days_per_year)
	# months = floor((employee_total_workings_days - (years*days_per_year))/days_in_month)
	# days = employee_total_workings_days - (months*days_in_month) - (years*days_per_year)
	
	relieving_date = get_datetime(relieving_date)+datetime.timedelta(days=1)
	relieving_date = get_datetime(relieving_date)+datetime.timedelta(days=-non_working_days)

	date_diff = relativedelta.relativedelta(relieving_date, date_of_joining)


	print('employee_total_workings_days****')
	print(relieving_date)
	# print(employee_total_workings_days)
	# print(days_in_month)
	# print(days_per_year)
	
	return {
		"current_work_experience":current_work_experience,
		"years": date_diff.years,
		"months": date_diff.months,
		"days": date_diff.days
		}


def get_work_experience_using_method(
	method, current_work_experience, minimum_year_for_gratuity, employee
):
	if method == "Round off Work Experience":
		current_work_experience = round(current_work_experience)
	else:
		current_work_experience = (current_work_experience)

	if current_work_experience < minimum_year_for_gratuity:
		current_work_experience = 0
	return current_work_experience
