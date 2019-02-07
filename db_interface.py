import psycopg2
import config
conn = psycopg2.connect(database=config.DATABASE, user = config.USER,
password = config.PASSWORD, host = config.HOST)



def get_list_of_stores():
    curr = conn.cursor()
    curr.execute("SELECT storeName from store_attributes;");
    list_of_stores = curr.fetchall()
    curr.close()

    return list_of_stores


def get_number_of_stores():
    curr = conn.cursor()
    curr.execute("SELECT COUNT(*) from store_attributes;");
    number_of_stores = curr.fetchone()[0]
    curr.close()

    return int(number_of_stores)

def get_number_of_employees():
    curr = conn.cursor()
    curr.execute("SELECT SUM(numberofemployees) from store_attributes;");
    number_of_employees = curr.fetchone()[0]
    curr.close()

    return int(number_of_employees)

def get_number_of_cities():
    curr = conn.cursor()
    curr.execute("SELECT COUNT(DISTINCT city) from store_attributes;");
    number_of_cities = curr.fetchone()[0]
    curr.close()

    return int(number_of_cities)


def employee_list():   
    curr = conn.cursor()
    curr.execute("SELECT * from employee_attributes;");
    responses = curr.fetchall()
    curr.close()

    return responses


def late_employees(start_date, end_date):
    curr = conn.cursor()
    curr.execute("SELECT DISTINCT EmployeeID from employee_register where entrydate >= %s and entrydate <= %s and islate = 1;", (start_date, end_date));
    responses = curr.fetchall()
    curr.close()

    return list(map(lambda x: x[0], responses))

def overtime_employees(start_date, end_date):
    curr = conn.cursor()
    curr.execute("SELECT DISTINCT EmployeeID from employee_register where entrydate >= %s and entrydate <= %s and isovertime = 1;", (start_date, end_date));
    responses = curr.fetchall()
    curr.close()

    return list(map(lambda x: x[0], responses))
