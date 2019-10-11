import slack_user_polling
from shecodes_user_manager.db_manager import DbManager, Volunteer
import shutil
import os
import sqlite3
import pytest

class TestSlackUserPolling(object):

    def setup_method(self, test_method):
        original_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shecodes_user_manager",
                                        "she_codes_account_manager_db_v1.db")

        self.test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "she_codes_account_manager_db_v1_tests.db")

        shutil.copy(original_db_path, self.test_db_path)
        self.db_manager = DbManager(self.test_db_path)

    def teardown_method(self, test_method):
        # self.db_manager.close_db()
        os.unlink(self.test_db_path)

    def test_insert_SlackPollingStatus(self):
        with self.db_manager:
            volunteer_data = Volunteer(43, "sandy@ear.com", "Sandy", "Raskin", "haifa", "north", "technion", "district_manager")
            self.db_manager.insert_into_volunteer_data_table(volunteer_data)
            volunteer_data_id = self.db_manager.get_volunteer_data_id()
            self.db_manager.insert_new_volunteer_to_slack_user_polling_table(volunteer_data_id)
            cur = self.db_manager.conn.cursor()
            sql = 'SELECT * FROM SlackPollingStatus'
            cur.execute(sql)
            db_result = cur.fetchall()
            assert (db_result[-1][0] == volunteer_data_id)

    def test_SlackPollingStatus_change_status(self):
        with self.db_manager:
            volunteer_data_id = 1
            self.db_manager.insert_new_volunteer_to_slack_user_polling_table(volunteer_data_id)
            self.db_manager.update_slack_user_status([volunteer_data_id], "YOHOO")
            cur = self.db_manager.conn.cursor()
            sql = 'SELECT * FROM SlackPollingStatus'
            cur.execute(sql)
            db_result = cur.fetchall()
            assert (db_result[-1][1] == "YOHOO")