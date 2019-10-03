import json

from shecodes_user_manager.db_manager import DbManager
from shecodes_user_manager.slack_api_helper import WorkspaceInvitation, SlackApiHelper

def main():
    # slack_invitation_mail = WorkspaceInvitation()
    # slack_invitation_mail.send_invitation_mail()
    with open("shecodes_user_manager\slack_token.json", "rb") as fp:
        my_tokens = json.load(fp)
    slack_api_helper = SlackApiHelper(my_tokens["slack_signing_secret"], my_tokens["slack_bot_token"],
                                       my_tokens["slack_user_token"])
    '''some function connected to kafka topic and retrieve volunteer_id '''
    # slack_api_helper.get_channel_user_to_add()
    # Once we have our event listeners configured, we can start the
    # Flask server with the default `/events` endpoint on port 3000
    db_manager = DbManager()

    slack_api_helper.start_server()


if __name__ == "__main__":
    main()
