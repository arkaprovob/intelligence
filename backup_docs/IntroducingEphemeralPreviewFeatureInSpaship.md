# introducing ephemeral preview feature in spaship
## spaship ephemeral preview feature
the spaship ephemeral preview feature is designed to enhance and accelerate development processes. it relies heavily on the ci pipeline and creates an ephemeral environment optimized for previewing changes before final deployment. below are the key points and workflow for ephemeral preview in spaship.
### key points
1. **trigger ephemeral environment from the cli**
2. **optimized ephemeral environment creation:**
   - create a single environment for a specific pull request id to avoid multiple ephemeral environments.
   - use the action id for optimized ephemeral environment creation for multiple deployments.
3. **latest deployment monitoring:** check the latest ephemeral deployment from the manager's ephemeral environment section.
4. **automatic cleanup:** ephemeral environments are deleted after a certain time (initially set to 24 hours).
5. **no extra authorization:** use the same deployment url and api key for ephemeral environment deployment with specific args (--preview/-p).
### cli & manager workflow
#### cli:
to use ephemeral environment, you need to upgrade your @spaship/cli to version 1.5.4 or above. you can download it from here. you can check the ephemeral env creation instruction below.
**step 1:** initialize spaship.yaml file using `spaship init` to generate the config file.
![initialize spaship.yaml](./images/ephemeral_1.png)
**step 2:** pass `--preview` or `-p` to deploy in ephemeral environment with the existing deployment command `spaship deploy`. new ephemeral environment will get created with the each deployment.![preview](./images/ephemeral_2.png)
**step 3:** for the optimized ephemeral environment creation you need to pass `--prid={prid}` along with `--preview` or `-p` flag.
![preview](./images/ephemeral_3.png)
**step 4:** deployment commands
##### single-ephemeral preview deployment
- `spaship deploy -env={url} --apikey={apikey} --ref=1.1 -preview` -`spaship deploy -env={url} --apikey={apikey} --ref=1.1 -p`
##### ephemeral preview deployment based on the pr id
- `spaship deploy -env={url} --apikey={apikey} --ref=1.1 -p --prid=19`
- `spaship deploy -env={url} --apikey={apikey} --ref=1.1 -preview --prid=19`
###### ephemeral environment creation :
![preview](./images/ephemeral_4.png)
#### manager:
**step 1:** access the ephemeral environment tab in spaship manager.
![ephemeral environment tab](./images/ephemeral_5.png)
**step 2:** monitor the activity stream for successful deployment and check details like pr id, time left for the ephemeral environment, and internal access url for the deployed spas.
![activity stream](./images/ephemeral_6.png)