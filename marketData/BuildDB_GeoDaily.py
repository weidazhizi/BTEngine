import pandas as pd
import numpy as np
import mysql.connector as msql
from mysql.connector import errorcode
from mysql.connector.constants import ClientFlag

config = {'user': 'root', 'password': 'trinnacle17'}
cnx = msql.connect(user = 'root', password = 'trinnacle17', client_flags=[ClientFlag.LOCAL_FILES])
cursor = cnx.cursor()
DB_NAME = "GeoTickersDaily15_17"
tickerList = "dailyData/allTickers.csv"

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME)
        )
    except msql.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


def fetch_data_form(tickerList):
    tickerListDF = pd.DataFrame.from_csv(tickerList)
    tickerList = list(tickerListDF.index.values)
    print(tickerList)

    TABLES = {}

    for ticker in tickerList:
        temp = ticker.split()[0].replace("/", "_")
        if(ticker.split()[0].replace("/", "_") in ["ALL", "ASC", "CALL", "FOR", "IN", "INT", "KEY", "KEYS", "LOCK", "LOOP", "MOD", "ON", "OK", "OUT", "TRUE"]):
            temp = temp + "_"
        TABLES[temp] = (
        "CREATE TABLE `" + temp + "` ("
        "  `id` int ,"
        "  `date` date ,"
        "  `open` float ,"
        "  `close` float ,"
        "  `volume` int,"
        "  `short_interest_ratio` float,"
        "  `institutional_own` float,"
        "  `short_interest_ratio_float` float,"
        "  `institutional_own_float` float,"
        "  PRIMARY KEY (`date`)"
        ") ENGINE=InnoDB")

    #print(TABLES["SPY"])
    return TABLES
    #print(portDFdict["SPY"])

try:
    cnx.database = DB_NAME
except msql.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)
#create tables and insert data
num = 0
TABLES = fetch_data_form(tickerList)
shitnames = []
for name, ddl in TABLES.items():
    try:
        #print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except msql.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
    name0 = name
    if name[-1] == "_":
        name0 = name[0:-1]
    insert_data = """LOAD DATA LOCAL INFILE 'dailyData/""" + name0 + """.csv'"""+\
    """ INTO TABLE """ + name +\
    """ FIELDS TERMINATED BY ','"""+\
    """ ENCLOSED BY '"'"""+\
    """ LINES TERMINATED BY '\n'"""+\
    """ IGNORE 1 LINES """ +\
    """ (id, date, @vopen, @vclose, @vvolume, @vshort_interest_ratio, @vinstitutional_own, @vshort_interest_ratio_float, @vinstitutional_own_float)""" +\
    """ SET"""+\
    """ open = nullif(@vopen,'NA'),"""+\
    """ close = nullif(@vclose,'NA'),"""+\
    """ volume = nullif(@vvolume,'NA'),"""+\
    """ short_interest_ratio = nullif(@vshort_interest_ratio,'NA'),"""+\
    """ institutional_own = nullif(@vinstitutional_own,'NA'),"""+\
    """ short_interest_ratio_float = nullif(@vshort_interest_ratio_float,'NA'),"""+\
    """ institutional_own_float = nullif(@vinstitutional_own_float,'NA')"""
    #print(insert_data)

    try:
        cursor.execute(insert_data)
    except:
        shitnames.append(name)
    num = num + 1
    print(num)
print(shitnames)

cnx.commit()

print(num)

cursor.close()
cnx.close()
