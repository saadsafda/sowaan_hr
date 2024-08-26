# Copyright (c) 2023, Sowaan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import (
    flt,
    formatdate,
    get_datetime,
    getdate,
    today,
	add_days
)
from frappe.model.document import Document

class LeaveBalanceAdjustment(Document):
	def before_submit(self):
		self.leave_ledger_entry = update_previous_leave_allocation(self.leave_allocation, self.balance_allocation)
		
	
	def on_cancel(self):
		update_previous_leave_allocation_revert(self.leave_allocation, self.balance_allocation, self.leave_ledger_entry)
	

def update_previous_leave_allocation(allocation, earned_leaves):
    allocation = frappe.get_doc("Leave Allocation", allocation)
    new_allocation = flt(
        allocation.total_leaves_allocated) + flt(earned_leaves)

    # new_leaves_allocated = flt(
    #     allocation.new_leaves_allocated) + flt(earned_leaves)

    

    
    if new_allocation != allocation.total_leaves_allocated:
        today_date = today()

        allocation.db_set("total_leaves_allocated",
                          new_allocation, update_modified=False)
        # allocation.db_set("new_leaves_allocated",
        #                   new_leaves_allocated, update_modified=False)
        
        ledger = create_additional_leave_ledger_entry(
            allocation, earned_leaves, today_date)

        # print("ledger*********")
        # print(ledger)

        text = _("allocated {0} leave(s) via leave balance adjustment on {1}").format(
			frappe.bold(earned_leaves), frappe.bold(formatdate(today_date))
		)

        allocation.add_comment(comment_type="Info", text=text)

        return ledger

def update_previous_leave_allocation_revert(allocation, earned_leaves, leave_ledger_entry):
    allocation = frappe.get_doc("Leave Allocation", allocation)
    new_allocation = flt(
        allocation.total_leaves_allocated) - flt(earned_leaves)

    # new_leaves_allocated = flt(
    #     allocation.new_leaves_allocated) - flt(earned_leaves)

    
    if new_allocation != allocation.total_leaves_allocated:
        today_date = today()

        allocation.db_set("total_leaves_allocated",
                          new_allocation, update_modified=False)
        # allocation.db_set("new_leaves_allocated",
        #                   new_leaves_allocated, update_modified=False)
        
        if leave_ledger_entry:
            ledger_entry = frappe.get_doc("Leave Ledger Entry", leave_ledger_entry)
            ledger_entry.db_set("is_expired",
                          1, update_modified=False)
            ledger_entry.cancel()

        text = _("unallocated {0} leave(s) via leave balance adjustment on {1}").format(
			frappe.bold(earned_leaves), frappe.bold(formatdate(today_date))
		)

        allocation.add_comment(comment_type="Info", text=text)

def create_additional_leave_ledger_entry(allocation, leaves, date):
    """Create leave ledger entry for leave types"""
   
    args = dict(
		leaves=leaves,
		from_date=allocation.from_date,
		to_date=allocation.to_date,
		is_carry_forward=0,
	)

    return create_leave_ledger_entry(allocation, args)

def create_leave_ledger_entry(ref_doc, args):
    ledger = frappe._dict(
		doctype="Leave Ledger Entry",
		employee=ref_doc.employee,
		employee_name=ref_doc.employee_name,
		leave_type=ref_doc.leave_type,
		transaction_type=ref_doc.doctype,
		transaction_name=ref_doc.name,
		is_carry_forward=0,
		is_expired=0,
		is_lwp=0,
	)
    ledger.update(args)

    doc = frappe.get_doc(ledger)
    doc.flags.ignore_permissions = 1
    doc.submit()

    return doc.name
		
