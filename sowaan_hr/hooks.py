from . import __version__ as app_version

app_name = "sowaan_hr"
app_title = "Sowaan Hr"
app_publisher = "Sowaan"
app_description = "Modern HR features"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@sowaan.com"
app_license = "MIT"

fixtures = [
	{
		"doctype":"Custom Field",
		"filters":[
			[
				"fieldname",
                "in",
				(
					"gps_location", "marked_gps", "map", "checkout_entry", "required_hours", "allow_to_complete_required_hours_during_the_whole_month",
                    "late_approved", "custom_shift_roaster"
				)
			]
		]
	}, 
	{
		"doctype":"Client Script",
		"filters":[
			[
				"dt",
                "in",
				(
					"Employee Checkin"
				)
			]
		]
	},
	{
		"doctype":"Server Script",
		"filters":[
			[
				"reference_doctype",
                "in",
				(
					"Attendance"
				)
			]
		]
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sowaan_hr/css/sowaan_hr.css"
# app_include_js = "/assets/sowaan_hr/js/sowaan_hr.js"

# include js, css files in header of web template
# web_include_css = "/assets/sowaan_hr/css/sowaan_hr.css"
# web_include_js = "/assets/sowaan_hr/js/sowaan_hr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sowaan_hr/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "sowaan_hr.install.before_install"
# after_install = "sowaan_hr.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sowaan_hr.uninstall.before_uninstall"
# after_uninstall = "sowaan_hr.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sowaan_hr.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Payment Entry": "sowaan_hr.overrides.employee_payment_entry.EmployeePaymentEntry",
    "Salary Slip": "sowaan_hr.overrides.employee_salary_slip.EmployeeSalarySlip",
    # "Payroll Period": "sowaan_hr.overrides.employee_payroll_period.EmployeePayrollPeriod",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# doc_events = {
# 	"Salary Slip":{
# 		"validate": "sowaan_hr.sowaan_hr.api.salary_slip.validate"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sowaan_hr.tasks.all"
# 	],
# 	"daily": [
# 		"sowaan_hr.tasks.daily"
# 	],
# 	"hourly": [
# 		"sowaan_hr.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sowaan_hr.tasks.weekly"
# 	]
# 	"monthly": [
# 		"sowaan_hr.tasks.monthly"
# 	]
# }

# Testing
# -------
advance_payment_doctypes = ["KSA Gratuity"]
# before_tests = "sowaan_hr.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sowaan_hr.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sowaan_hr.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sowaan_hr.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
