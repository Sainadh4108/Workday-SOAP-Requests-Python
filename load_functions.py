# -*- coding: utf-8 -*-
#!/usr/bin/python

# Tenant Credentials
import sys
import os
import suds
from suds import client
from suds.wsse import Security, UsernameToken
from suds.sax.text import Raw
from suds.sudsobject import asdict
from suds import WebFault
import urllib2
import re
import base64
from suds.plugin import MessagePlugin
import cgi
from time import gmtime, strftime
from collections import defaultdict
import ast

## Uncomment for full debug output:
#import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
##logging.getLogger('suds.transport').setLevel(logging.DEBUG) # MUST BE THIS?
# logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
# logging.getLogger('suds.resolver').setLevel(logging.DEBUG)
#logging.getLogger('suds.xsd.query').setLevel(logging.DEBUG)
# logging.getLogger('suds.xsd.basic').setLevel(logging.DEBUG)
# logging.getLogger('suds.binding.marshaller').setLevel(logging.DEBUG)


## Log in to workday
def workday_client_login(*args,**kwargs):
    wsdl_url = kwargs['wsdl_url']
    username = kwargs['username']
    password = kwargs['password']
    proxy = kwargs['proxy']
    client_return = None
    print "Connecting to wsdl_url ..."
    try:
        if(proxy.strip() !=""):
            client_return = client.Client(wsdl_url,proxy={'https':proxy})
        else:
            client_return = client.Client(wsdl_url)
        security = Security()
        token = UsernameToken(username, password)
        security.tokens.append(token)
        client_return.set_options(wsse=security)
    except Exception as e:
             print(e)
             return client_return

    print("Logged In to: "+wsdl_url)
    return client_return




def get_raw_document(xmlRequest,client_custom,shared_folder_name,file_name_data,file_data_input):

    result = {}
    shared_folder_name = shared_folder_name
    xmlRequest = xmlRequest
    file_name_data = file_name_data
    file_data_input = file_data_input

    xml = Raw(xmlRequest)



    try:
        result= client_custom.service.Get_Worker_Documents(xml)

    except WebFault as e:
        print(str(e))
        if(str(e).index("is not a valid ID")>=0):
                print "File ID doesn't exist"
                return ("none",str(file_data_input))

        else: 
            return ("Error",file_data_input[0])
            print "Here"
            sys.exit()


    file_name = ""
    file_data = ""

    # Name the file
    if( result[2][0][0][1].__contains__("Filename")):
        file_name = result[2][0][0][1]["Filename"].encode("utf8")

    extension = ""
    index_of_file_extension = file_name.rfind(".")
    if(index_of_file_extension != -1):
        extension = file_name[index_of_file_extension:]

    
    i=0
    file_name = file_data_input[1]+"."+file_data_input[2]+"."+file_data_input[3]+"."+file_data_input[4]
    final_file_name = file_name

    while(True):
        if file_name_data.has_key((final_file_name+extension).lower()) == True:
            i=i+1
            final_file_name = file_name+"_"+str(i)
        else:
            break

    final_file_name = final_file_name + extension

    # Get File 
    if( result[2][0][0][1].__contains__("File")):
        file_data =result[2][0][0][1]["File"]

    # Get the folder path for the file
    my_path = shared_folder_name+final_file_name

    with open(my_path,"wb") as f:
        f.write(base64.b64decode(file_data))

    file_name_data[final_file_name.lower()] = 0

    print("Downloaded - " + final_file_name)
    

    return ("good",final_file_name)

## Log out of workday
def get_document(xmlRequest,client_custom):
    result = {}
    xmlRequest = xmlRequest
    xml = Raw(xmlRequest)
    try:
        result= client_custom.service.Get_Worker_Documents(xml)
    except WebFault as e:
        print(str(e))
        return ("error",result[2][0][0][1]["ID"].encode("utf8"),'')
        
     
    dataList = ["","","","","","","","",""]

    if(result[2][0][0][1].__contains__("ID")):
        dataList[0] = result[2][0][0][1]["ID"].encode("utf8")
    
    if(result[2][0][0][1].__contains__("Filename")):
        dataList[1] = result[2][0][0][1]["Filename"].encode("utf8")

    if(result[2][0][0][1].__contains__("Comment")):
        dataList[2] = cgi.escape(result[2][0][0][1]["Comment"].encode("utf8"))

    if(result[2][0][0][1].__contains__("File")):
        dataList[3] = result[2][0][0][1]["File"].encode("utf8")

    if(result[2][0][0][1].__contains__('Document_Category_Reference')):
        dataList[4] = result[2][0][0][1]['Document_Category_Reference'][1][1][1].encode("utf8")
        dataList[5] = result[2][0][0][1]['Document_Category_Reference'][1][1][0].encode("utf8")
        
    dataList[6] = result[2][0][0][1]['Worker_Reference'][1][1][1].encode("utf8")    
    dataList[7] = result[2][0][0][1]['Worker_Reference'][1][1][0].encode("utf8")
    
    if(result[2][0][0][1].__contains__("Content_Type")):
        dataList[8] = result[2][0][0][1]["Content_Type"].encode("utf8")

    xmlOutputPart1=""

    xmlOutputPart2='''
            <ns0:Filename>{fileName}</ns0:Filename>
            <ns0:Comment>{comment}</ns0:Comment>
            <ns0:File>{file}</ns0:File>
            <ns0:Document_Category_Reference ns0:Descriptor="?">
                <ns0:ID ns0:type="{doc_id_type}">{doc_id}</ns0:ID>
            </ns0:Document_Category_Reference>
            <ns0:Worker_Reference ns0:Descriptor="?">
               <ns0:ID ns0:type="{worker_id_type}">{worker_id}</ns0:ID>
            </ns0:Worker_Reference>
            <ns0:Content_Type>{content_type}</ns0:Content_Type>
    '''.format(fileName=dataList[1],comment=dataList[2],file=dataList[3],doc_id_type=dataList[4],doc_id=dataList[5],worker_id_type=dataList[6],worker_id=dataList[7],content_type=dataList[8])

    return ("good",dataList[0],xmlOutputPart2)


# Get_Docs data file id iterator
def get_base_64_data_iterator(client_custom,worker_file_IDs,index_no,batch_size):
    client_custom = client_custom
    output_data = []
    worker_file_IDs = worker_file_IDs
    index_no = index_no
    batch_size = batch_size

    preXML = '''<ns0:Worker_Document_Reference ns0:Descriptor="?">
                    <ns0:ID ns0:type="File_ID">'''
                           
    postXML    = '''</ns0:ID>
              </ns0:Worker_Document_Reference>'''

    xmlRequest = ""


    get_data_logs = open("Logs/GET_DOCS_LOG","a")

    start_index = index_no

    end_index = len(worker_file_IDs)

    ##  Iterative download worker documents
    for doc_no in range(start_index,end_index):
        print(str(doc_no) + "  -  "+worker_file_IDs[doc_no])
        get_data_logs.write(str(doc_no) + " - " + worker_file_IDs[doc_no]+" - "+ strftime("%H:%M:%S", gmtime()) +"\n")
        xmlRequest=preXML+worker_file_IDs[doc_no]+ postXML

        output_data = get_document(xmlRequest,client_custom)

        if(output_data[0] == "good"):
            if(doc_no*1.0/batch_size-(doc_no/batch_size) == 0):
                with open("Document_Variables/doc_data_"+str(doc_no/batch_size)+".py","ab") as f:
                    f.write('''soap_xml_data=['''+'["'+output_data[1]+'" , """'+output_data[2]+'"""],\n')
                    get_data_logs.write("Downloaded!\n")
            else:
                with open("Document_Variables/doc_data_"+str(doc_no/batch_size)+".py","ab") as f:
                    f.write('["'+output_data[1]+'" , """'+output_data[2]+'"""],\n')
                    get_data_logs.write("Downloaded!\n")
            print "Downloaded"
        else:
            print("Error")
            sys.exit()

    # Close variables
    for i in range(0,(end_index/batch_size)+1):
        with open("Document_Variables/doc_data_"+str(i)+".py","ab") as f:
            f.write(']')


# Get_Docs data file id iterator
def get_raw_file_data_iterator(client_custom,worker_file_IDs,index_no,shared_folder_name):
    client_custom = client_custom
    output_data = []
    worker_file_IDs = worker_file_IDs
    index_no = index_no
    
    

    file_name_data = {}
    grouped_data = defaultdict(list)

    if(index_no == 0):
        with open("Logs/File_name_variable", "w") as b:
            b.write("{'text':0}")

    with open("Logs/File_name_variable", "r") as b:
        file_name_data = ast.literal_eval(b.read())

    preXML = '''<ns0:Worker_Document_Reference ns0:Descriptor="?">
                    <ns0:ID ns0:type="File_ID">'''
                           
    postXML    = '''</ns0:ID>
              </ns0:Worker_Document_Reference>'''

    xmlRequest = ""

    start_index = index_no

    end_index = len(worker_file_IDs)

    ##  Iterative download worker documents
    for doc_no in range(start_index,end_index):
        print(str(doc_no) + "  -  "+worker_file_IDs[doc_no][0])

        with open("Logs/GET_DOCS_LOG","a") as f:
            f.write(str(doc_no) + " - " + worker_file_IDs[doc_no][0]+" - "+ strftime("%H:%M:%S", gmtime()) +"\n")

        xmlRequest=preXML+worker_file_IDs[doc_no][0]+ postXML


        output_data = get_raw_document(xmlRequest,client_custom,shared_folder_name,file_name_data,worker_file_IDs[doc_no])

        if(output_data[0] == "good"):
            with open("Logs/GET_DOCS_LOG","a") as f:
                f.write("Downloaded - "+output_data[1]+"\n")

            with open("Logs/file_name_variable", "w") as b:
                b.write(str(file_name_data))
        else:
            if(output_data[0] == "none"):
                with open("Logs/GET_DOCS_LOG","a") as f:
                    f.write("File_ID doesn't Exist\n")
                with open("Logs/Non_Existant_Files",'a') as f:
                    f.write(output_data[1]+"\n")
            else:
                print "Here1"
                sys.exit()


def put_document_attachment(client_custom,xml_data):
    #Load Worker Documents
    result = None
    try:

        result = client_custom.service.Put_Worker_Document("",Raw(xml_data))
    except WebFault as e:
        print(e)
        sys.exit()
    return "Successful"


def put_document_iterator(client_custom,doc_data,index_no,doc_name):

    put_data_logs = open("Logs/PUT_DOCS_LOG_"+doc_name,"a")
    start_index = index_no
    end_index = len(doc_data)
    client_custom = client_custom

    ##  Iterative download worker documents
    for doc_no in range(start_index,end_index):

        print(str(doc_no) + " - "+doc_data[doc_no][0])
        put_data_logs.write(str(doc_no) + " - " + doc_data[doc_no][0]+" - "+ strftime("%H:%M:%S", gmtime()) +"\n")

        output_data = put_document_attachment(client_custom,doc_data[doc_no][1])

        if(output_data == "Successful"):
            put_data_logs.write("Uploaded!\n")
            print "Uploaded"
        else:
            print("Error")
            sys.exit()
