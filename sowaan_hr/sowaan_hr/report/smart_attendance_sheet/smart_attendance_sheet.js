// Copyright (c) 2022, Sowaan and contributors
// For license information, please see license.txt
/* eslint-disable */

var d  = new Date();
frappe.query_reports["Smart Attendance Sheet"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: new Date(d.getFullYear(),d.getMonth(),1),//frappe.datetime.str_to_obj(frappe.datetime.add_days(frappe.datetime.get_today(),-2)),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.str_to_obj(frappe.datetime.get_today()),
			reqd: 1
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
			}
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": ["","Branch","Grade","Department","Designation"]
		},
		{
			"fieldname":"summarized_view",
			"label": __("Summarized View"),
			"fieldtype": "Check",
			"Default": 0,
		}
	],
};
