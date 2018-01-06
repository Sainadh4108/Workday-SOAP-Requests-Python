# -*- coding: utf-8 -*-

####################################################################
### Tenant Credentials
from credentials import username,password
wsdl_url = '' # Enter Workday wsdl here
proxy = ''
index_no = 0

## Data to change
from Document_Variables.doc_data_0 import soap_xml_data
doc_name = "doc_data_0"

####################################################################
# includes suds import & following functions
# def workday_client_login :
from load_functions import *


client_custom = workday_client_login(wsdl_url = wsdl_url,username = username,password = password,proxy = proxy)

if(client_custom != None):

	print("Starting Upload!")
	try:
		put_document_iterator(client_custom,soap_xml_data,index_no,doc_name)
	except Exception as e:
		print(e)

	print("Task Complete")
else:
	print("Connection Error")