# spaship services overview

spaship is a cloud-native service designed to help developers to deploy front-end applications into a managed kubernetes
environment, specifically openshift. this service makes deployment and delivery of front-end applications extremely easy
by abstracting the complexity of underlying kubernetes infrastructure from the developers. in this overview, we will
take a look at the four main parts of spaship

## operator aka deployment engine

the operator is responsible for interfacing with kubernetes apis to automate the provisioning, monitoring, and
regulation of provisioned objects and applications. it is written in java, and the source code can be
found [here](https://github.com/spaship/spa-operator).
the operator is the cloud-native part of spaship, enabling developers to create and manage kubernetes objects using
simple payloads.
it requires 600m cpu and 512mb of ram to run effectively.

## orchestrator

the orchestrator interacts with the operator and sends payloads to it for processing incoming requests. it also
orchestrates the workflow and user inputs.  \
the orchestrator is written in javascript and uses the nodejs runtime, and the source code can be
found [here](https://github.com/spaship/spaship/tree/master/packages/api).  \
it requires 600m cpu and 512mb of ram to run effectively.

## manager

the manager is the front-end and user interface of spaship, where users can interact to provision applications, manage
web properties, check reports, and view application deployment statistics.  \
it is a javascript application built using the next.js framework, and the source code can be
found [here](https://github.com/spaship/spaship/tree/master/packages/manager).  \
the manager requires 300m cpu and 512mb of ram to run effectively.

## cli

the cli is written in javascript and is mostly used by ci to automate deployment tasks. it interacts with the
orchestrator to pass on payloads inputted by users. the cli is a useful tool for automating the deployment process and
can be used in conjunction with the manager to simplify the deployment of front-end applications.  \
the source code can be found [here](https://github.com/spaship/spaship/tree/master/packages/cli) and the package is
available [here](https://www.npmjs.com/package/@spaship/cli)

# diagram

following is the high-level diagram of spaship services deployed in mp+ environment
![alt_text](images/spaship_services_overview//image1.jpg "image_tooltip")

# conclusion

in conclusion, spaship is a cloud-native service that makes the deployment and delivery of front-end applications easy
and fast. its four main parts work together to abstract the complexity of underlying kubernetes infrastructure from the
developers, allowing them to focus on building great front-end applications.