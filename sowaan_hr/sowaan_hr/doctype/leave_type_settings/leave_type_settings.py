# Copyright (c) 2023, Sowaan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class LeaveTypeSettings(Document):
	def validate(self):
		pass
		# date_string = "24-05-2023"  # Replace with your desired date
		# date_format = "%d-%m-%Y"

		# date = datetime.strptime(date_string, date_format)
		# day_of_year = date.timetuple().tm_yday
		# print(f"The day of the year for {date_string} is: {day_of_year}.")

