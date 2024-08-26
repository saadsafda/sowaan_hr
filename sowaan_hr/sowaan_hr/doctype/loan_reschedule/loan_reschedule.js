// Copyright (c) 2023, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loan Reschedule', {
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
	},
	// repayment_date: function (frm) {
	// 	if (frm.doc.loan) {
	// 		frappe.call({
	// 			method: "frappe.client.get",
	// 			args: {
	// 				doctype: "Loan",
	// 				name: frm.doc.loan,
	// 			},
	// 			callback(r) {
	// 				if (r.message) {
	// 					var loan_doc = r.message;

	// 					if (frm.doc.repayment_date) {
	// 						let paymentDate = 0;
	// 						for (let i = 0; i < loan_doc.repayment_schedule.length; i++) {
	// 							const item = loan_doc.repayment_schedule[i];
	// 							if (item.is_accrued == false) {
	// 								paymentDate = item.payment_date;
	// 								break;
	// 							}
	// 						}
	// 						const daysCount = dateDiffInDays(new Date(frm.doc.repayment_date), new Date(paymentDate));
	// 						// const daysCount = dateDiff(doc.repayment_date, paymentDate);
	// 						const monthCount = Math.floor(daysCount / 30.44);
	// 						const values = {
	// 							loan: frm.doc.loan,
	// 							month: monthCount,
	// 							oldDate: frm.doc.repayment_date
	// 						};
	// 						if (frm.doc.loan) {
	// 							frappe.db.sql(`
	// 							select
	// 								date_add(payment_date, interval ${monthCount} month) as payment_date,
	// 								principal_amount,
	// 								interest_amount,
	// 								total_payment,
	// 								balance_loan_amount
	// 							from
	// 								\`tabRepayment Schedule\`
	// 							where
	// 								parent = %(loan)s and
	// 								is_accrued = 0
	// 							order by
	// 								payment_date;
	// 						`, { loan: frm.doc.loan }).then(childTable => {
	// 								for (let i = 0; i < childTable.length; i++) {
	// 									const child = childTable[i];
	// 									frm.doc.append("repayment_dates", child);
	// 								}
	// 								frm.refresh_field('repayment_dates');
	// 							});
	// 						}
	// 					}
	// 				}
	// 			}
	// 		});
	// 	}
	// }
});


// function dateDiffInDays(date1, date2) {
// 	const timeDiff = date2.getTime() - date1.getTime();
// 	const dayDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
// 	return dayDiff;
// }

