# streamlining deployment with git broker
we have taken things to the next level by combining containerized deployment with gitflow, resulting in a completely automated build and deployment process. interested in learning more? check out our blog in wf 3.0.
## what is ssr?
ssr (server-side rendering) is a technique of rendering web pages on the server before sending them to the client's browser. in ssr, the server sends a fully rendered page to the client instead of sending an empty page with javascript that needs to be executed before rendering. to know more, check this [link](#).
## how is spaship doing it?
spaship uses containerized deployment technique for supporting ssr applications.
## how is this different from the existing process?
before ssr support, spaship mainly dealt with static resource deployment, which is the usual way to deploy bundled html resources in shared apache servers. and using the spaship cli, those bundles used to get loaded to the target environment. since ssr applications are different and require specialized runtime, in this containerized deployment approach, one will be able to deploy their front-end container and corresponding configuration (which might require during application startup, for example, environment variables) from the spaship manager or using the cli; this enables the possibility of deployment of all kinds of front-end applications (and lightweight backend node applications) through spaship service.
### important cases:
1. it requires a pre-existing container image to deploy in the target environment, although using spaship cli once can create an integration flow for build and deployment.
2. the context path strictly depends on the homepage attribute of the package.json file.
we've identified the above cases in our current version. these will be addressed in our next major release, where we'll provide solutions to these challenges.
### key points to consider for the containerized deployment:
- existing attributes will be there for the deployment, consists name, path, and ref.
- in the containerized deployment, we've provided three more attributes "healthcheckpath", "image (url)" and "configurations".
  - **image (url):** you've to provide the image url for your application. spaship will fetch the image from your registry and start the deployment. your image should be present in the registry (quay, podman, docker etc), else it can deploy your image. it can be configured from the spaship manager and cli. this is the mandatory field for the containerized deployment.
  - **health check path:** it determines the health status of your application. by default, the value of the health check path is the context path, but can also configure it as per your expectations. it can be configured from the spaship manager.
  - **configuration:** you can provide your environment variables in the configurations as a key value pair. it will add value to your deployment. this is not mandatory for every application, and it can be configured from the spaship manager.
to access the application deployment from the spaship manager, the property owner has to explicitly provide permission for the application creation to the user, or for the cli if using the api key, we can perform the deployment. as of now, spaship runs the containerized application in the default 3000 port; we'll provide the flexibility of changing the port it in the upcoming release. we deploy the application currently (if hosted in prod cluster) in two different clusters for the high availability. you can easily get the pod logs from the spaship manager after the deployments, and also receive an application available event in the activity stream section.
### limitations:
from this workflow 2.0 feature, you can set the applicationpath, healthcheckpath (for the liveness/readiness check), configuration value update from the spaship manager, but you cannot update the other values from the spaship manager like cpu, replicas, etc. if you have any specific requirements, then you can reach out to the spaship team.
### system context diagram for the containerized deployment:
it'll give you the containerization scope that fits in the existing architecture.
![ssr architecture](./images/ss1.jpeg)
### containerized deployment design details:
here you'll find the complete design details related to containerized deployment.
### process of using containerized deployment from the spaship manager:
#### step 1: provide the permission for application creation from the spaship
![step 1](./images/ssr_step1.png)
#### step 2: click on the add new app to create the containerized deployment 
![step 2](./images/ssr_step2.png)
#### step 3: provide the details for the containerized deployment 
![step 3](./images/ssr_step3.png)
#### step 4: containerized deployments are marked as cyan, click on the spa to get the more details about the deployment
![step 4](./images/ssr_step4.png)
#### step 5: explore the containerized deployments from the spa details page
![step 5](./images/ssr_step5.png)
#### step 6: configure the spa and update the values accordingly
![step 6](./images/ssr_step6.png)
#### step 7: containerized applications can be redeployed in a single click from the spaship manager with the existing configurations 
![step 7](./images/ssr_step7.png)
#### step 8: check the deployment status from the activity stream
![step 8](./images/ssr_step8.png)
### process of using containerized deployment from the spaship cli:
#### step 1: update the spaship cli (v1.5.6 or above) from [here](#)
![step 1 cli](./images/ssr_cli_step1.png)
#### step 2: create the spaship.yaml using spaship init (existing process)
![step 2 cli](./images/ssr_cli_step2.png)
#### step 3: provide the image (url) in the deployment (instead of the archive). by providing the image (url) it will be considered as a containerized deployment. 
command : 
```bash
spaship deploy --env={env} --apikey={apikey} --image={image (url)}
```
![step 3 cli](./images/ssr_cli_step3.png)
note: from the cli if you are deploying an application for the first time, the healthcheckpath will be considered as the context path. you can configure it later from the spaship manager.