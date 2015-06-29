from suds import client
from suds.wsse import Security, UsernameToken
from suds.sax.text import Raw
from suds.sudsobject import asdict
from suds import WebFault
 
'''
Given a Workday Employee_ID, returns the last name of that employee.

I had trouble finding working examples online of interacting with the Workday SOAP API
via Python - both the authentication piece and data retrieval. It turns out to be very simple,
but it took a while to come up with due to scant documentation, so posting here in case
anyone finds it helpful.

The most common SOAP lib for Python is suds, but suds has fallen out of maintenance as
SOAP has fallen out of favor over the past 5-10 years.
suds is officially replaced by suds-jurko, which is now part of Fedora:

https://bitbucket.org/jurko/suds
https://fedorahosted.org/suds/wiki/Documentation

pip install suds-jurko
'''
 
#Uncomment for full debug output:
# import logging
# logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# logging.getLogger('suds.transport').setLevel(logging.DEBUG) # MUST BE THIS?
# logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
# logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
# logging.getLogger('suds.resolver').setLevel(logging.DEBUG)
# logging.getLogger('suds.xsd.query').setLevel(logging.DEBUG)
# logging.getLogger('suds.xsd.basic').setLevel(logging.DEBUG)
# logging.getLogger('suds.binding.marshaller').setLevel(logging.DEBUG)
 
# Fully credentialed service user with access to the Human Resources API
username = 'id@tenant_name'
password = '*****'
 
# wsdl url from public web services workday
# for more information refer documentation on workday on SOAP
wsdl_url = 'https://****************************/Staffing/v24.1?wsdl'
client = client.Client(wsdl_url)
 
# Wrapping our client call in Security() like this results in submitting
# the auth request with PasswordType in headers in the format WD expects.
security = Security()
token = UsernameToken(username, password)
security.tokens.append(token)
client.set_options(wsse=security)
# The workflow is, generate an XML element containing the employee ID, then post
# that element to the Get_Workers() method in the WSDL as an argument.
# We could do this with two suds calls, having it generate the XML from the schema,
# but here I'm creating the POST XML manually and submitting it via suds's `Raw()` function.

