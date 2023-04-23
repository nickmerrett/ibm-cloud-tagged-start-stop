import os
import json
from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_cloud_sdk_core import ApiException
from ibm_platform_services import GlobalSearchV2

 
#Authenticate user on IBM Cloud to do VPC VSI commands
API_KEY = os.environ['api_key']
authenticator = IAMAuthenticator(API_KEY)
service = VpcV1(authenticator=authenticator)
global_search_service = GlobalSearchV2(authenticator=authenticator)

#Set API endpoints
service.set_service_url('https://au-syd.iaas.cloud.ibm.com/v1')
 
#Get the required action from environment variable
VSIaction = os.environ['action']
tagSearch = os.environ['tag']

# Using the search function, look for the specified tag
query = "tags:\"" + tagSearch + "\""
response = global_search_service.search(query=query,fields=['*'])
scan_result = response.get_result()['items']

#print(json.dumps(scan_result, indent=2))

instance_ids = []

#Iterate through the returned search results and look for types of instance, I have assumed what is returned is tagged correctly, but this could also be checked again here if needed
for result in scan_result:
  if result["type"] == "instance":
    instance_ids.append(result["resource_id"])
 
# Perform action on list
for instanceID in instance_ids:
    print("instance_id = " + instanceID + " | action = " + VSIaction)
    try:
        response = service.create_instance_action(
           instance_id=instanceID,
           type=VSIaction,
        )
    except ApiException as e:
        print( VSIaction + " instances failed with status code " + str(e.code) + ": " + e.message)

