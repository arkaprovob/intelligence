# spaship recovery work instruction (rwi) document
effective date: 2023-03-13
* introduction
    this recovery work instruction document guides recovering spaship after an incident. the purpose of this document is to ensure that the incident response team has the necessary procedures and documentation to restore spaship to its regular operation.
* overview of spaship
    spaship is a single page application hosting and delivery platform in managed platform plus. it allows front-end developers to upload their spas in managed kubernetes clusters without requiring knowledge about the underlying infrastructure.
    resources can be found under the [appendices section](#bookmark=id.ajtx7uozg3zv).
* incident response plan and escalation procedures
    the incident response plan for spaship outlines the procedures for identifying, responding to, and resolving incidents that affect the application. the incident response team includes the system administrator, network administrator, and developers.
    incidents are classified according to the severity and escalated based on their impact on spaship. the following incident classifications are used:
    <span style="text-decoration:underline;">major</span>: critical issue that impacts a high number of end users or critical business functions.
    <span style="text-decoration:underline;">critical</span>: significant issue that impacts some end users or non-critical business functions.
    <span style="text-decoration:underline;">minor</span>: minor issue that affects a small number of end users or non-critical business functions.
    <span style="text-decoration:underline;">low</span>: low-priority issue that does not impact end users or business functions.
    more details are available in the spaship sla matrix spreadsheet, the link given under the [appendices section](#bookmark=id.ajtx7uozg3zv).
* recovery procedures
    the following procedures should be followed to recover spaship after an incident has occurred:
1. first, determine the cause of the incident and document it.
2. notify the spaship development team and provide them with all necessary information about the incident.
3. check the  spaship application logs for any recent error incident, and if required, restart the selected spaship services and verify that it is functioning correctly.
4. verify that all data of every hosted property is intact and that no data has been lost.
5. if any data has been lost
    1. <span style="text-decoration:underline;">for hosted applications</span>: involve the respective stakeholder and restore it from the gitlab or github commit.
    2. <span style="text-decoration:underline;">for the spaship application database</span>: restore it from the most recent backup
6. test spaship to ensure that it is fully functional.
7. if spaship is not functioning properly, escalate the incident to the next level.
* testing procedures
    after spaship has been recovered, the following testing procedures should be performed to ensure that it is fully functional:
    verify that all web properties are intact and users can log in and access their applications.
    test all functional features of spaship to ensure that they are working correctly.
    perform a load test to ensure that spaship can handle the expected traffic.
* escalation procedures
    spaship has yet to have a dedicated incident response team. for the time being, the developers are responsible for providing support and resolving an incident. more details are given in the spaship sla matrix.
    the spaship team is working with the devops team in na to provide support during na hours while the india team covers apac/pune timezone. 
    in the interim, the escalation contact is  for all types of escalations. 
* documentation requirements
    the incident response team should document all incidents and recovery procedures. the following documentation should be created:
1. jira tickets for escalations.  
2. incident reports that include the cause of the incident, the steps taken to resolve it, and the impact it had on spaship.
3. recovery checklists that provide step-by-step instructions for recovering spaship.
4. other relevant documentation, such as architecture documents and web property hosting-related information in the mp+ cluster.
* training requirements
    the incident response team (spaship is yet to team up with the devops team for the same) and other personnel involved in the incident response and recovery process should be trained on the following:
1. the incident response plan for spaship.
2. the procedures for recovering spaship after an incident.
3. the testing procedures for ensuring that spaship is fully functional after recovery.
* appendices
    * **[spaship sla matrix](https://docs.google.com/spreadsheets/d/1mncw1tgqkod11ilb6gzkt7oyuyr_dn_q-lti_jfscm8/edit?usp=sharing)**
    * [spaship console](https://spashio.redhat.com)
    * [spaship io](https://spaship.io/)
    * [spaship architecture and workflow](https://docs.google.com/presentation/d/1o934uxdnibb8oa-womyp5kzm8a1lqjn14d5rlwbiqou/edit?usp=sharing)
    * **[spaship channel slack](https://app.slack.com/client/t027f3gaj/c04f5prkemc)**
    * [spaship roadmap](https://miro.com/app/board/uxjvpt37mga=/)
    * **[spaship jira link](https://issues.redhat.com/projects/spaship)**
    * **[spaship support email](mailto:spaship-dev@redhat.com)**