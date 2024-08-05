# cmdb code for spaship
### what changes are we bringing with the cmdb code in spaship?
in the new spaship release, we're incorporating the cmdb code for all onboarded properties. starting with this new release, anyone looking to onboard a new property must assign a corresponding cmdb code to that property.
### intended uses of the cmdb code:
the collected cmdb codes serve two primary purposes:
1. **mp+ resource tagging**
2. **identifying high-priority applications for improved high availability.**
### leveraging the cmdb code for streamlined deployments
by utilizing the cmdb code for the specific property, we'll gain insights into the business criticality of the applications. for instance, consider an application with a severity level of c1 or c2 indicating high business criticality. in this scenario, for that specific property, we'll ensure a higher level of availability. to achieve this elevated availability of the application, we'll deploy it across multiple clusters. as of now, it will only be applicable to the environment in the production cluster. here is the diagram for this:
![cmdb code deployment diagram](./images/cmdb_flow.png)
### how to add cmdb code during property registration:
**step 1**: open spaship.redhat.com, and click on the create new property
![step 1](./images/cmdb_step1.png)
**step 2.1**: if you have a cmdb code, you can put it in the placeholder and keep the "cmdb id" as selected
![step 2.1](./images/cmdb_step2.png)
**step 2.2**: if you don't know your cmdb code, you can also search it by your property name, it will eventually fetch & populate the cmdb code
![step 2.2](./images/cmdb_step2_2.png)
**step 3**: property will be created with that specific cmdb code, you can find your cmdb code and the severity of the application in the settings.
![step 3](./images/cmdb_step2_3.png)