// Copyright (c) 2023, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Leave Type Settings', {
	// refresh: function(frm) {

	// }
	synce_leave_allocation: function (frm) {
		frappe.call({
			method: "sowaan_hr.sowaan_hr.utils.allocate_earned_leaves",
			// args: {
			// 	"doc": frm.doc
			// },
			callback: function (r) {
				if (!r.exc) {
					// frm.set_value('access_token', r.message)
					// frm.save();
				}
			},
			// freeze: true,
			// freeze_message: __('Syncing data from Complis...')
		});
	}
});
