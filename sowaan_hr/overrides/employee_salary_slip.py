import frappe
from hrms.payroll.doctype.salary_slip.salary_slip import (SalarySlip, calculate_tax_by_tax_slab)
from frappe.utils import (
	add_days,
	ceil,
	cint,
	cstr,
	date_diff,
	floor,
	flt,
	formatdate,
	get_first_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
)
from hrms.payroll.doctype.salary_slip.salary_slip_loan_utils import (
	set_loan_repayment,
)
from sowaan_hr.overrides.employee_payroll_period import (get_period_factor)


class EmployeeSalarySlip(SalarySlip):
    def update_payment_status_for_gratuity(self):
        additional_salary = frappe.db.get_all(
            "Additional Salary",
            filters={
                "payroll_date": ("between", [self.start_date, self.end_date]),
                "employee": self.employee,
                "ref_doctype": "KSA Gratuity",
                "docstatus": 1,
            },
            fields=["ref_docname", "name"],
            limit=1,
        )

        if additional_salary:
            status = "Paid" if self.docstatus == 1 else "Unpaid"
            if additional_salary[0].name in [entry.additional_salary for entry in self.earnings]:
                frappe.db.set_value("KSA Gratuity", additional_salary[0].ref_docname, "status", status)

    def get_tax_paid_in_period(self, start_date, end_date, tax_component):
		# find total_tax_paid, tax paid for benefit, additional_salary
        total_tax_paid = self.get_salary_slip_details(
            start_date,
            end_date,
            parentfield="deductions",
            salary_component=tax_component,
            variable_based_on_taxable_salary=1,
        )

        tax_deducted_till_date = self.get_opening_for("tax_deducted_till_date", start_date, end_date)

        # Minus the amount from annual tax that is already paid to tax authorities
        total_extra_tax = 0
        if frappe.db.exists("DocType", "Paid Income Tax"):
            total_extra_tax = flt(frappe.db.sql("""
                select 
                    sum(pit.amount) 
                from 
                    `tabPaid Income Tax` pit
                where
                    pit.docstatus=1
                    and %(from_date)s>=pit.period_from
                    and  %(to_date)s<=pit.period_to
                    and pit.employee=%(employee)s
            """,{
                "employee": self.employee,
                "from_date": start_date,
                "to_date": end_date
            })[0][0])

        # Minus the previous additional monthly tax
        extra_current_tax_amount = 0
        if frappe.db.exists("DocType", "Paid Income Tax Monthly"):
            extra_current_tax_amount = flt(frappe.db.sql("""
                select 
                    sum(pitm.amount) 
                from 
                    `tabPaid Income Tax Monthly` pitm
                where
                    pitm.docstatus=1
                    and %(from_date)s>=pitm.period_from
                    and  %(to_date)s<=pitm.period_to
                    and pitm.payroll_date < %(from_date)s
                    and pitm.payroll_date < %(to_date)s
                    and pitm.employee=%(employee)s
            """,{
                "employee": self.employee,
                "from_date": self.start_date,
                "to_date": self.end_date
            })[0][0])

            
        return total_tax_paid + tax_deducted_till_date + total_extra_tax + extra_current_tax_amount
    
    def calculate_variable_tax(self, tax_component):
        self.previous_total_paid_taxes = self.get_tax_paid_in_period(
            self.payroll_period.start_date, self.start_date, tax_component
        )

        # Structured tax amount
        eval_locals, default_data = self.get_data_for_eval()
        self.total_structured_tax_amount = calculate_tax_by_tax_slab(
            self.total_taxable_earnings_without_full_tax_addl_components,
            self.tax_slab,
            self.whitelisted_globals,
            eval_locals,
        )

        self.current_structured_tax_amount = (
            self.total_structured_tax_amount - self.previous_total_paid_taxes
        ) / self.remaining_sub_periods

        # Total taxable earnings with additional earnings with full tax
        self.full_tax_on_additional_earnings = 0.0
        if self.current_additional_earnings_with_full_tax:
            self.total_tax_amount = calculate_tax_by_tax_slab(
                self.total_taxable_earnings, self.tax_slab, self.whitelisted_globals, eval_locals
            )
            self.full_tax_on_additional_earnings = self.total_tax_amount - self.total_structured_tax_amount

        current_tax_amount = self.current_structured_tax_amount + self.full_tax_on_additional_earnings
        if flt(current_tax_amount) < 0:
            current_tax_amount = 0

        self._component_based_variable_tax[tax_component].update(
            {
                "previous_total_paid_taxes": self.previous_total_paid_taxes,
                "total_structured_tax_amount": self.total_structured_tax_amount,
                "current_structured_tax_amount": self.current_structured_tax_amount,
                "full_tax_on_additional_earnings": self.full_tax_on_additional_earnings,
                "current_tax_amount": current_tax_amount,
            }
        )

        # Minus the amount from monthly tax that is already paid to tax authorities
        extra_current_tax_amount = 0
        if frappe.db.exists("DocType", "Paid Income Tax Monthly"):
            extra_current_tax_amount = flt(frappe.db.sql("""
                select 
                    sum(pitm.amount) 
                from 
                    `tabPaid Income Tax Monthly` pitm
                where
                    pitm.docstatus=1
                    and %(from_date)s>=pitm.period_from
                    and  %(to_date)s<=pitm.period_to
                    and %(from_date)s<=pitm.payroll_date
                    and  %(to_date)s>=pitm.payroll_date
                    and pitm.employee=%(employee)s
            """,{
                "employee": self.employee,
                "from_date": self.start_date,
                "to_date": self.end_date
            })[0][0])

        return current_tax_amount - extra_current_tax_amount
    
    def calculate_net_pay(self):
        if self.salary_structure:
            self.calculate_component_amounts("earnings")

		# get remaining numbers of sub-period (period for which one salary is processed)
        if self.payroll_period:
            self.remaining_sub_periods = get_period_factor(
				self.employee,
				self.start_date,
				self.end_date,
				self.payroll_frequency,
				self.payroll_period,
				joining_date=self.joining_date,
				relieving_date=self.relieving_date,
			)[1]
        
        self.gross_pay = self.get_component_totals("earnings", depends_on_payment_days=1)
        self.base_gross_pay = flt(
			flt(self.gross_pay) * flt(self.exchange_rate), self.precision("base_gross_pay")
		)
        if self.salary_structure:
            self.calculate_component_amounts("deductions")
        
        set_loan_repayment(self)
        self.set_precision_for_component_amounts()
        self.set_net_pay()
        self.compute_income_tax_breakup()
		