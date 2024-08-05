## documentation
### possible causes of deployment errors in spaship projects and how to resolve them:
there are several possible reasons for deployment errors in your spaship project. one possibility is that there was a mistake with the file type or deployment url specified in your .yml file. another possibility is that your api key has expired, which can cause issues with authentication and authorization. to resolve these issues, you may need to check your deployment url and file type, as well as ensure that your api key is still valid and up-to-date. if generating a new key seems to work, consider upgrading the cli version to 1.5.5 for better error logging.
### deleting deployments in spaship:
**question:** hey! is there a way to delete deployments i've made? i can't seem to find an option for it.  
**answer:** currently, we don’t have a delete feature for deployments. if you need to delete any application, please create a ticket for us, and we’ll assist you with it.
### overwriting deployments in spaship:
**question:** how can i overwrite a deployment instead of adding another one? i've noticed the deployment count keeps increasing, but i'd like to maintain just one deployment.  
**answer:** you can override the deployment by either changing the path for the particular application or by re-uploading it into the same path.
### changing deployment path:
**question:** so, if i change the path in my spaship file, does that effectively overwrite the existing deployment?  
**answer:** yes, if you change the path or name in your spaship file and redeploy, it will effectively overwrite the existing deployment.
### understanding deployment count:
**question:** what does the deployment count represent? is it the number of times i've deployed the application?  
**answer:** yes, exactly. the deployment count indicates how many times you've deployed the application. each deployment adds to this count.
### spaship's resilience and failover mechanism:
**question:** what is spaship's resilience and failover mechanism?  
**answer:** spaship is pretty resilient, and any environment failure will automatically attempt to recover. in production environments, there are more than one instance. if an instance fails, the traffic will be redirected to other instances.
### spaship sla (service level agreement):
**question:** does spaship have an sla (service level agreement)?  
**answer:** yes, you can find the sla at this link: https://spaship.dev.redhat.com/sla
### resolution of .htaccess bug:
**question:** is the bug with .htaccess still ongoing in spaship?  
**answer:** no, it was present in the previous bare metal version of spaship but has been resolved after migrating to the cloud native version. you can use a .htaccess file now.
### filing a ticket for deleting deployments:
**question:** where should i file a ticket for deleting deployments in spaship?  
**answer:** there will be a provision in the spaship ui to delete them once rbac is released. in the meantime, you can create a ticket and request the team to do it for you.
### troubleshooting deployment errors:
**question:** i am getting a 400 error when deploying my project, even though it has been working fine for a while. what could be causing this issue?  
**answer:** the error message suggests that there may be an issue with file type or api key expiry. to resolve the issue, you can try generating a new api key and updating your deployment configuration accordingly. additionally, upgrading the cli version to 1.5.5 may have helped with better error logging.
### access denied issue:
**question:** i am trying to access the web property for spaship at <https://spaship.redhat.com/>, but when i click on the publish url i get an access denied error. is this supposed to be like that?  
**answer:** it seems like there might be a proxy issue preventing you from accessing the web property. you can try adding a proxy to your browser settings and see if that resolves the issue. if it does not, then it's possible that there is an spa deployment issue at play. in this case, please provide more information about the output you are seeing on the screen so we can better understand the problem and suggest a solution.
### handling nested routes:
**question:** how does spaship handle nested routes in an application's path?  
**answer:** according to the spaship documentation, when deploying an application with a nested route, spaship converts the forward slashes (/) into underscores (\_) for the internal access url. however, for the route url, it will be similar to the intended path. this is done to ensure that the internal access urls are unique and do not conflict with each other.
### handling unresponsive pages:
**question:** the spaship site is experiencing issues and displaying "this page has become unresponsive" messages.  
**answer:** it's affecting multiple pages on the website, and kyle buchanan was advised to clear his cache and login again in spaship. if that didn't work, soumyadip chowdhury created a jira for the problem and suggested testing the site using the stage environment prior to releasing a patch. additionally, there may be an issue with configuration key/value pairs not being applied correctly.
### troubleshooting performance issues:
**question:** what are the steps i can take if i am experiencing issues with spaship's performance?  
**answer:** if you are experiencing issues with spaship's performance, try clearing your cache and logging back into spaship. if the issue persists, please contact our support team for further assistance. they may ask you to provide more information about your browser and device settings, as well as any error messages or logs that you have encountered. w
### router url warning on static deployment:
**question:** i'm receiving an 'application is down' warning for a router url on a static deployment. what should i do?  
**answer:** if you're encountering an 'application is down' warning for a router url on a static deployment, follow these troubleshooting steps:
1. verify internal access url: firstly, ensure that the internal access url is functioning correctly and is up to date. if the internal access url is working fine, it indicates that the application is running properly internally.
2. check latest deployment archive: confirm that the latest .zip archive for the deployment is correct and matches the expected version. this ensures that the deployment package itself is not the source of the issue.
3. inspect router urls: verify the router urls associated with the deployment. check if there are any discrepancies or errors reported for these urls. ensure that all router urls are properly configured and accessible.
4. review cluster hosting: determine which clusters are hosting the application. check if there are any issues specific to certain clusters that could be affecting the accessibility of the application.
5. network investigation: considering the possibility of a network issue, especially with akamai, investigate if there are any network-related issues impacting the router urls. reach out to your network or akamai support team for further assistance in diagnosing and resolving any network issues.
6. monitor application deployment: keep an eye on the application deployment status and any updates from the development team. they will investigate the issue further and provide updates on the progress via the provided jira
link. 7. report issues: if you continue to experience issues accessing the application or if there are any further concerns, don't hesitate to reach out and report them. provide as much