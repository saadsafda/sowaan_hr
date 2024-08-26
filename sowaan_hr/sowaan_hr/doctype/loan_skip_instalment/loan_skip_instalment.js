// Copyright (c) 2023, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan Skip Instalment', {
	// refresh: function(frm) {

	// }
	loan: function (frm) {
		if (frm.doc.loan) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Loan",
					name: frm.doc.loan,
				},
				callback(r) {
					if (r.message) {
						var loan_doc = r.message;
						frm.set_value('applicant_name', loan_doc.applicant_name)
						frm.set_value('repayment_method', loan_doc.repayment_method)
						frm.set_value('repayment_periods', loan_doc.repayment_periods)
						frm.set_value('loan_amount', loan_doc.loan_amount)
					}
				}
			});
		}
	}
});
