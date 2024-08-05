# generate the lighthouse score for spa in spaship
the lighthouse feature in spaship is designed to enhance and accelerate your development. the goal is to generate the lighthouse report with a single click. developers need not worry about the pipeline or any type of integration. after a successful deployment, developers can generate the lighthouse report effortlessly.
## key points about the lighthouse feature:
1. trigger the lighthouse generate report from the application details in spaship manager (you need to have the application creation permission).
1. the lighthouse report can be generated for all types of deployments, including static, containerized (workflow 2.0 & 3.0), and for all environments.
1. for every new deployment, developers can generate a new lighthouse report, with a new lighthousebuildid.
1. from the spaship manager, you can view core metrics like performance, accessibility, best practices, seo, and pwa.
1. in the report view cls, fcp, fmp, speed metrics, total blocking time will be visible. for more detailed information, visit the lighthouse report portal.
1. the estimated time for report generation is 3-5 minutes, and it will be automatically updated in the spaship manager.
1. if a developer tries to generate a report without deploying the application, the report will be generated, but the lighthouse-build-id will remain similar; it will change with every new deployment.
## process for using symlink from the spaship manager:
let's walk through the process of using lighthouse in spaship manager to generate the scores for single page applications (spas)
**step 1.0: generate the lighthouse report from the spaship manager**
![step 1.0](./images/lighthouse_1.png)
**step 2.0: view the lighthouse report after the report generation**
![step 2.0](./images/lighthouse_2.png)
**step 3.0: view the complete report**
![step 3.0](./images/lighthouse_3.png)
**step 4.0: explore more details about the lighthouse report from the report portal**
![step 4.0](./images/lighthouse_4.png)
### restrictions & limitations:
1. if the application is unreachable [503] or not found on the required path [404], the lighthouse report cannot be generated until the application is live or redeployed.
1. if any application has authorization, the report cannot be generated.
### coming next:
1. auto-report generation after deployment.
1. distinguish stage and prod authorization and auto login using puppeteer script.