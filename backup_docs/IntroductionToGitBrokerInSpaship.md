# what is the git broker?
the concept behind the git broker app is to streamline developers' experiences by enabling direct deployment of applications from git repositories. with this tool, developers can kickstart the deployment process with just one interaction, significantly reducing the time and effort typically associated with deployment tasks. after committing code to the repository, a simple comment initiates the deployment of the application. this solution requires no modifications to the current deployment workflow or the application itself, making configuration simple and resulting in a substantial reduction in deployment workload.
## key points about git broker:
- this feature aims to enhance the deployment experience of workflow 3.0.
- developers need to perform the initial deployment from the spaship manager to register the application and git url.
- in gitlab, integration of the git broker webhook (available in the spaship manager) is required. the webhook secret should be the api key.
- in the webhook configuration, you've got to provide access for the following events: push events, tag push events, comments, and merge request events.
- once the repository is configured, after every commit, developers need to mention the required environment (preprod cluster environments only) in the comment (e.g., "spaship dev").
- it will deploy the application based on the pre-existing configuration of the workflow 3.0 deployment from the spaship manager.
- all deployment statuses and activities will be accessible in the comment thread and also in the manager.
- the estimated deployment time aligns with the workflow 3.0 deployment process. initially, it will build the application and then commence the deployment.
- as of now, it's only available for the internal redhat gitlab instance (gitlab.cee.redhat.com). github support will be provided shortly.
- additionally, we've introduced zero-click deployment. once a pull request is created, it will automatically generate an ephemeral environment. further details can be found in [this link](https://source.redhat.com/groups/public/spaship/blog_article/deploy_spa_with_zero_interaction_using_git_broker__ephemeral_environment).
## process for using git broker:
let's walk through the process of using git broker to deploy single page applications (spas).
**step 1:** initiate the normal workflow 3.0 deployment from the spaship manager. additionally, please ensure that it's a gitlab repository on the redhat gitlab instance. to learn more about workflow 3.0, please visit [this blog](https://source.redhat.com/groups/public/spaship/blog_article/introduction_to_spaship_workflow_30).
**step 2:** after successfully deploying and registering your application, proceed to the settings and copy the gitbroker webhook url.
**step 3:** generate an api key for the specific application from the settings.
**step 4:** navigate to the gitlab project repository and click on "settings" in the navigation bar. then, select "webhooks" and proceed to add a new webhook.
**step 5:** paste the copied git broker url as the webhook url. in the "secret token" option, paste the api key. enable permissions for push events, tag push events, comments, and merge request events.
**step 6:** make a new commit in that repository, and the system will prompt you to specify the environments for deployment.
**step 7:** in the comment for the new commit, mention the environment as "spaship dev". this will trigger the initiation of the build and deployment processes.
**step 8:** once the operation is completed, you will receive the application deployment status event in the comment.
**step 9:** you can verify the status by checking the spaship manager activity stream.