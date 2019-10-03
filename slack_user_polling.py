import time
from shecodes_user_manager.db_manager import DbManager
from shecodes_user_manager.slack_api_helper import SlackApiHelper
from shecodes_user_manager.polling_ui_mutex import PollingUiMutex

def polling_check_data(manager, slack_api_helper):
    mails_to_check, volunteer_data_ids = manager.get_volunteer_to_check_new_status_on_slack()
    for (mail, volunteer_id) in zip(mails_to_check, volunteer_data_ids):
        mail_in_workspace_respond = slack_api_helper.is_mail_in_workspace(mail, volunteer_id)
        if mail_in_workspace_respond:
            slack_channels_for_volunteer = manager.get_slack_channels_for_volunteer(volunteer_id)
            slack_api_helper.adding_member_to_channel(slack_channels_for_volunteer)
            print("volunteer" + str(volunteer_id) + "-" + mail + "added to channels" + str(slack_channels_for_volunteer))
            manager.update_slack_user_status([volunteer_id], "ADDED_TO_CHANNELS")

def main():
    manager = DbManager()
    slack_api_helper = SlackApiHelper.create()
    while True:
        polling_ui_mutex = PollingUiMutex("polling")
        with polling_ui_mutex:
            polling_check_data(manager, slack_api_helper)
        print("polling...")
        time.sleep(5)


if __name__ == "__main__":
    main()
