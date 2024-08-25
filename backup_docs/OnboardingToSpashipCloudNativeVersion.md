# spaship cloud native version migration steps

1. update spaship cli to the latest major version (`@spaship/cli@x.x` - version **1.5.3** at the time of writing this
   update).
    - package link: [npmjs.com/package/@spaship/cli](http://www.npmjs.com/package/@spaship/cli)
2. obtain a new deploy url (vpn required):
    - go to spaship manager: [spaship.redhat.com](https://spaship.redhat.com)
    - select your property: ![select property](./images/cloud_native1.png)
    - click on "environment configuration" next to the property
      name: ![environment configuration](./images/cloud_native2.png)
    - copy the deploy url: ![copy deploy url](./images/cloud_native21.png)
3. obtain a new api key (vpn required):
    - follow the first three steps mentioned above to navigate to your property.
    - click on "create api key": ![create api key](./images/cloud_native31.png)
    - select the expiration date and click on create: ![select expiry date](./images/cloud_native32.png)
    - copy the api key for use in automated or manual deployments.
4. automated deployment (using jenkins/gitlab cd pipeline):
   ```bash
   - npm install
   - npm run build
   - echo "build created successfully for $deploy_env"
   - export version=$(node -p "require('./package.json').version") // not required
   - npx @spaship/cli@latest deploy --apikey=$deploy_key --env=$spaship_deploy_env --ref=$version
   ```
5. manual deployment:
   update `.spashiprc.yml` file with the new api key. find more details in the spaship documentation.
   video
   tutorial: [spaship cloud native migration](https://drive.google.com/file/d/150oyktzdmqmxkwns1mdkqio7zvgyccgp/view?usp=sharing)
   quick start guide: [spaship quickstart guide](https://spaship.io/docs/guide/user-guide/quickstart/)
   for questions/concerns:

- email: spaship-dev@redhat.com
- chat room: spaship