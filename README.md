# Powering on and off IBM cloud VSIs to a schedule
## Introduction
The real value of a cloud is the elasticity and minute by minute billing.

Unfortunately IBM cloud doesn't have built in tools to automate some of these things, and the serverless solution (functions) doesn't include all the IBM Cloud SDKs in the python runtime. 

The solution is to use Code Engine, essentially run a container on IBMs managed kubernetes cluster. You can also create a cronjobs to schedule your job when you want to start and stop your vsi images. Problem Solved.

The contained code and instructions will create a container that can start and stop VSIs based on tags. The tagging scheme is up to the implementer, it only needs to be provided at runtime, this allows for multiple jobs and tags to be used to created as sophisticated scheme as needed. 

The basic idea is to tag Virtual Server Instances (VSIs)  you want to be managed by this scheme and they will automatically be found and powered off and on to the schedule you specify. Create more tags and schedules as needed

Some inspiration was taken from [this blog](https://www.ibm.com/cloud/blog/using-ibm-cloud-code-engine-to-turn-virtual-server-instances-on/off-in-an-automated/scheduled-manner)

The instructions below are just the basics to get started. 

## Build Image
I wanted to use IBM Container Registry (why not if I am already using IBM Cloud) plus its a little easier to integrate with.

I will also note you can point your Code Engine Jobs to a git repository to build the image dynamically

Build, replace your tag with what ever registry you like
```
podman build -t podman build -t us.icr.io/autoonoff/ibm_vpc:latest .
```
And then push
```
podman push us.icr.io/autoonoff/ibm_vpc:latest
```
## Get API_KEY
Create a new api-key to use with your vsi schedule start stop cron  job

```
ibmcloud iam api-key-create auto-vsi
```

## CodeEngine Pre-Requisites  
You can either use the UI which isnt that hard or use the following IBMcloud cli instructions (this could also be automated with ansible)

Create the project and select it
```
ibmcloud ce project create -n VSI_StartAndStop
ibmcloud ce project select -n VSI_StartAndStop
```

Create the api-key secret
```
ibmcloud ce secret create --name api-key --from-literal "api_key=<Your API Key>"
```

Create the tag configmap
```
ibmcloud ce configmap create --name tag-nightly --from-literal tag=power_policy:nightly

```

Create the start amd stop action configmaps, (we select the different one for the different job definition)
```
ibmcloud ce configmap create --name action-start --from-literal action=start
ibmcloud ce configmap create --name action-stop --from-literal action=stop
```

## Create CodeEngine Jobs (from pre-built images)
### Create the Start Job
```
ibmcloud ce job create --name vsi-start --image <registry/namespace/repository:tag> --cpu .125 --memory .25G --env-from-secret api-key --env-from-configmap tag-nightly --env-from-configmap action-start
```

### Create the Stop Job
```
ibmcloud ce job create --name vsi-stop --image <registry/namespace/repository:tag> --cpu .125 --memory .25G --env-from-secret api-key --env-from-configmap tag-nightly --env-from-configmap action-stop
```

## Create CodeEngine Jobs (from source (optional))
### Create the Start Job
```
ibmcloud ce job create --name vsi-start --build-source . --wait --cpu .125 --memory .25G --env-from-secret api-key --env-from-configmap tag-nightly --env-from-configmap action-start
```

### Create the Stop Job
```
ibmcloud ce job create --name vsi-stop  -build-source . --wait --cpu .125 --memory .25G --env-from-secret api-key --env-from-configmap tag-nightly --env-from-configmap action-stop
```


## Create Cron Schedule

Turn on at 8am every weekday (adjust the schedule as needed)
```
ibmcloud ce sub cron create --name cron-vsi-start --destination vsi-start --destination-type job --schedule '0 8 * * 1-5' --time-zone "America/Phoenix"
```

Turn off at 8pm every day (adjust the schedule as needed)
```
ibmcloud ce sub cron create --name cron-vsi-start --destination vsi-stop --destination-type job --schedule '0 20 * * *' --time-zone "America/Phoenix"
```
