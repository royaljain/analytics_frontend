import psycopg2
import pandas.io.sql as psql
import config


conn = psycopg2.connect(database=config.DATABASE, user = config.USER,
password = config.PASSWORD, host = config.HOST)

store_id = "'store1'"
query = "SELECT * FROM employee_register where StoreId={};".format(store_id)
dataframe = psql.read_sql(query, conn)
print(dataframe.dtypes)