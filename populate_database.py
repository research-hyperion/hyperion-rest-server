import sqlite3
import csv

database_version = 1

connection = sqlite3.connect('hyperion.db')

cursor = connection.cursor()

'''
with open('drug_names.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        sql_insert_query = "insert into drugs (drugname) values (\'{0}\')".format(row['DrugName'])
        cursor.execute(sql_insert_query)
    connection.commit()
'''
# update database version

sql_update_version_query = "update dbversion set version={0}".format(str(database_version))
cursor.execute(sql_update_version_query)
connection.commit()
connection.close()


