## introduction
spaship services facilitate the building, deployment, and hosting of single page applications (spas). it is designed to deliver spas to specific openshift namespaces. the architecture of spaship comprises three main services: the manager (front-end), the orchestrator (middle layer), and the operator or deployment engine(cloud-native part).
## consequences of service failure
the impact of each spaship service going down would vary, as each has a specific role within the system. the following outlines the consequences should each service become unavailable:
### 1. manager down
users will experience limited access and functionality if the manager service goes down. specifically:
* inability to create a new property and environment.
* inability to view statistics and the dashboard.
* inability to track app deployment status.
* inability to view build and deployment logs.
* inability to view build and deployment activities.
* inability to create new keys used for cli access.
* inability to create containerized applications.
* apache ssi (chroming) sync will not function.
however, users would still be able to perform the following actions using the cli:
* redeploy existing applications.
* add new static applications.
### 2. orchestrator down
if the orchestrator service goes down, most functionalities will be unavailable as the orchestrator binds the deployment engine and the manager. despite this, users will still be able to:
* access the existing spas and environments.
### 3. deployment engine down
if the deployment engine service goes down, several aspects of deployment will be compromised:
* new deployments will not occur.
* the creation of new properties or environments will not be possible.
* build or deployment logs will not be shown.
* apache ssi (chroming) sync will not work.
* application build processes will not function.
however, users will still be able to:
* see existing applications.
* check the dashboard.
* create new api keys, though they will not be functional.
* check the activity stream.
* check existing deployment status.
## important note
in any of the above scenarios, it is important to note that all existing environments and applications deployed within those environments will remain accessible. even if any component of the spaship service goes down, the already deployed applications will not be affected, and users will still be able to access them.