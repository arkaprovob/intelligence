# spaship and spaship sandbox tenants overview
## introduction
this document provides an overview of two tenants, spaship and spaship sandbox, and their respective environments and clusters. a visual chart is included to help illustrate the relationships between the tenants, environments, and clusters.
## tenants 
1. **spaship sandbox(<span style="text-decoration:underline;">spaship–sandbox</span>)**: this tenant is designed for development, testing, and staging purposes. it is available in the following clusters (**all sandbox namespaces starts with spaship-sandbox–**):
    * iad2-preprod
    * iad2-prod
2. **spaship(<span style="text-decoration:underline;">spaship</span>)**: this tenant is designed for production environments. it is available in the following clusters  (**all spaship namespaces starts with spaship–**):
    * iad2-preprod
    * iad2-prod
    * e1-preprod
    * w2-preprod
    * e1-prod
    * w2-prod
## environments
### spaship sandbox
the spaship sandbox tenant has four different environments:
1. **dev**: development environment for initial development and testing.
2. **qa**: quality assurance environment for verifying the functionality and performance of the application.
3. **stage**: staging environment for final testing and validation before deployment to the production environment.
4. **preview**: preview environment for showcasing the application before it is released to the production environment, and this will be doubled as uat
### spaship
the spaship tenant has only one environment:
1. **production**: the live environment where the application is deployed for end users.
## visual chart
<table>
  <tr>
   <td><strong>cluster</strong>
   </td>
   <td><strong>spaship sandbox</strong>
   </td>
   <td><strong>spaship</strong>
   </td>
  </tr>
  <tr>
   <td><a href="https://console-openshift-console.apps.mpp.preprod.iad2.dc.paas.redhat.com/">iad2-preprod</a>
   </td>
   <td>✓
   </td>
   <td>✓
   </td>
  </tr>
  <tr>
   <td><a href="https://console-openshift-console.apps.mpp.prod.iad2.dc.paas.redhat.com/">iad2-prod</a>
   </td>
   <td>✓
   </td>
   <td>✓
   </td>
  </tr>
  <tr>
   <td><a href="https://console-openshift-console.apps.mpp-e1-preprod.syvu.p1.openshiftapps.com/">e1-preprod</a>
   </td>
   <td>
   </td>
   <td>✓
   </td>
  </tr>
  <tr>
   <td><a href="https://console-openshift-console.apps.mpp-w2-preprod.cfln.p1.openshiftapps.com/">w2-preprod</a>
   </td>
   <td>
   </td>
   <td>✓
   </td>
  </tr>
  <tr>
   <td><a href="https://console-openshift-console.apps.mpp-e1-prod.9e4s.p1.openshiftapps.com/">e1-prod</a>
   </td>
   <td>
   </td>
   <td>✓
   </td>
  </tr>
  <tr>
   <td><a href="https://console-openshift-console.apps.mpp-w2-prod.0jgd.p1.openshiftapps.com/topology/ns/spaship--preview?view=graph">w2-prod</a>
   </td>
   <td>
   </td>
   <td>✓
   </td>
  </tr>
</table>
<table>
  <tr>
   <td><strong>environments</strong>
   </td>
   <td><strong>spaship sandbox</strong>
   </td>
   <td><strong>spaship</strong>
   </td>
  </tr>
  <tr>
   <td>dev
   </td>
   <td>✓
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>qa
   </td>
   <td>✓
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>stage
   </td>
   <td>✓
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>preview
   </td>
   <td>✓
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>production
   </td>
   <td>
   </td>
   <td>✓
   </td>
  </tr>
</table>
## conclusion
this document provides a comprehensive overview of the two tenants, spaship sandbox and spaship, and the environments and clusters where they are available. the table included helps to illustrate the relationships between these components for better understanding.