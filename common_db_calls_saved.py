import db_interface
from collections import defaultdict



employee_list = db_interface.employee_list()
store_employees_map = defaultdict(list)

for employee in employee_list:
	store_employees_map[employee[3]].append(employee[0])

store_name_to_id = {'Ulsoor Road': 'store1', 'Indira Nagar': 'store2'}