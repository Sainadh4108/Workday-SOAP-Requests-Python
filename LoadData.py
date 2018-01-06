import sys

xmlData1='''
            <ns0:ID ns0:type="File_ID"></ns0:ID>
   '''

xmlData2='''
            <!--Optional:-->
            <ns0:ID>WORKER_DOCUMENT-0-33424234</ns0:ID>
            <ns0:Filename>abcd.docx</ns0:Filename>
            <ns0:Comment>Document Comment</ns0:Comment>
 
            <!--Optional:-->
            <ns0:File>djaflkjaljfd</ns0:File>
            <ns0:Document_Category_Reference ns0:Descriptor="?">
               <!--Zero or more repetitions:-->
               <ns0:ID ns0:type="WID">2342342344663363</ns0:ID>
            </ns0:Document_Category_Reference>

            <ns0:Worker_Reference ns0:Descriptor="?">
               <!--Zero or more repetitions:-->
               <ns0:ID ns0:type="Employee_ID">3243242</ns0:ID>
            </ns0:Worker_Reference>
            <ns0:Content_Type>application/vnd.openxmlformats-officedocument.wordprocessingml.document</ns0:Content_Type>
'''
# Login to workday
from Login import * 
open("forLoad.xml","w")
result = {}
def iterateEnvelope():
    try:
        global result
        result= client.service.Put_Worker_Document(Raw(xmlData1),Raw(xmlData2))
        
    except WebFault as e:
        print(e)
        sys.exit()
     


iterateEnvelope()

print "Done"
