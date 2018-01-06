# -*- coding: utf-8 -*-

####################################################################
### Tenant Credentials
from credentials import username,password
wsdl_url = '?wsdl'
print "Warning : ", wsdl_url[wsdl_url.index("/service/")+9: wsdl_url.index("/Staffing")]
proxy = ''
shared_folder_name = ""
batch_size = ""

get_raw = True
index_no = 0


####################################################################
# includes suds import & following functions
# def workday_client_login :
from load_functions import *
from data_variables import worker_file_IDs


client_custom = workday_client_login(wsdl_url = wsdl_url,username = username,password = password,proxy = proxy)

if(client_custom != None):
	print("Starting Download!")
	try:
		if(get_raw == True):
			get_raw_file_data_iterator(client_custom,worker_file_IDs,index_no,shared_folder_name)
		else:
			get_base_64_data_iterator(client_custom,worker_file_IDs,index_no,batch_size)
	except Exception as e:
		print(e)

	print("Task Complete")
else:
	print("Connection Error")