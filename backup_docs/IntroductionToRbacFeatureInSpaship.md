# rbac in spaship

we're introducing the rbac feature in spaship. this helps to ensure that users only have access to the resources that
they need to perform their job functions and protects sensitive resources (all the operations) from unauthorized access.
rbac will help spaship comply with these regulations by providing a clear and auditable record of who has access to what
resources and what actions they can perform.

## access control list

as there will be six permissions in the access control list, they consist of api key creation-deletion, environment
creation-sync & permission creation-deletion.

## key points of rbac

- specific permissions for all the member (owner/user) of a particular web property
- there will two roles - owner & user
    - owner: someone who has the access for all the permissions
    - user: someone who has the access for some specific permissions
- important note: a user can also have the access of permission creation & deletion
- we can search a member form the organization (rover search) and provide the specific access.
- we can directly search from the rover group and provide specific access to the members exist in that rover group
- someone who has the access of permission create & delete, can provide or revoke the access for the other
- a member can not delete himself from the property or revoke his/her access for "permission creation & delete" if
  exists
- after creating a new property the default access will be provided to property creator.

## access registration workflow

![image](./images/rbac1.png)

## rbac technical details

here you'll find the complete technical details related to rbac.

## process of using rbac from the spaship manager

### step 1

go to the property settings, there will be a section for managing the permissions
![step 1](./images/rbac_step1.png)

### step 2.1

search & provide the access to the members
search user from the rover with the name or the email id. you'll get the list of the users and select from there.
![step 2.1](./images/rbac_step2a.png)
you can search for multiple members and add them in the list. by default user access will be provided, you can change
the permission according to yourself.
![step 2.1](./images/rbac_step2b.png)
if you click on the show advance settings you'll find all the permissions list, you can choose from there and modify as
per your requirement.
![step 2.1](./images/rbac_step2c.png)

### step 2.2

in the same way, you can fetch the members of the rover group. you have to provide the name of the rover group and it'll
show you all the members of that particular rover group. you can set the permissions accordingly, as per your
requirements.
![step 2.2](./images/rbac_step2_2.png)

### step 3

get the list of the newly added members (here the sot is rover in this case)
![step 3](./images/rbac_step3.png)

### step 4.1

edit the permissions for all the listed members (someone who has the access of permission create & delete, can provide
or revoke the access for the other)
![step 4.1](./images/rbac_step4.png)

### step 4.2

in the same way, if you want you can manage the permission for the members by clicking on the configure access
![step 4.2](./images/rbac_step4_2.png)

### step 5

delete a member from the property. (after deleting the member, he/she won't be able to perform any of the actions)
![step 5](./images/rbac_step5.png)

### step 6

find all the event logs for the rbac operations in the activity stream
![step 6](./images/rbac_step5_1.png)

#### video guide for [complete spaship rbac workflow](https://drive.google.com/file/d/1xgn55mpjig_cdlat1g7we1l9nnbqnzcc/view?usp=sharing)