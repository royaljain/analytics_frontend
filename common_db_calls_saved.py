import db_interface
from collections import defaultdict

from datetime import date


employee_list = db_interface.employee_list()
store_employees_map = defaultdict(list)

for employee in employee_list:
	store_employees_map[employee[3]].append(employee[0])

store_name_to_id = {'Ulsoor Road': 'store1', 'IndiraNagar': 'store2', 'Airport': 'store3'}
list_of_leaves = [date(2019, 2, 3), date(2019, 1, 12)]


employee_id_to_name = {}

for employee in employee_list:
	employee_id_to_name[employee[0]] = employee[1]
