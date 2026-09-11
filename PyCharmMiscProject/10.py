employees_pay = [
    {"name": "Иванов", "salary": 80000},
    {"name": "Петрович", "salary": 120000},
    {"name": "Сергеев", "salary": 45000}
]
def calculate_tax(money):
    tax = money * 0.13
    return round(tax,2)
def process_payroll(pay_list):
    payroll_report = []
    for pay in pay_list:
        tax_amount = calculate_tax(pay["salary"])
        net_salary = pay["salary"] - tax_amount
        report_pay = {
            "Имя": pay["name"],
            "Налог": tax_amount,
            "На руки": net_salary
        }
        payroll_report.append(report_pay)
    return payroll_report
print(process_payroll(employees_pay))