# spaship issues 
overview
this document covers the basic deployment steps and challenges faced during application deployment in spaship. this should also include the error messages and images from spaship managers.  
 
about spaship
* environments:
    * prod: [https://spaship.redhat.com/](https://spaship.redhat.com/)  
    * stage: [https://spaship.stage.redhat.com/](https://spaship.stage.redhat.com/) 
    * qa: [https://spaship.qa.redhat.com/](https://spaship.qa.redhat.com/)
* services:
    * operator
    * orchestrator   
    * manager
    * cli
* dashboard: [https://spaship.redhat.com/dashboard](https://spaship.redhat.com/dashboard) 
* sla: [https://spaship.redhat.com/sla](https://spaship.redhat.com/sla) 
* documentation: [https://spaship.redhat.com/docs](https://spaship.redhat.com/docs)  
* logs: 
* catchpoint alerts: 
<br>
<span style = 'font-size:larger'>important prerequisites </span>
* user should be connected to vpn
* user should be logged in using sso to deploy through manager. 
<span style = 'font-size:larger'>spaship manager</span>
* **the footer is returning garbled characters instead of valid html content for partner connect qa environment  for few specific applications**
    * the issue occurred due to garbled characters in the footer. the sync config for qa has two footers, one set to https://connect.qa.redhat.com/api/chrome/footer and the other to https://connect.qa.redhat.com/api/chrome/rh-unified-footer. accessing the first url results in a redirection to https://connect.qa.redhat.com/en/api/chrome/rh-unified-footer. however, as the sync service programmatically pulls web content, it cannot handle the redirection. this issue does not affect the application using the rh-unified-footer
    * this curl command will help to simulate and debug the issue **curl -x get https://connect.qa.redhat.com/api/chrome/footer --proxy http://squid.corp.redhat.com:3128**
<br>
* **all spaship environment pods in pre-prod clusters started failing**
    * this issue occurred due to a recent upgrade to the managed platform plus (mp+) cluster to v 4.11. the upgrade introduced new scc (security context constraint) policies - namely, restricted-v2, nonroot-v2, and hostnetwork-v2 - that impose more stringent criteria for admitting workloads based on pod security standards. consequently, the policy prevented the existing pods from starting because they included a script entry point that violated the new criteria. more details on this[ are available here.](https://connect.redhat.com/en/blog/important-openshift-changes-pod-security-standards#:~:text=the%20new%20(v2)%20policy%20versions%20drop%20all%20capabilities%2c%20while%20the%20previous%20versions%20%5bv1%5d%20only%20drop%20a%20subset.%c2%a0)
    * an [outage email](https://mail.google.com/mail/u/0/#sent/qgrcjhrtxbskncbzprkpvchtzjgsvnlbdkl) has been sent for the same 
    * [jira issue](https://issues.redhat.com/browse/spaship-1387) 
    * to solve the issue changed the docker entry point of the sidecar container from `entrypoint [ "/deployments/run-java.sh" ]`  to `env java_app_jar="/deployments/quarkus-run.jar"` rebuild the sidecar container and then deployed in all spaship environments.
<br>
* **akamai is redirecting to a malformed url which gives a 503 error, and the url contains two different addresses separated by a comma. [encountered issue link](https://issues.redhat.com/browse/spaship-1307)**
    * once an environment is configured with akamai redirection, the following two attributes need to be updated in the router config map specific to that environment. for example, if the name of the property is <span style= 'font-size:larger'>**developers** </span>and the name of the environment is <span style= 'font-size:larger'>**stage**</span>, then look for a configuration map in the property’s namespace called <span style= 'font-size:larger'>**router-config-developers-stage** </span>and alter the values of the following properties
        * <span style= 'font-size:larger'>**fallback :** </span>the default value is set to blank, change it to the base url of that specific application in case of the property mentioned above it is **[https://developers.stage.redhat.com](https://developers.stage.redhat.com)**
        * <span style= 'font-size:larger'>**forwarded_host:** </span>the default value is set to blank, change it to the name of the domain, from the example given above it would be **developers.stage.redhat.com**
    * **rca**: the <span style= 'font-size:larger'>**forwarded_host**</span> header is used by akamai for the request redirection purpose without the proper value it will resulting in an invalid redirection.
<!-- * soumya please document the solution [of this task](https://issues.redhat.com/browse/spaship-1308) with rca  here \ -->
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;spaship cli : 
<!-- &lt;please document errors occurred during deployments > -->
**important note:** please upgrade the cli to the [latest version](https://www.npmjs.com/package/@spaship/cli) before performing any troubleshooting
* **error message :  ›   error: the api key was not accepted by https://spaship.redhat.com/api/v1/applications/deploy/one-platform/prod**
    * **invalid api key issue :**
    * ![alt_text](images/spaship-issues-img/image1.png "image_tooltip")
    * error message :  ›   error: the api key was not accepted by https://spaship.redhat.com/api/v1/applications/deploy/one-platform/prod 
    * **solutions :**
        * please create a new api key from the specific  web property
        * check the deployment url too, if it’s matched with the created apikey
<br>
* **error message error you should provide the archive file name which contains the spaship.yaml file**
* **not providing the archive for the deployment** 
* ![alt_text](images/spaship-issues-img/image2.png "image_tooltip")
* **solutions :**
    * pass the archive (zip of the distribution) file name with the deployment command
    * command : spaship deploy -e={deployment_url} --apikey={api_key} <span style= 'font-size:larger'>**archive.zip**</span>(you may use npm pack for creating distribution)
    * pass your distribution (post build)
    *  as -–builddir argument with the distribution 
    * command : spaship deploy -e={deployment_url} --apikey={api_key} **--builddir=dist**
    * explicitly mention **builddir=dist** in to the **spaship.yaml** file
<br>
* **error message : enoent: no such file or directory, open 'spaship.yaml'**
* **no spaship.yaml file present**
* ![alt_text](images/spaship-issues-img/image3.png "image_tooltip")
* **solutions :**
    * please check that you have ‘spaship.yaml’ in the correct directory or not
    * please run `spaship init` to deploy to generate
<br>
* **unable to connect with spaship**
    * ![alt_text](images/spaship-issues-img/image4.png "image_tooltip")
    * error message : error: unable to connect to [https://spaship.redhat.com/api/v1/applications/deploy/one-platform/prod](https://spaship.redhat.com/api/v1/applications/deploy/one-platform/prod).
    * **solutions :**
        * please check you’re connected to vpn or not
        * check if there is any preplanned outage from the team
        * if you’re connected to vpn and still getting this issue, please inform to [spaship-dev@redhat.com](mailto:spaship-dev@redhat.com) or forum-spaship 
* **service unavailable or pointing to the invalid server issue**
    * ![alt_text](images/spaship-issues-img/image5.png "image_tooltip")
    * error message : error: the server returned an invalid message.  the server may be down, or your .spashiprc.yml may  be pointing at the wrong server (please upgrade your cli version and try again).
    * **solutions :**
        * please check your **deployment url** from your spashiprc file or the deployment command
        * check if there is any preplanned outage from the team
        * if you’re connected to vpn and still getting this issue, please inform to [spaship-dev@redhat.com](mailto:spaship-dev@redhat.com) or forum-spaship 
* application takes too long to deploy?
    * please try to deploy again or check your internet connection
* application stuck on cli prompt? 
    * close the cli, and try to deploy again
* the richard feyman message (root cause : unknown)
* [cli planned enhancement](https://issues.redhat.com/browse/spaship-1259)
    <span style= 'font-size:larger'>**spaship manager**</span>
<!-- &lt;please document errors occurred during deployments > -->
* deploy app using spaship manager
* the access url does not generate on preprod environment whenever the access quotas exhausts
* client side exception after some amount of inactivity on the manager
    * ![alt_text](images/spaship-issues-img/image6.png "image_tooltip")
    * please refresh and try to login (this is occurred due to long time of inactivity)
* endless loading occurs on property creation page  
* trying to create an already existing property
![alt_text](images/spaship-issues-img/image7.png "image_tooltip")
![alt_text](images/spaship-issues-img/image8.png "image_tooltip")
**401  is not unauthorized code. this occurs in normal tab after certain period of inactivity**
misc questions
* if we are automatically deploying our app to spaship, where would i setup the proxy so that the publish domain is accessible to everyone?
    * for your property, there are four environments, dev, stage, and qa are the pre-production environments, and prod is the production environment.
        in the akamai setup, the urls for those three preprod environments, dev, stage, and qa, will only be internally accessible. you cannot access it without a proxy.
        whereas the prod environment, which will be connected to the [public url](http://developers.redhat.com/), will be publicly accessible, i.e., anyone can use it without a proxy setup, and for that, you will have to publish your application to the prod environment.
        if you go to the [settings page of your property](https://spaship.redhat.com/properties/developers/settings), there you will find the information about those different environments and their deployment urls.
        this [article](https://source.redhat.com/groups/public/customer-platform-devops/digital_experience_operations_dxp_ops_wiki/using_squid_proxy_to_access_akamai_preprod_domains_over_vpn) explains how to set up a squid proxy for accessing the pre-prod environments.
* i am attempting to deploy my app with the path _/api/docs_ but it keeps showing the following. oddly enough, when i try to navigate to _/api_ it works, but not _/api/docs_. here is my spaship.yaml file:
```
        name: api-documentation-dev
        path: /api/docs
        single: true
        builddir: build
```
&lt;answer here>
* next question 
* next question
* next question 