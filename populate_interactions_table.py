
import sqlite3
import csv


connection = sqlite3.connect('hyperion.db')

cursor = connection.cursor()


with open('ddi.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        sql_insert_query = "insert into interactions (drug1name,drugbank1id,drug2name,drugbank2id,interactioncode) values(\'{0}\',\'{1}\',\'{2}\',\'{3}\',{4})".format(row['Drug1Name'],row['Drugbank1Id'],row['Drug2Name'],row['Drugbank2Id'],int(row['InteractionCode']))
        cursor.execute(sql_insert_query)
    connection.commit()

