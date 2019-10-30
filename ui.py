from shecodes_user_manager.db_manager import DbManager
from shecodes_user_manager.db_manager import Volunteer
from shecodes_user_manager.slack_api_helper import SlackApiHelper
from shecodes_user_manager.slack_api_helper import WorkspaceInvitation
from shecodes_user_manager.polling_ui_mutex import PollingUiMutex
from shecodes_user_manager import logging_manager
import sys

class UI(object):
    def __init__(self):
        print(
            '==>To update an exist volunteer - enter volunteer id + first&last name and fill in the desired fields. \n '
            '(Enter 0 to keep field unchanged). \n ==>in order to view existing volunteer type only volunteer id. \n')
        self._volunteer_id = input("Insert volunteer ID:")
        self._mail = input("Insert mail:")
        self._first_name = input("First name:")
        self._last_name = input("Last name:")
        self._area = input("Insert area:")
        self._district = input("Insert district:")
        self._branch = input("Insert branch:")
        self._role = input("Insert role:")
        self._db_manager = DbManager()
        self.slack_api_helper = SlackApiHelper.create()

    def insert_new_volunteer(self):
        volunteer = Volunteer(volunteer_id = self._volunteer_id, mail=self._mail, first_name=self._first_name, last_name=self._last_name, area=self._area, district=self._district, branch=self._branch, role=self._role)
        return self._db_manager.insert_volunteer(volunteer)

    def update_volunteer_data(self):
        volunteer = Volunteer(volunteer_id = self._volunteer_id, mail=self._mail, first_name=self._first_name, last_name=self._last_name, area=self._area, district=self._district, branch=self._branch, role=self._role)
        return self._db_manager.update_volunteer_data(volunteer)

    def view_volunteer_data(self):
        volunteer = Volunteer(volunteer_id = self._volunteer_id, mail=self._mail, first_name=self._first_name, last_name=self._last_name, area=self._area, district=self._district, branch=self._branch, role=self._role)
        return self._db_manager.view_volunteer_data(volunteer)

    def is_user_registered_to_slack_workspace(self, mail, volunteer_id):
        response = self.slack_api_helper.is_mail_in_workspace(mail, volunteer_id)
        return response

    def newly_added_volunteer_to_slack(self, time_period):
        polling_volunteer_id_list = self._db_manager.get_polling_status_counter(time_period)
        all_volunteer_id_in_period_list = self._db_manager.get_joined_volunteer_counter(time_period)
        newly_added_list = []
        for volunteer_id in all_volunteer_id_in_period_list:
            counter = 1
            for polling_volunteer_id in polling_volunteer_id_list:
                if volunteer_id == polling_volunteer_id:
                    counter = 0
                    break
            if counter == 1:
                newly_added_list.append(volunteer_id)
        return newly_added_list

    def add_user_to_channels(self):
        self.slack_channels_for_volunteer = self._db_manager.get_slack_channels_for_volunteer(self.volunteer_id_update_or_inserted)
        self.slack_api_helper.adding_member_to_channel(self.slack_channels_for_volunteer)

    def user_choose_table(self):
        choices = {'1': 'Insert new volunteer',
                   '2': 'Update volunteer data',
                   '3': 'View volunteer data',
                   '4': 'Check how many volunteers added to slack in period of time YYYY-MM-DD'}
        choices_to_functions = {'1': self.insert_new_volunteer,
                                '2': self.update_volunteer_data,
                                '3': self.view_volunteer_data,
                                '4': self.newly_added_volunteer_to_slack}
        print(choices)
        self._choice = input('Insert choice number:')
        with self._db_manager:
            if self._choice == '3':
                data_to_view = choices_to_functions[self._choice]()
                if data_to_view is None:
                    logging_manager.logger.error("volunteer data ID insert isn't in system please check")
                else:
                    for item in data_to_view:
                        print("{} :  {}".format(item, data_to_view[item]))
            if self._choice == '4':
                self._start_time_for_analysis = input(
                    "For maintenance only use - Insert data to know how many volunteer "
                    "joined slack in period of time YYYY-MM-DD")
                data_to_view = choices_to_functions[self._choice](self._start_time_for_analysis)
                print("How many volunteer joined slack workspace from {} : {}".format(self._start_time_for_analysis, len(data_to_view)))
            if self._choice != '4' and self._choice != '3':
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
                            volunteer_exist_in_polling_table = self._db_manager.volunteer_in_polling_table_check(self.volunteer_id_update_or_inserted)
                            if not volunteer_exist_in_polling_table:
                                self._db_manager.insert_new_volunteer_to_slack_user_polling_table(self.volunteer_id_update_or_inserted)
                            else:
                                logging_manager.logger.info("volunteer already in polling table")
                    else:
                        logging_manager.logger.error(choices[self._choice] + " failed - please check logs to verify the problem")
                        print(choices[self._choice] + " failed - please check logs to verify the problem")


def main():
    logging_manager.init_logger("She_codes_UI.log")
    start_ui = UI()
    start_ui.user_choose_table()


if __name__ == "__main__":
    main()
