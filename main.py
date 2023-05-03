import logging
import os

import functions
import functions.logger

import csv

import requests

import planon

# *********************************************************************
# LOGGING - set of log messages
# *********************************************************************

log = logging.getLogger(__name__)

# *********************************************************************
# SETUP
# *********************************************************************

API_KEY = os.environ['API_KEY']
BASE_URL = os.environ['BASE_URL']

PEOPLE_URL = BASE_URL + "/people" 
LOGIN_URL = BASE_URL + "/jwt"

log.debug(f"{BASE_URL=}")

headers = {
         'Authorization':API_KEY
      }

scopes= "urn:dartmouth:people:read.highlysensitive"

planon.PlanonResource.set_site(site=os.environ['PLN_API_URL'])
planon.PlanonResource.set_header(jwt=os.environ['PLN_API_KEY'])

PLN_API_URL = os.environ['PLN_API_URL']
log.debug(f"{PLN_API_URL}")
PLN_API_KEY = os.environ['PLN_API_KEY']
log.debug(f"{PLN_API_KEY}")



# ***********************************************************************
# MAIN - calls the get_jwt() , get_dart_people() , get_planon_people
# ***********************************************************************
log.debug("acquiring dartapi JWT...")

# ***********************************************************************
# SOURCE DARTMOUTH PEOPLE 
# ***********************************************************************
dartapi_jwt = functions.get_jwt(url=LOGIN_URL,key=API_KEY,scopes=scopes,session=requests.Session())
dart_people = functions.get_people(jwt=dartapi_jwt,url=PEOPLE_URL,session=requests.Session())

# ***********************************************************************
# SOURCE PLANON PEOPLE 
# ***********************************************************************
log.debug("Getting planon people")
pln_people = planon.Person.find()
total_pln_records = str(len(pln_people))

# ********************** COMPARE PEOPLE ***************************************#

# Filter planon people by NetID 
# dict comprehension to find dart person with netid as key
# for planon person in planon people get dartmouth person
# compare dartmouth person to planon person
# loops breaks when it is done looping through all the filtered planon people
# use continue at end of for loop - so it does not force stop , if exception occurs
# loop stops when match = filtered_pln_people

# *************************************************************************** #

len_pln=int(len(pln_people))
len_dart=int(len(dart_people))
diff = len_dart-len_pln
total_dart_records= len(dart_people)
log.info(f"Total number of dart records : {total_dart_records}")
log.info(f"Total number of planon records : {total_pln_records}")
print(f"Difference in numbers of records between Planon and Dartmouth system : {diff}")


pln_filter_by_netid = {
    "filter": {
    'FreeString7': {'exists' : True},
       'FreeString7': {'eq' : 'f0035x5'},
        # 'FirstName': {'eq' : 'Harini'}
        #   'EmploymenttypeRef' : {'exists': True}
        }
}

filtered_pln_people =planon.Person.find(pln_filter_by_netid)
# log.info(f"filtered_pln_people : {str(filtered_pln_people)}")
total_pln_records_filtered = str(len(filtered_pln_people))
log.info(f"Total number of planon_records_filtered :  {total_pln_records_filtered}")

filtered_dart_people ={ person['netid']: person for person in dart_people} #type:ignore
# log.info(f"Dart_records_filtered :  {str(filtered_dart_people['d36546b'])}")
log.info(f"Total number of dart_records_filtered : {str(len(filtered_dart_people))}")


match=0
unmatch=0
key=0
log.info(f"Loop through planon records for {str(len(filtered_pln_people))} loops and find the corresponding dart record")

# https://www.geeksforgeeks.org/working-csv-files-python/
filename = "output/unmatched.csv"
                    
column_headers = ['DC_NetID','Planon_NetID','DC_email','Planon_email','DC_FullName','Planon_FullName','DC_FirstName','Planon_FirstName','DC_LastName','Planon_LastName','DC_DartAcctStatus','Planon_DartAcctStatus','Planon_IsArchived']

with open(filename, 'w') as csvfile:    
    csvwriter = csv.writer(csvfile)    
    csvwriter.writerow(column_headers)

    for pln_person in filtered_pln_people:
        
        if pln_person:
            netid = pln_person.NetID
            try:
                dc_person = filtered_dart_people[netid]
                if dc_person == None :
                    raise IndexError

                if (pln_person.FirstName == dc_person['first_name']):
                    match += 1
                    # log.info(f"Records match for {netid} in loop number {match}")
                elif(pln_person.FirstName != dc_person['first_name']):
                    unmatch+=1
                    log.info(f"Records unmatch for: {netid } in loop number {unmatch} ")                
                    
                    row_data = [dc_person['netid'], pln_person.NetID, dc_person['email'],pln_person.Email, dc_person['name'],pln_person.FullName, dc_person['first_name'],pln_person.FirstName,dc_person['last_name'], pln_person.LastName,dc_person['account_status'],pln_person.DartmouthAccountStatus,pln_person.IsArchived ]
                    # dc_person['account_status'],pln_person.DartmouthAccountStatus
                    with open(filename, 'a') as csvfile:                   
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(row_data)

                if match == len(filtered_pln_people):
                    log.info(f"Stopping loop on count number : {match}")
                    break   

            except KeyError as ex:            
                exception = ex
                key=key+1            
                # log.debug(f"Record with key error : {email}")
            
        continue
                

    if match == len(filtered_pln_people):
        log.debug(f"All {len(filtered_pln_people)} records match ")
    else:
        log.debug(f"Number of records that do not match : {unmatch}")
        
    log.debug(f"Number of records with keyerror : {key} ")





pln_filter_by_netid = {
    "filter": {
    'Code': {'eq' : '2911'},
        }
}

filtered_pln_people =planon.LeaseContract.find(pln_filter_by_netid)
