from shecodes_user_manager.db_manager import DbManager
from shecodes_user_manager.db_manager import Volunteer


class UI(object):
    def __init__(self):
        print("To update an exist volunteer - enter mail and fill in the desired fields. \n Enter 0 to keep field unchanged")
        self._mail = "g"  #input("Insert mail:")
        self._area = "b" #input("Insert area:")
        self._district = "c" #input("Insert district:")
        self._branch = "d" #input("Insert branch:")
        self._role = "f" #input("Insert role:")
        self._db_manager = DbManager()

    # def updated_volunteer(self):
    #     volunteer = Volunteer(mail=self._mail, area=self._area, district=self._district, branch=self._branch, role=self._role,
    #               handled=0)
    #     return self._db_manager.update_volunteer(volunteer)

    def insert_new_volunteer(self):
        volunteer = Volunteer(mail=self._mail, area=self._area, district=self._district, branch=self._branch, role=self._role,
                  handled=0)
        return self._db_manager.insert_volunteer(volunteer)

    def user_choose_table(self):
        choices = {'1': 'Insert new volunteer',
                   '2': 'Update volunteer data',
                   '3': 'Delete volunteer'}
        choices_to_functions = {'1': self.insert_new_volunteer}
        print(choices)
        self._choice = '1'# input('Insert choice number:')
        commit_result = choices_to_functions[self._choice]()
        if commit_result:
            print(choices[self._choice] + " succeed")
        else:
            print(choices[self._choice] + " failed - mail is already in system")


def main():
    start_ui = UI()
    start_ui.user_choose_table()


if __name__ == "__main__":
    main()
