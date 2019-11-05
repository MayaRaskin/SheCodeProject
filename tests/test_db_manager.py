import pytest
import shutil
import os
from shecodes_user_manager.db_manager import DbManager, Volunteer, DbManagerException
from shecodes_user_manager.logging_manager import init_logger
import sqlite3


class TestDbManager:

    @classmethod
    def setup_class(cls):
        init_logger("test_db_manager.log")

    def setup_method(self, test_method):
        original_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shecodes_user_manager",
                                        "she_codes_account_manager_db_v1.db")

        self.test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "she_codes_account_manager_db_v1_tests.db")

        shutil.copy(original_db_path, self.test_db_path)
        self.manager = DbManager(self.test_db_path)

    def teardown_method(self, test_method):
        # self.db_manager.close_db()
        os.unlink(self.test_db_path)

    def test_get_channels_for_volunteer(self):
        with self.manager:
            sandy_the_dog = Volunteer(43, "sandy@ear.com", "Sandy", "Raskin", "haifa", "north", "technion",
                                      "district_manager")
            self.manager.insert_volunteer(sandy_the_dog)
            volunteer_data_id = self.manager.get_volunteer_data_id()
            channels = self.manager.get_slack_channels_for_volunteer(volunteer_data_id)
            assert (len(channels) > 0)

    def test_insert_volunteer_illegal_location(self):
        with self.manager:
            sandy_the_dog = Volunteer(42, "sandy@ear.com", "Sandy", "Raskin", "North", "Harish", "Smokey", "district_manager")
            result = self.manager.insert_volunteer(sandy_the_dog)
            assert not result

    def test_insert_volunteer_illegal_role(self):
        with self.manager:
            sandy_the_dog = Volunteer(42, "sandy@ear.com", "Sandy", "Raskin", "haifa", "north", "technion", "Doctor")
            result = self.manager.insert_volunteer(sandy_the_dog)
            assert not result

    def test_entering_exist_volunteer_twice(self):
        with self.manager:
            sandy_the_dog = Volunteer(42, "sandy@ear.com", "Sandy", "Raskin", "haifa", "north", "technion", "district_manager")
            result = self.manager.insert_volunteer(sandy_the_dog)
            with pytest.raises(DbManagerException):
                result = self.manager.insert_volunteer(sandy_the_dog)

    def test_view_volunteer_data(self):
        with self.manager:
            sandy_the_dog = Volunteer(24, "0", "0", "0", "0", "0", "0", "0")
            view_data_dict = self.manager.view_volunteer_data(sandy_the_dog)
            for key in view_data_dict:
                if (type(view_data_dict[key]) == int):
                    assert (view_data_dict[key] != 0)
                else:
                    assert (len(view_data_dict[key]) > 0)

    def test_view_not_exist_volunteer_data(self):
        with self.manager:
            sandy_the_dog = Volunteer(100, "0", "0", "0", "0", "0", "0", "0")
            with pytest.raises(DbManagerException):
                view_data_dict = self.manager.view_volunteer_data(sandy_the_dog)
