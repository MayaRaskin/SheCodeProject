from shecodes_user_manager.db_manager import DbManager
from shecodes_user_manager.db_manager import Volunteer
from shecodes_user_manager.slack_api_helper import SlackApiHelper
from shecodes_user_manager.slack_api_helper import WorkspaceInvitation
from shecodes_user_manager.polling_ui_mutex import PollingUiMutex
from shecodes_user_manager import logging_manager


class UI(object):
    def __init__(self):
        print("To update an exist volunteer - enter volunteer id + first&last name and fill in the desired fields. \n Enter 0 to keep field unchanged")
        self._volunteer_id = "15" #input("Insert volunteer ID:")
        self._mail = "maximus.raskin@gmail.com "  #input("Insert mail:")
        self._first_name = "d"
        self._last_name = "r"
        self._area = "0" #input("Insert area:")
        self._district = "0" #input("Insert district:")
        self._branch = "0" #input("Insert branch:")
        self._role = "area_manager" #input("Insert role:")
        self._db_manager = DbManager()
        self.slack_api_helper = SlackApiHelper.create()

    def insert_new_volunteer(self):
        volunteer = Volunteer(volunteer_id = self._volunteer_id, mail=self._mail, first_name=self._first_name, last_name=self._last_name, area=self._area, district=self._district, branch=self._branch, role=self._role)
        return self._db_manager.insert_volunteer(volunteer)

    def update_volunteer_data(self):
        volunteer = Volunteer(volunteer_id = self._volunteer_id, mail=self._mail, first_name=self._first_name, last_name=self._last_name, area=self._area, district=self._district, branch=self._branch, role=self._role)
        return self._db_manager.update_volunteer_data(volunteer)

    def is_user_registered_to_slack_workspace(self, mail, volunteer_id):
        response = self.slack_api_helper.is_mail_in_workspace(mail, volunteer_id)
        return response

    def add_user_to_channels(self):
        self.slack_channels_for_volunteer = self._db_manager.get_slack_channels_for_volunteer(self.volunteer_id_update_or_inserted)
        self.slack_api_helper.adding_member_to_channel(self.slack_channels_for_volunteer)

    def user_choose_table(self):
        choices = {'1': 'Insert new volunteer',
                   '2': 'Update volunteer data',
                   '3': 'Delete volunteer'}
        choices_to_functions = {'1': self.insert_new_volunteer,
                                '2': self.update_volunteer_data}
        print(choices)
        self._choice = '2'# input('Insert choice number:')
        self.polling_ui_mutex = PollingUiMutex("UI")
        with self.polling_ui_mutex:
            commit_result = choices_to_functions[self._choice]()
            if commit_result:
                print(choices[self._choice] + " succeed")
                logging_manager.logger.info(choices[self._choice] + " succeed")
                self.volunteer_id_update_or_inserted = self._db_manager.get_volunteer_data_id()
                mail_in_workspace_respond = self.is_user_registered_to_slack_workspace(self._mail, self.volunteer_id_update_or_inserted)
                if mail_in_workspace_respond:
                    self.add_user_to_channels()
                else:
                    print("Sending invitation...")
                    logging_manager.logger.info("Sending invitation...")
                    workspace_invitation = WorkspaceInvitation(self._mail)
                    workspace_invitation.send_invitation_mail()
                    self._db_manager.insert_new_volunteer_to_slack_user_polling_table(self.volunteer_id_update_or_inserted)
            else:
                logging_manager.logger.error(choices[self._choice] + " failed - volunteer id is already in system")
                print(choices[self._choice] + " failed - volunteer id is already in system")


def main():
    logging_manager.init_logger("UI")
    start_ui = UI()
    start_ui.user_choose_table()


if __name__ == "__main__":
    main()
