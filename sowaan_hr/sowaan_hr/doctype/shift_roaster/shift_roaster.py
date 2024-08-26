# Copyright (c) 2024, Sowaan and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document


class ShiftRoaster(Document):

    def before_save(self):
        # To Date must be greater than frequency respective date
        if self.is_replicated:
            if self.frequency == 'Weekly':
                t_date = frappe.utils.add_days(self.from_date, 7)
            elif self.frequency == 'Bi Weekly':
                t_date = frappe.utils.add_days(self.from_date, 14)
            elif self.frequency == 'Monthly':
                t_date = frappe.utils.add_days(self.from_date, 28)

            if self.to_date < t_date:
                frappe.throw("To Date must be after Frequency respective date.")



    def before_submit(self) :

        freq_days = 0
        if self.frequency == 'Weekly':
            freq_days = 7
        elif self.frequency == 'Bi Weekly':
            freq_days = 14
        elif self.frequency == 'Monthly':
            freq_days = 28

        employees = []
        shifts = []
        from_dates = []
        to_dates = []
        shifttable = []

        if self.is_replicated :
            days_diff = frappe.utils.date_diff(self.to_date , self.from_date) + 1
            div = int( days_diff / freq_days )
            mod = days_diff % freq_days

            for i in range(days_diff):
                j = i % len(self.shifts)
                shift_row = self.shifts[j].as_dict().copy()
                shift_row['date'] = frappe.utils.add_days(self.from_date, i)
                shifttable.append(shift_row)

        else :
            for i in range(freq_days):
                shift_row = self.shifts[i].as_dict().copy()
                shifttable.append(shift_row)


        shifts, from_dates, to_dates = creating_shifts(shifttable, self.from_date, self.is_replicated, self.to_date, freq_days)

        self.shift_assignment = []
        for i in range(0, len(shifts)) :
            self.append('shift_assignment',{
                'shift_type' : shifts[i] ,
                'from_date' : from_dates[i] ,
                'to_date' : to_dates[i] ,
            })

        for row in self.employees :
            employees.append(row.employee)

        submitting_shifts(employees, shifts , from_dates, to_dates, self.name)



    def before_cancel(self) :

        self.shift_assignment = []

        sh_ass_list = frappe.get_list("Shift Assignment",
                        filters = {
                            'custom_shift_roaster' : self.name ,
                            'docstatus' : 1 ,
                        })
        
        if sh_ass_list :
            for sh_ass in sh_ass_list :
                sh_ass_doc = frappe.get_doc('Shift Assignment',sh_ass.name)
                sh_ass_doc.cancel()
                
            for sh_ass in sh_ass_list :
                sh_ass_doc = frappe.get_doc('Shift Assignment',sh_ass.name)    
                sh_ass_doc.delete()


    def on_trash(self) :
        self.shift_assignment = []

        sh_ass_list = frappe.get_list("Shift Assignment",
                        filters = {
                            'custom_shift_roaster' : self.name ,
                            'docstatus' : 2 ,
                        })
                
        for sh_ass in sh_ass_list :
            sh_ass_doc = frappe.get_doc('Shift Assignment',sh_ass.name)    
            sh_ass_doc.delete()







# @frappe.whitelist()
# def creating_shifts(shifttable , from_date, is_replicated, to_date, freq_days) :
    
#     shifts = []
#     from_dates = []
#     to_dates = []


#     if shifttable:
#         current_shift = None
#         current_from_date = None
#         current_to_date = None

#         for row in shifttable:
#             if row.shift_type:
#                 if current_shift is None:
#                     current_shift = row.shift_type
#                     current_from_date = row.date
#                     current_to_date = row.date
#                 elif row.shift_type == current_shift:
#                     current_to_date = row.date
#                 else:
#                     if current_shift:
#                         shifts.append(current_shift)
#                         from_dates.append(current_from_date)
#                         to_dates.append(current_to_date)
#                     current_shift = row.shift_type
#                     current_from_date = row.date
#                     current_to_date = row.date
#             else:
#                 if current_shift:
#                     next_shift = None
#                     next_index = shifttable.index(row) + 1
#                     if next_index < len(shifttable):
#                         next_shift = shifttable[next_index].shift_type
#                     if next_shift != current_shift:
#                         shifts.append(current_shift)
#                         from_dates.append(current_from_date)
#                         to_dates.append(current_to_date)
#                         current_shift = None
#                         current_from_date = None
#                         current_to_date = None

#         if current_shift:
#             shifts.append(current_shift)
#             from_dates.append(current_from_date)
#             to_dates.append(current_to_date)
            
    

#         return shifts , from_dates , to_dates



@frappe.whitelist()
def creating_shifts(shifttable , from_date, is_replicated, to_date, freq_days):
    shifts = []
    from_dates = []
    to_dates = []

    if shifttable:
        current_shift = None
        current_from_date = None

        for entry in shifttable:
            shift_type = entry.get('shift_type')
            date = entry.get('date')

            if shift_type:
                if current_shift == shift_type:
                    current_to_date = date
                else:
                    if current_shift is not None:
                        shifts.append(current_shift)
                        from_dates.append(current_from_date)
                        to_dates.append(current_to_date)
                    
                    current_shift = shift_type
                    current_from_date = date
                    current_to_date = date
            else:
                if current_shift is not None:
                    shifts.append(current_shift)
                    from_dates.append(current_from_date)
                    to_dates.append(current_to_date)
                    current_shift = None
                    current_from_date = None
                    current_to_date = None

        if current_shift is not None:
            shifts.append(current_shift)
            from_dates.append(current_from_date)
            to_dates.append(current_to_date)

    return shifts, from_dates, to_dates



@frappe.whitelist()
def submitting_shifts(employees, shifts , from_dates, to_dates, name) :

    for emp in employees :
        for i in range(0, len(shifts)) :
            sh_ass_doc = frappe.new_doc('Shift Assignment')
            sh_ass_doc.employee = emp
            sh_ass_doc.shift_type = shifts[i]
            sh_ass_doc.start_date = from_dates[i]
            sh_ass_doc.end_date = to_dates[i]
            sh_ass_doc.custom_shift_roaster = name
            sh_ass_doc.save()
            sh_ass_doc.submit()