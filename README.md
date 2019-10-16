# Final project: She Codes Volunteers Slack Channels Management 

## Introduction:

Today the volunteer group is managed by notes on google drive and the permission for the variety systems of She Codes organization (Facebook, Slack, Connect, Google Drive, WIKI etc.) are given manually.
The goal of this project is to automate this process. Due to time constraints, the project focused on creating database scheme and the ability to add volunteers automatically to channels on Slack application. The design of this project is such that it can be extended to make use of other API integrations.

## Use case:

User can add to the program's database a new volunteer. The role of volunteer must be supplied.
Each role is  attributed to specific slack channels in the db.
In the background, the following actions are being committed:
Check if the newly added volunteer email is registered with the she codes slack workspace.
If new volunteer is already in the workspace, then add user to channels relevant to role.
Else new volunteer isn’t yet in workspace. Send volunteer an email with a link** with an invitation to slack workspace. In addition,add volunteer to the SlackPollingStatus table so that we can keep track of his registration status.
A polling process is running in background, sampling SlackPollingStatus table, seeking volunteers with status “Not in workspace”.
For each volunteer with this status: check whether email is registered with the workspace. If status changed, and volunteer joined the workspace, then add to channels according to role entered and update status in the SlackPollingStatus  table to “done”.  
__Link added to email via the invitation_link.json file. The link can be used by up to 2000 people. When the users cap of 2000 is exhausted a new link should be generated according to the below example:__

![From invitation link creation guide of slack](/images/invitation_link.png)

## Architecture description:
__ERD__  

![ERD](/images/She_codes_volunteer_account_manager.png)

__High level architecture__  

![High level architecture](/images/SheCodes_user_manager_Diagram.jpg)

__classes - class diagram__  

![classes - class diagram](/images/classes_class diagram.png)

