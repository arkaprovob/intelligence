### what is the purpose behind the zero-interaction deployment!

currently, to deploy an application, we require at least one interaction to initiate the deployment process. however,
with git broker, we are introducing zero-interaction deployments. initially, this feature is exclusively available for
ephemeral environments. it will operate with merge requests; after the creation of any merge request, an ephemeral
environment will be generated for the respective application.

### key points about this workflow:

- this feature aims to enhance the deployment experience within workflow 3.0, improving overall efficiency.
- developers need to initiate the initial deployment process from the spaship manager to register both the application
  and its corresponding git url.
- integration of the git broker webhook, available in the spaship manager, is necessary within gitlab. the webhook
  secret should align with the api key for authentication purposes.
- when configuring the webhook, ensure access is provided for specific events, including the initiation of a merge
  request subsequent to any modifications within the repository.
- following the initiation of a merge request, an ephemeral environment will be dynamically generated, utilizing
  predefined configurations established within the preproduction environment.
- after merging, and upon the completion of necessary review processes, the application can also be deployed using the
  git broker commit
  mechanism ([blog link](https://source.redhat.com/groups/public/spaship/blog_article/introduction_to_git_broker_in_spaship)),
  ensuring the seamless progression of the software delivery lifecycle.
- through this approach, developers can streamline the deployment process, reducing manual intervention and facilitating
  faster delivery of updates and features.
  limitations: as of now, this feature is in beta, implying that it's currently undergoing refinement. rest assured,
  we're committed to further enhancing its functionality in the upcoming release.
  update ephemeral environments directly from the spaship manager. this enables the custom configuration for the
  ephemeral deployment
  retrieve the pod and build logs for the ephemeral environment deployment. this insightful data allows for
  comprehensive analysis and troubleshooting, ensuring smooth operation.
  customize your workflow to seamlessly trigger ephemeral environment initialization. by tailoring the process to your
  specific requirements, you can optimize efficiency and align with your team's practices and preferences.
  process for using zero interaction deployment: let's walk through the process of using git broker to deploy single
  page applications (spas)
  step 1: initiate the normal workflow 3.0 deployment from the spaship manager. additionally, ensure that it's a gitlab
  repository hosted on the redhat gitlab instance. for further insights into workflow
  3.0, [please refer to this blog](https://source.redhat.com/groups/public/spaship/blog_article/introduction_to_spaship_workflow_30).
  ![zero images interaction step 1 ](./images/zero_interaction_1.png)
  step 2: after successfully deploying and registering your application, proceed to the settings and copy the gitbroker
  webhook url.
  ![zero images interaction step 2](./images/zero_interaction_2.png)
  step 3: generate an api key from the settings for the specific application.
  ![zero images interaction step 3](./images/zero_interaction_3.png)
  step 4: navigate to the gitlab project repository and click on "settings" in the navigation bar. then, select "
  webhooks" and proceed to add a new webhook.
  ![zero images interaction step 4](./images/zero_interaction_4.png)
  step 5: paste the copied git broker url as the webhook url. in the "secret token" option, paste the api key. enable
  permissions for push events, tag push events, comments, and merge request events.
  ![zero images interaction step 5](./images/zero_interaction_5.png)
  step 6: create a pull/merge request (pr/mr) in the registered repository.
  ![zero images interaction step 6](./images/zero_interaction_6.png)
  step 7: an ephemeral environment is automatically created for the merge request. additionally, it prompts whether we
  want to deploy any other environment or not.
  ![zero images interaction step 7](./images/zero_interaction_7.png)
  step 8: the ephemeral environment can be validated from the spaship manager. in this case, it is automatically
  provisioned against pr number 10, as indicated in the action id.
  ![zero images interaction step 8](./images/zero_interaction_8.png)
  step 9: after merging, a prompt will appear asking if we want to deploy the changes in the preprod environments.
  following this, we can proceed with the deployment process from the commit. for more information on this process,
  please refer to this blog.
  ![zero images interaction step 9](./images/zero_interaction_9.png)
  important links related to git broker deployment
- [introduction to workflow 3.0](https://source.redhat.com/groups/public/spaship/blog_article/introduction_to_spaship_workflow_30)
- [streamlining deployment using git broker](https://source.redhat.com/groups/public/spaship/blog_article/streamlining_deployment_with_git_broker_)
- [introduction to git broke in spaship](https://source.redhat.com/groups/public/spaship/blog_article/introduction_to_git_broker_in_spaship)