import db_interface
from collections import defaultdict

from datetime import date


employee_list = db_interface.employee_list()
store_employees_map = defaultdict(list)

for employee in employee_list:
	store_employees_map[employee[3]].append(employee[0])

store_name_to_id = {'Ulsoor Road': 'store1', 'IndiraNagar': 'store2', 'Airport': 'store3'}
list_of_leaves = [date(2019, 2, 3), date(2019, 1, 12)]
dish_id_to_name = {'dish1': 'coffee','dish2' : 'tea', 'dish3': 'milkshake', 'dish4': 'ginger tea',
 'dish5': 'pancake', 'dish6': 'pizza', 'dish7': 'samosa', 'dish8': 'burger'}

store_to_dish = { 'store1' : 'pancake', 'store2' : 'pancake', 'store3' : 'burger'}


employee_id_to_name = {}

for employee in employee_list:
	employee_id_to_name[employee[0]] = employee[1]
