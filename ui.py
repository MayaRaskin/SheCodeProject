from shecodes_user_manager.db_manager import DbManager
from shecodes_user_manager.db_manager import Volunteer
from shecodes_user_manager.slack_api_helper import SlackApiHelper
from shecodes_user_manager.slack_api_helper import WorkspaceInvitation
from shecodes_user_manager.polling_ui_mutex import PollingUiMutex
import json


class UI(object):
    def __init__(self):
        print("To update an exist volunteer - enter mail and fill in the desired fields. \n Enter 0 to keep field unchanged")
        self._volunteer_id = "17" #input("Insert volunteer ID:")
        self._mail = "maximus.raskin@gmail.com "  #input("Insert mail:")
        self._first_name = "d"
        self._last_name = "r"
        self._area = "haifa" #input("Insert area:")
        self._district = "north" #input("Insert district:")
        self._branch = "technion" #input("Insert branch:")
        self._role = "district_manager" #input("Insert role:")
        self._db_manager = DbManager()
        self.slack_api_helper = None

    # def updated_volunteer(self):
    #     volunteer = Volunteer(mail=self._mail, area=self._area, district=self._district, branch=self._branch, role=self._role,
    #               handled=0)
    #     return self._db_manager.update_volunteer(volunteer)

    def insert_new_volunteer(self):
        volunteer = Volunteer(volunteer_id = self._volunteer_id, mail=self._mail, first_name=self._first_name, last_name=self._last_name, area=self._area, district=self._district, branch=self._branch, role=self._role)
                  # handled=0)
        return self._db_manager.insert_volunteer(volunteer)

    def get_slack_api_helper(self):
        if self.slack_api_helper is None:
            with open("shecodes_user_manager\slack_token.json", "rb") as fp:
                my_tokens = json.load(fp)
            self.slack_api_helper = SlackApiHelper(my_tokens["slack_signing_secret"], my_tokens["slack_bot_token"],
                                              my_tokens["slack_user_token"])
        return self.slack_api_helper

    def is_user_registered_to_slack_workspace(self, mail, volunteer_id):
        slack_api_helper = self.get_slack_api_helper()
        response = slack_api_helper.is_mail_in_workspace(mail, volunteer_id)
        return response

    def add_user_to_channels(self):
        slack_api_helper = self.get_slack_api_helper()
        self.slack_channels_for_volunteer = self._db_manager.get_slack_channels_for_volunteer(self.volunteer_id_update_or_inserted)
        slack_api_helper.adding_member_to_channel(self.slack_channels_for_volunteer)

    def user_choose_table(self):
        choices = {'1': 'Insert new volunteer',
                   '2': 'Update volunteer data',
                   '3': 'Delete volunteer'}
        choices_to_functions = {'1': self.insert_new_volunteer}
        print(choices)
        self._choice = '1'# input('Insert choice number:')
        self.polling_ui_mutex = PollingUiMutex("UI")
        with self.polling_ui_mutex:
            commit_result = choices_to_functions[self._choice]()
            if commit_result:
                print(choices[self._choice] + " succeed")
                self.volunteer_id_update_or_inserted = self._db_manager.get_volunteer_data_id()
                mail_in_workspace_respond = self.is_user_registered_to_slack_workspace(self._mail, self.volunteer_id_update_or_inserted)
                if mail_in_workspace_respond:
                    self.add_user_to_channels()
                else:
                    print("Sending invitation...")
                    workspace_invitation = WorkspaceInvitation(self._mail)
                    workspace_invitation.send_invitation_mail()
                    self._db_manager.insert_new_volunteer_to_slack_user_polling_table(self.volunteer_id_update_or_inserted)
                    print('add in topic to sub queue for not in workspace')
                    '''send mail'''
                    '''add in topic to sub queue for not in workspace '''
            else:
                print(choices[self._choice] + " failed - volunteer id is already in system")


def main():
    start_ui = UI()
    start_ui.user_choose_table()


if __name__ == "__main__":
    main()
