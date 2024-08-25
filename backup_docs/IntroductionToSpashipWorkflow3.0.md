# introduction to spaship workflow 3.0

## origin of the idea

developers often have to worry about managing their repositories, ci/cd pipelines, and hosting environments. spaship
provides a comprehensive solution to all these concerns, giving developers the freedom to focus on what really matters:
developing their applications and fulfilling business requirements. with spaship, developers can have peace of mind,
knowing that their ci/cd, and hosting are all taken care of by a single solution. so, if you're looking for a
streamlined approach to your development process, spaship may just be the answer to your concerns.

## what is spaship workflow 3.0?

in workflow 3.0, spaship service takes care of the end-to-end solution, handling everything from building to deployment
and hosting. by leveraging repository details, spaship creates a pipeline that automatically incorporates any source
code changes into its process.
in the case of containerized deployment, spaship utilizes openshift's native build config technique to generate
container images of the application. these images are then deployed in the target environment. whenever there is an
update in the source repository, the pipeline is triggered to initiate the build and deployment process.
for static resource deployment (planned for upcoming release), the workflow follows a similar approach. instead of
creating containers, spaship generates static resources and deploys them in the target environment. this method
functions similarly to a serverless technique, ensuring that any updates in the source code trigger the pipeline for
deployment.

## comparisons between workflows (2.0 & 3.0)

![comparisons between workflows](./images/comparisons_between_workflows.png)

## how is this different from the existing process?

before workflow support, spaship primarily dealt with static resource and container deployment. now, with the
introduction of workflow 3.0, you can directly build your application from your git repository (github/gitlab) and
deploy it directly to the targeted environment. in the first release, we have added the feature to use workflow 3.0 from
the spaship manager.

## key points to consider for workflow 3.0:

- existing attributes will be there for the deployment, consisting of name, path, ref, health-check-path, port &
  configuration.
- in workflow 3.0, we have introduced some new attributes including "repourl," "branch," "contextdir," "dockerfilename,"
  and "buildargs."
- repository details: in workflow 3.0, you need to provide the public repository url (github/gitlab) with the respective
  context directory and branch name. spaship will initiate the build process based on the provided repository details (
  after validation) and then proceed with the deployment.
- build argument: you can provide your build arguments as key-value pairs, which will enhance your build process. this
  is not mandatory for every application, and it can be configured from the spaship manager.
- in the repository validation, it will check whether the repository contains the dockerfile or not. in the manager, it
  will ask you for the docker file name (by default, it's dockerfile). if no docker file is found in the repository,
  then you won't be able to perform the deployment.
- spaship will also extract the port (if available) from the docker file, which can be changed by the user later. the
  default port will be 3000.
- if you register any repository and context directory for a particular application (irrespective of environments), you
  won't be allowed to use that repository and context directory in any other application.
- configurations can be explicitly modified. if you only change the configuration, the entire build process will not be
  performed. instead, only the configuration will be updated, resulting in minimal time to reflect the changes. however,
  if any other parameter is modified during the deployment, the entire application will be rebuilt and redeployed.
  additionally, if you wish to deploy your application without altering the existing details, you can do so using the
  one-click redeployment option.
- build & pod logs can be checked from the spaship manager, you can debug your application from the view log section of
  a particular application.

## spaship workflow 3.0 architecture

this is the complete architecture of the spaship workflow 3.0. we'll include the puzzle app in the upcoming release.
![spaship workflow 3.0 architecture](./images/spaship_workflow_30.png)

## spaship workflow 3.0 design details

here you'll find
the [complete design details](https://docs.google.com/presentation/d/1ebzb1y_u3i0wt3yyih91iihoooousmiltudprwvtppg/edit?usp=sharing)
related to workflow 3.0

## process of using workflow 3.0 from the spaship manager:

**step 1:** provide the permission for application creation from the spaship
![image 1](./images/spaship_workflow_30_step_1.png)
**step 2:** click on the add new app to create the workflow 3.0 deployment
![image 2](./images/spaship_workflow_30_step_2.png)
**step 3.1:** enable "from git repo" option to use workflow 3.0
![image 3.1](./images/spaship_workflow_30_step_3.png)
**step 3.2:** . enter repository details - repository url, context directory (default /), git branch (default main),
docker (default dockerfile)
![image 3.2](./images/spaship_workflow_30_step_3_2.png)
**step 3.3:** enter application details - name, environment, path (default /), health check path (default /), ref,
port (default 3000)
![image 3.3](./images/spaship_workflow_30_step_3_3.png)
**step 3.4:** enter application configuration (environment variables)
![image 3.4](./images/spaship_workflow_30_step_3_4.png)
**step 3.5:** enter the build arguments (for the docker build)
![image 3.5](./images/spaship_workflow_30_step_3_5.png)
**step 3.6:** review and submit the details
![image 3.6](./images/spaship_workflow_30_step_3_6.png)
**step 4.1:** check the build log for the application
![image 4.1](./images/spaship_workflow_30_step_4_1.png)
**step 4.2:** check the deployment logs for the application
![image 4.2](./images/spaship_workflow_30_step_4_2.png)
**step 5:** redeploy the application with the existing details and configurations
![image 5](./images/spaship_workflow_30_step_5.png)
**step 6:** check application status from the activity stream
![image 6](./images/spaship_workflow_30_step_6.png)
video guide
for [complete workflow 3.0](https://drive.google.com/file/d/1qzzbjtqcgdwud6xkkdjced_rbc7wlwoi/view?usp=sharing)
please note that workflow 3.0 deployments are protected
by [rbac](https://source.redhat.com/groups/public/spaship/blog_article/introducing_symlink_support_in_spaship).