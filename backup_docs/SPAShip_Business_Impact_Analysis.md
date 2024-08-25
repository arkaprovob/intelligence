# spaship bible

# purpose

find out answers to the following questions and act on eliminating or minimizing the impact when spaship goes down.

* [what happens when the spaship goes down today? ](spaship_service_breakdown_consequences.md)
* what would happen if spaship does not come online for 24/48 hrs.?

# scope

this document focuses on assessment, events and documentation that is significant for faster recovery to minimize the
impact of disruption to spaship services. the document should also focus on eliminating the loss of valuable information
collected by spaship and related integrations.
<!-- note: this denotes that docs will be moved to backstage   -->

# documents

[deloyment environment  overview](spaship_infrastructure.md)
[spaship services overview](spaship_services_overview.md)
[dependencies and business impact analysis](spaship_dependencies:business_impact_analysis.md)
workflow documents
[spaship issue register](spaship_issues.md) - this can be part of faqs
spaship playbook
<!-- * [propertywise stakeholders list (owner point of contact etc.)](https://docs.google.com/spreadsheets/d/1ya48rbt8kf4gtfjokeleashul_-d2okml6yaqpgbl8k/edit?usp=sharing) -->

* spaship application setup,build, deployment and environments
* continuous integration and delivery (ci/cd) integration
* guidelines for securing spaship deployments and recommendations for secure communication with openshift and other
  components
* maintenance and upgrades
    * strategies for disaster recovery and backup of spaship deployments
    * backing up application configurations, data, and resources
    * procedures for recovering from failures or outages
* additional resources or references for further information
  global coverage
  [sla document](spaship_recovery_work_instruction.md)
  [catchpoint alerts](https://portal.catchpoint.com/ui/symphony/controlcenter/tests/product/23729)
* spaship operator service alert
* spaship manager service alert
* spaship mongodb instance alert
* other dependencies
    * akamai
    * auth.redhat.com
    * mp+
      criticality rating
      cmbd codes
      where do i find logs?
      where do i report problems? 