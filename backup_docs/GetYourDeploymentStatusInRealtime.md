# get your deployment status in realtime

## realtime activity stream feature

the realtime activity stream feature improves our deployment experience and provides real-time status about the
deployment activities. we can easily integrate it for the particular web properties.

### key points of the realtime activity stream:

- receives the realtime activities for the properties.
- integration can be done anywhere, such as any services, consoles, etc.
- it can be used for analytics, notifications, or triggering other dependent services.
- emits all types of events including 'application deployment started', 'application deployed successfully', etc.
- no additional configuration is required for consuming the events (it will work with any existing valid apikeys).

### realtime activity stream workflow:

![realtime activity stream workflow](./images/realtime%20activity%20stream%20workflow.png)

### implementational details:

1. **step 1:** create an apikey for consuming the streams (existing any key will work as well).
   ![create apikey](./images/real_time_1.png)
2. **step 2:** consume event from any services (consuming in the console for demo purposes).
    - **endpoint:** `https://spaship.redhat.com/api/v1/analytics/events/{propertyname}`
    - **curl command:**
      ```bash
      curl --location --request get 'https://spaship.redhat.com/api/v1/analytics/events/{propertyname}' \
      --header 'authorization: bearer {apikey}'
      ```
    - **demo response:**
      `json
      data: {"activitystream":{"propertyidentifier":"one-platform","action":"application_deployment_started","props":{"applicationidentifier":"test1","env":"ephemeral-1b95"},"message":"deployment started for test1 at ephemeral-1b95","createdby":"souchowd@redhat.com","source":"cli"}}
      `
      ![consume event](./images/real_time_2.png)