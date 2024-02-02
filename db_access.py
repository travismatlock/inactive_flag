#Need a nightly script to mark the lpps in the database as inactive so that the lpp map can display accordingly.

#The criteria to mark as inactive is: not created in the last year and observation not submitted in the last two years.

import pymysql
import numpy as np
from datetime import date
from datetime import timedelta
#%%
host = 'usanpn-databases-test.c0xzlo6s7duc.us-west-2.rds.amazonaws.com'
port = 3306
user = 'travis'
password = 
database = 'usanpn2'

connection = pymysql.connect(
    host = host,
    port = port,
    user = user,
    password = password,
    database = database)
#%%
cursor = connection.cursor()
cursor.execute('SELECT cno.Name, cno.Network_ID, o.Observation_ID, MIN(o.Observation_Date), MAX(o.Observation_Date)\
               FROM usanpn2.Cached_Network_Observation cno LEFT JOIN usanpn2.Observation o ON cno.Observation_ID = o.Observation_ID\
               GROUP BY cno.Network_ID;')
min_max_obs = np.array(cursor.fetchall())
#%%
# query to find min admin's create date for each network
cursor = connection.cursor()
cursor.execute('SELECT *, MIN(p.Create_Date) AS MIN_CREATE FROM Network n\
               LEFT JOIN Network_Person np ON np.Network_ID = n.Network_ID\
               LEFT JOIN Person p ON p.Person_ID = np.Person_ID\
               LEFT JOIN App_Role_Network_Person arnp ON arnp.Network_Person_ID = np.Network_Person_ID\
               WHERE arnp.Role_ID = 1 GROUP BY n.Network_ID;')
admin_info = np.array(cursor.fetchall())
#%%
cursor = connection.cursor()
cursor.execute('SELECT * FROM usanpn2.Network_Profile')
network_profile = np.array(cursor.fetchall())
#%%
cursor = connection.cursor()
for network in network_profile:
    if network[18] == None:
        print(network[1])
        try:
            cursor.execute("UPDATE usanpn2.Network_Profile np SET np.Creation_Date = '"+
                           str(min_max_obs[np.where(min_max_obs == network[1])[1]][0,3])+
                           "' WHERE np.Network_ID = "+str(network[1])+';')
        except:
            try:
                cursor.execute("UPDATE usanpn2.Network_Profile np SET np.Creation_Date = '"+
                               str(admin_info[np.where(admin_info == network[2])[1]][0,52])+
                               "' WHERE np.Network_ID = "+str(network[1])+';')
            except:
                continue

connection.commit()   
#%%
inactive = []
no_date = []
not_in_cno = []
for network in network_profile:
    #print(network[18])
    if network[18] == None:
        no_date.append(network[1])
        continue
    try:
        if network[18] < (date.today() - timedelta(days = 365)) and\
        min_max_obs[np.where(min_max_obs == network[1])[1]][0,4].date() < (date.today() - timedelta(days = 730)):
            
            inactive.append(network[1])
            print(network[1])
    except:
        print(network[1])
        not_in_cno.append(network[1])
