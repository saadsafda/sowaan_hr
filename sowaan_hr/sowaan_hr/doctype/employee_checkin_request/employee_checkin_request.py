# Copyright (c) 2022, Sowaan and contributors
# For license information, please see license.txt

import frappe
import datetime
from datetime import datetime
from frappe.utils import (
    getdate
)
from frappe.model.document import Document

class EmployeeCheckinRequest(Document):
	def before_save(self):
		self.checkin_marked = ""
		
	def before_submit(self):
		print('hello')
		checkin = frappe.new_doc("Employee Checkin")
		checkin.user = frappe.session.user
		checkin.employee = self.employee
		checkin.log_type = self.log_type
		checkin.time = self.time
		checkin.insert(ignore_permissions=True)
		self.checkin_marked = checkin.name

		# cancel the attendance record of that day
		att = frappe.db.get_all("Attendance", filters={
			"employee": self.employee,
			"attendance_date": getdate(self.time),
			"docstatus": 1
		})

		if len(att) > 0:
			att_obj = frappe.get_doc("Attendance", att[0].name)
			# get the checkings of the attendnace day
			checkins = frappe.get_all("Employee Checkin", filters={
				"attendance": ["=",att_obj.name]
			})
			
			if len(checkins) > 0:
				for idx, x in enumerate(checkins):
					check = frappe.get_doc("Employee Checkin", x.name)
					check.shift_actual_start = checkin.shift_actual_start
					check.save()

			att_obj.cancel()


	def before_cancel(self):
		checkin = frappe.get_doc("Employee Checkin",self.checkin_marked)
		if checkin.attendance:
			frappe.throw("Attendance is already marked for this checkin request. Please cancel the attendance first if you really want to cancel this.")

		EmployeeCheckinRequest = frappe.qb.DocType("Employee Checkin Request")
		(frappe.qb.update(EmployeeCheckinRequest)
				.set("checkin_marked", "")
				.where(EmployeeCheckinRequest.name == self.name)).run()

		checkin.delete()
		self.checkin_marked = ""
		# self.save()
