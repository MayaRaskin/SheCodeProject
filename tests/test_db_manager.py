import pytest
import shutil
import os
from shecodes_user_manager.db_manager import DbManager, Volunteer, DbManagerException

class TestDbManager:

    def setup_method(self, test_method):
        original_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shecodes_user_manager",
                                        "she_codes_account_manager_db_v1.db")

        self.test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "she_codes_account_manager_db_v1_tests.db")

        shutil.copy(original_db_path, self.test_db_path)
        self.manager = DbManager(self.test_db_path)

    def teardown_method(self, test_method):
        # self.manager.close_db()
        os.unlink(self.test_db_path)

    def test_get_channels_for_volunteer(self):
        sandy_the_dog = Volunteer(43, "sandy@ear.com", "Sandy", "Raskin", "haifa", "north", "technion", "district_manager")
        self.manager.insert_volunteer(sandy_the_dog)
        volunteer_data_id = self.manager.get_volunteer_data_id()
        channels = self.manager.get_slack_channels_for_volunteer(volunteer_data_id)
        assert (len(channels) > 0)

    def test_insert_volunteer_illegal_location(self):
        sandy_the_dog = Volunteer(42, "sandy@ear.com", "Sandy", "Raskin", "North", "Harish", "Smokey", "Doctor")
        with pytest.raises(DbManagerException):
             self.manager.insert_volunteer(sandy_the_dog)

    def test_insert_volunteer_illegal_role(self):
        sandy_the_dog = Volunteer(42, "sandy@ear.com", "Sandy", "Raskin", "haifa", "north", "technion", "Doctor")
        with pytest.raises(DbManagerException):
            self.manager.insert_volunteer(sandy_the_dog)







