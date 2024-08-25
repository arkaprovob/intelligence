troubleshooting
**question:** the footer is returning garbled characters instead of valid html content for partner connect qa
environment for few specific applications.  
**answer:** the issue occurred due to garbled characters in the footer. the sync config for qa has two footers, one set
to https://connect.qa.redhat.com/api/chrome/footer and the other
to https://connect.qa.redhat.com/api/chrome/rh-unified-footer. accessing the first url results in a redirection
to https://connect.qa.redhat.com/en/api/chrome/rh-unified-footer. however, as the sync service programmatically pulls
web content, it cannot handle the redirection. this issue does not affect the application using the rh-unified-footer

- this curl command will help to simulate and debug the issue
  `curl -x get https://connect.qa.redhat.com/api/chrome/footer --proxy http://squid.corp.redhat.com:3128`
  **question:** all spaship environment pods in pre-prod clusters started failing.  
  **answer:** this issue occurred due to a recent upgrade to the managed platform plus (mp+) cluster to v 4.11. the
  upgrade introduced new scc (security context constraint) policies - namely, restricted-v2, nonroot-v2, and
  hostnetwork-v2 - that impose more stringent criteria for admitting workloads based on pod security standards.
  consequently, the policy prevented the existing pods from starting because they
  included a script entry point that violated the new criteria. more details on this are available here.
- an outage email has been sent for the same
- jira issue
- to solve the issue changed the docker entry point of the sidecar container from to env
  rebuild the sidecar container and then
  deployed in all spaship environments.
  **question:** akamai is redirecting to a malformed url which gives a 503 error, and the url contains two different
  addresses separated by a comma.  
  **answer:** related issue link; once an environment is configured with akamai redirection, the following two
  attributes need to be updated in the router config map specific
  to that environment. for example, if the name of the property is developers
  and the name of the environment is stage, then look for a configuration map in
  the property’s namespace called router-config-developers-stage and alter the values of the following properties
- fallback: the default value is set to blank, change it to the base url of that specific application in case of the
  property mentioned above it is https://developers.stage.redhat.com
- forwarded_host: the default value is set to blank, change it to the name of the domain, from the example given above
  it would be developers.stage.redhat.com
- rca: the forwarded_host header is used by akamai for the request redirection purpose without the proper value it will
  resulting in an invalid redirection.
  **question:** error message : › error: the api key was not accepted
  by https://spaship.redhat.com/api/v1/applications/deploy/<name-of-property>/<environment>  
  **question:** error message : › error: the api key was not accepted
  by https://spaship.redhat.com/api/v1/applications/deploy/one-platform/prod  
  **answer:** solutions :
  entrypoint [ "/deployments/run-java.sh" ]
  java_app_jar="/deployments/quarkus-run.jar"
- please create a new api key from the specific web property
- check the deployment url too, if it’s matched with the created api key
  **question:** error message : error: you should provide the archive file name which contains the spaship.yaml file.  
  **answer:** not providing the archive for the deployment
- solutions :
- pass the archive (zip of the distribution) file name with the deployment
  command
- command : `spaship deploy -e={deployment_url} --apikey={api_key}
archive.zip (you may use npm pack for creating distribution)`
- pass your distribution (post build)
- as -–builddir argument with the distribution
- command : `spaship deploy -e={deployment_url} --apikey={api_key}
--builddir=dist`
- explicitly mention builddir=dist in to the spaship.yaml file
  **question:** error message : enoent: no such file or directory, open 'spaship.yaml'.  
  **answer:** no spaship.yaml file present
- solutions :
- please check that you have ‘spaship.yaml’ in the correct directory or not
- please run `spaship init` to deploy to generate
  **question:** error message : error: unable to connect to spaship  
  **answer:** solutions :
- please check you’re connected to vpn or not
- check if there is any preplanned outage from the team
- if you’re connected to vpn and still getting this issue, please inform to spaship-dev@redhat.com or forum-spaship
  **question:** error message : error: the server returned an invalid message. the server may be down, or your
  .spashiprc.yml may be pointing at the wrong server (please upgrade your cli version and try again).  
  **answer:** solutions :
- please check your deployment url from your spashiprc file or the
  deployment command
- check if there is any preplanned outage from the team
- if you’re connected to vpn and still getting this issue, please inform to
  spaship-dev@redhat.com or forum-spaship
  **question:** application takes too long to deploy?  
  **answer:** please try to deploy again or check your internet connection
  **question:** application stuck on cli prompt?  
  **answer:** close the cli, and try to deploy again
  **question:** spaship manager is giving 401 is not unauthorized code all of a sudden  
  **answer:** this occurs in normal tab after certain period of inactivity.
  **question:** spaship workflow 2.0 (containized deployment) “npm err! code eaccess”  
  **answer:** for the workflow 2.0, if you want to build it using the github action you’ve
  to do a slight modification in the ci and you’ve to set the usergroup in
  the action secret. here is the updated ci, you can take the ref from this.
- for the workflow 3.0, you can take the reference of this repository
  (dockerfile) , and in this case you have to pass usergroup (1004990000) as the build argument from the spaship manager
  during the deployment, else you will face the npm issue.
  faq
  **question:** what are the primary requirements for accessing spaship.  
  **answer:** user should be connected to vpn.
- users should be logged in using sso to deploy through manager.
  **question:** what is spaship?  
  **answer:** spaship is a dedicated deployment platform designed to streamline the deployment of all kinds of front-end
  applications into a mp+. it simplifies the process by eliminating the need for in-depth knowledge of kubernetes or
  openshift intricacies.
  **question:** what spaship is not?  
  **answer:** it is not the same as akamai cdn.
  **question:** how to host on spaship?  
  **answer:** ans: [quickstart deployment guide | spaship](https://spaship.io/docs/guide/user-guide/quickstart/)
  **question:** how spaship works?  
  **answer:
  ** [spaship workflows](https://docs.google.com/presentation/d/1o934uxdnibb8oa-womyp5kzm8a1lqjn14d5rlwbiqou/edit?usp=sharing).
  **question:** how to start contribution in spaship ?  
  **answer:
  ** [spaship developer’s guide](https://docs.google.com/document/d/1n5gpm2bghff3vefyyhrd0lfmiyonlbrh4tsyg5vaok8/edit?usp=sharing)
  it'sawip
  **question:** how is spaship different from one platform?  
  **answer:** spaship focuses on improving the deployment experience by providing cli and
  an interactive user interface for web property management and with the ability to be integrated with existing ci based
  deployment platforms whereas one platform provides services like authentication, feedback, search, notifications etc
  **question:** how one platform utilizes spaship  
  **answer:** one platform spas are deployed using spaship cli and are hosted on spaship.
  **question:** what are the minimum system requirements to install spaship  
  **answer:** depending on how many properties and environments are hosted via spaship, in
  general spaship consists of three services 1. operator: each instance of operator requires 512mb of ram and two
  millicore cpu; total no of instance is 4 2. orchestrator: each instance of orchestrator requires 2048mb of ram and one
  millicore cpu; total instance 2. 3. manager : each instance of orchestrator requires 1024mb of ram and .5 millicore
  cpu; total instance 2.
  **question:** how does spaship help its stakeholders ?  
  **answer:** by removing the following pain points for developers and application owners
- deploying web apps is too difficult. it consumes a lot of developer time
- dealing with ci
- long deployment time
- fixed number of environments to work with
  **question:** how to publish new path to akamai  
  **answer:** please
  follow [this guide](https://docs.google.com/document/d/1con0_czeqdx1sb6s9v9hssveqccscbgrwdm1xk-y48a/edit?usp=sharing)
  for more information.
  **question:** where can i find spaship recovery instruction?  
  **answer:
  ** [spaship recovery work instruction document](https://docs.google.com/document/d/1pz5zk5xgwxqygeo-n6xb-r-nnppzgcoxq0q78sudquq/edit?usp=sharing).
  **question:** how and where is the spaship service’s health and status monitoring process configured?  
  **answer:
  ** [how to use catchpoint for spaship monitoring.docx](https://docs.google.com/document/d/19tlzovxxvxcdy5m9rcwxpklceegj91fj/edit#heading=h.gjdgxs).
  **question:** where can i find spaship’s services overview ?  
  **answer:
  ** [spaship services overview](https://docs.google.com/document/d/1kkudvgsqybmk4ddh-zkobqbfgidzs_tvbtypgsxly_4/edit#heading=h.54fkbadgf4hp).
  **question:** where can i find spaship’s business impact analysis  
  **answer:
  ** [spashipdependencies:businessimpactanalysis](https://docs.google.com/document/d/1cti6zruarpdndyba5tql_663-sdk1u62ljb6tdzkeyk/edit#heading=h.usv2wz4eveoc)
  and [spaship service breakdown consequences](https://docs.google.com/document/d/1dvlbupzjrnvm1amy91nzhss1iukefozrznjb6w0v34a/edit#heading=h.171hwayaxj4y).
  **question:** where can i find spaship recovery instructions?  
  **answer:
  ** [spaship recovery work instruction document](https://docs.google.com/document/d/1pz5zk5xgwxqygeo-n6xb-r-nnppzgcoxq0q78sudquq/edit).
  **question:** if we are automatically deploying our app to spaship, where would i setup the proxy so that the publish
  domain is accessible to everyone?  
  **answer:** for your property, there are four environments, dev, stage, and qa are the pre-production environments,
  and prod is the production environment.in the akamai setup, the urls for those three preprod environments, dev, stage,
  and qa, will only be internally accessible. you cannot access it without a proxy.whereas the prod environment, which
  will be connected to the public url, will be publicly accessible, i.e., anyone can use it without a proxy setup, and
  for that, you will have to publish your application to the prod environment.if you go to the settings page of your
  property, there you will find the information about those different environments and their deployment
  urls.this [article](https://source.redhat.com/groups/public/customer-platform-devops/digital_experience_operations_dxp_ops_wiki/using_squid_proxy_to_access_akamai_preprod_domains_over_vpn)
  explains how to set up a squid proxy for accessing the pre-prod environments.
  **question:** where can i find the changelog of spaship?.  
  **answer:
  ** [spaship release logs](https://docs.google.com/document/d/1tdwbct9d3n3ljnjpid7b67304tgl2urwnkwswgasnhk/edit?usp=sharing)