// Copyright (c) 2023, Sowaan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["KSA Gratuity Balance Report"] = {
	"filters": [
        {
            fieldname: 'gratuity_rule',
            label: __('Gratuity Rule'),
            fieldtype: 'Link',
            options: 'Gratuity Rule',
			mandatory: 1,
            default: frappe.defaults.get_user_default('gratuity_rule')
        },
        {
            fieldname: 'relieving_date',
            label: __('Relieving Date'),
            fieldtype: 'Date',
			mandatory: 1,
			default: frappe.datetime.get_today()
        }
    ]
};
