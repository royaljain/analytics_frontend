import psycopg2
import pandas.io.sql as psql
import config


conn = psycopg2.connect(database=config.DATABASE, user = config.USER,
password = config.PASSWORD, host = config.HOST)

employee_id = "1234"
str_employee_id = "'{}'".format(employee_id)
query = "SELECT employee_register.employeeid, name, manager, islate, isovertime, hoursworked, entrydate, timein, timeout FROM employee_register INNER JOIN employee_attributes ON employee_register.employeeid=employee_attributes.employeeid where employee_attributes.employeeid={};".format(str_employee_id)
dataframe = psql.read_sql(query, conn)

print(dataframe.dtypes)