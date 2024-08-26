// Copyright (c) 2022, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Late Approval Request', {
	// setup: function(frm) {
	// 	frm.set_query("late_day", function() {
	// 		return {
	// 			filters: [
	// 				["Attendance","late_entry", "=", 1]
	// 			]
	// 		}
	// 	});
	// },
	// "employee":function(frm){
	//     if(frm.doc.employee !== ""){
    // 	    frm.set_query("late_day", function() {
    // 			return {
    // 				filters: [
    // 				    ["Attendance","employee", "=", frm.doc.employee],
    // 					["Attendance","late_entry", "=", 1]
    // 				]
    // 			}
    // 		});
	// 		frm.set_value('late_day','');
	//     }
	// }
});
