import frappe
from frappe.desk.form.load import getdoc , getdoctype
from frappe.utils import today
from sowaan_hr.sowaan_hr.api.workflow import apply_actions
from sowaan_hr.sowaan_hr.api.employee import get_allowed_employees, get_current_emp



@frappe.whitelist()
def get_loans(employee, page):
    try:
        pageSize = 15
        page = int(page)

        if(page <= 0):
            return "Page should be greater or equal of 1"

        filters = {}

        allowed_employees = get_allowed_employees()
        
        if employee:
            if (len(allowed_employees) > 0 and employee in allowed_employees) or len(allowed_employees) == 0:
                filters["applicant"] = employee
            else:
                filters["applicant"] = get_current_emp()
        elif len(allowed_employees) > 0:
            filters["applicant"] = ["in", allowed_employees]
        
        loans = frappe.db.get_list(
            "Loan Application",
            filters=filters,
            fields=['*'],
            order_by="modified DESC",
            start=(page-1)*pageSize,
            page_length=pageSize
        )
        
        return loans
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


@frappe.whitelist()
def get_loan_types():
    data=frappe.db.get_list("Loan Security Type", filters={'disabled': 0}, fields=['*'])
    return data


@frappe.whitelist()
def create_loan(employee, loanType, loanAmount, isTermLoan, repaymentMethod, repaymentAmount, repaymentMonths, loanApprover, description):
    try:
        # Check if 'repaymentMethod' is 'Repay Fixed Amount per Period' and 'repaymentAmount' is not empty
        if isTermLoan == '1' and repaymentMethod == "Repay Fixed Amount per Period" and not repaymentAmount:
            raise Exception("Repayment Amount should not be empty")
        
        # Define the loan data dictionary with common fields
        loan_data = {
            "doctype": "Loan Application",
            "employee": employee,
            "applicant": employee,
            "loan_type": loanType,
            "loan_amount": float(loanAmount),
            "is_term_loan": True if isTermLoan == '1' else False,
            "loan_approver": loanApprover,
            "description": description
        }

        # Add conditional fields based on 'isTermLoan' and 'repaymentMethod'
        if isTermLoan == '1':
            if repaymentMethod == "Repay Fixed Amount per Period":
                loan_data["repayment_amount"] = float(repaymentAmount)
                loan_data["repayment_method"] = repaymentMethod
            else:
                loan_data["repayment_method"] = repaymentMethod
                loan_data["repayment_periods"] = int(repaymentMonths)

        # Create the loan document
        new_loan = frappe.get_doc(loan_data)
        
        new_loan.insert()
        # Retrieve the name of the newly created loan application
        name = get_first_doc_name("Loan Application", orderBy="modified DESC")


        return name
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)

        
@frappe.whitelist()
def update_loan(name,employee,loanType,loanAmount,isTermLoan,repaymentMethod,repaymentAmount,repaymentMonths,loanApprover, description):
    try:
        doc = frappe.get_doc('Loan Application', name)
        doc.applicant = employee
        doc.loan_type = loanType
        doc.loan_amount = float(loanAmount)
        doc.loan_approver = loanApprover
        doc.description = description

        if isTermLoan == 1:
            doc.repayment_method = repaymentMethod
            if repaymentMethod == "Repay Fixed Amount per Period":
                doc.repayment_amount = float(repaymentAmount)
            else:
                doc.repayment_periods = int(repaymentMonths)

        doc.save()

        data = get_first_doc_name("Loan Application", orderBy="modified DESC")

        return data

    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)

@frappe.whitelist()
def loan_up_sbm(name, action):

    # check_state = frappe.db.get_list('Workflow State',filters={'name': action}, fields=['*'])

    # if(len(check_state) != 0):
        # frappe.db.set_value('Loan Application',name, {
        # 'status':action,
        # })
    try:
        frappe.db.sql(f"""
                    UPDATE `tabLeave Application` 
                    SET status='{action}'
                    WHERE name='{name}';
                """)
        frappe.db.commit()
        data = frappe.db.get_doc("Loan Application",name)
        val = apply_actions(frappe.parse_json(data),action)
        frappe.db.set_value('Loan Application',name, {
        'workflow_state' :val.workflow_state,
        })
        
        return val
    except Exception as e:
        frappe.local.response['http_status_code'] = 500
        frappe.local.response['error_message'] = str(e)


def get_first_doc_name(doctype, orderBy):
    doc = frappe.db.get_all(doctype, order_by=orderBy)
    if doc:
        return doc[0]
    else:
        return None