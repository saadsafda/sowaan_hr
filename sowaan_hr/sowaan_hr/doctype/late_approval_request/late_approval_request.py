# Copyright (c) 2022, Sowaan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LateApprovalRequest(Document):
	def before_save(self):
		att = frappe.get_all("Attendance", filters={
			"employee": ["=",self.employee],
			"attendance_date": ["=", self.late_date],
			"late_entry": ["=",1]
		})
		if len(att) == 0:
			frappe.throw("There is no late on the selected date.")

	def on_submit(self):
		# get the attendance of the said late day
		att = frappe.get_list("Attendance", filters={
			"employee": ["=",self.employee],
			"attendance_date": ["=", self.late_date],
			"late_entry": ["=",1]
		})
		if len(att) > 0:
			isCheckinsFound = False
			att_obj = frappe.get_doc("Attendance", att[0].name)

			# get the checkings of the attendnace day
			checkins = frappe.get_all("Employee Checkin", filters={
				"attendance": ["=",att_obj.name]
			})
			if(len(checkins) > 0):
				isCheckinsFound = True

			# cancel the attendance doc	
			att_obj.cancel()

			# create a new attendance doc and copy all attributes from the cancelled one
			new_att = frappe.new_doc("Attendance")
			new_att.__dict__.update(att_obj.__dict__)
			new_att.docstatus = 1
			new_att.late_approved = True
			new_att.insert()

			# link the employee checkins to the attendance record
			if isCheckinsFound:
				for idx, x in enumerate(checkins):
					check = frappe.get_doc("Employee Checkin", x.name)
					check.attendance = new_att.name
					check.save()
				

			# delete the canceled attendance doc
			att_obj.delete()
			frappe.db.commit()
		else:
			frappe.throw("There is no late on the selected date.")
