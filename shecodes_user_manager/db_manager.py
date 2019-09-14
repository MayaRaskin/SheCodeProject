import sqlite3
import os

class Volunteer(object):
    def __init__(self, mail, area, district, branch, role, handled):
        self._mail = mail
        self._area = area
        self._district = district
        self._branch = branch
        self._role = role
        self._handled = handled

    @property
    def mail(self):
        return self._mail

    @property
    def area(self):
        return self._area

    @property
    def district(self):
        return self._district

    @property
    def branch(self):
        return self._branch

    @property
    def role(self):
        return self._role

    @property
    def handled(self):
        return self._handled

    def get_keys_for_sql(self):
        my_members = dir(self)
        result = []
        for member in my_members:
            if member.startswith("_") and not member.startswith("__"):
                result.append(member[1:]) # drop the '_' prefix

        return ", ".join(result)

    def get_place_holders_for_sql(self):
        result = []
        for i in range(len(self.get_values_for_sql())):
            result.append('?')
        return ", ".join(result)

    def get_values_for_sql(self):
        my_members = dir(self)
        result = []
        for member in my_members:
            if member.startswith("_") and not member.startswith("__"):
                result.append(getattr(self, member))
        return result


class DbManager(object):

    def __init__(self, path=None):
        if path is None:
            self._path_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shecodes_account_manager_db.db")
        else:
            self._path_db = path
        self.conn = sqlite3.connect(self._path_db)

    def volunteer_to_handle(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM slack_volunteer_data WHERE (handled = 0)')
        db_result = cur.fetchall()

        volunteers_list = []

        for row in db_result:
            volunteers_list.append(Volunteer(mail=row[0], area=row[1], district=row[2], branch=row[3], role=row[4],
                                             handled=row[5]))
        return volunteers_list

    def insert_volunteer(self, volunteer: Volunteer):
        try:
            with self.conn:
                cur = self.conn.cursor()
                sql = f'Insert INTO slack_volunteer_data({volunteer.get_keys_for_sql()}) ' \
                    f'VALUES({volunteer.get_place_holders_for_sql()})'
                cur.execute(sql, volunteer.get_values_for_sql())
                # self.conn.close()
                return True
        except sqlite3.IntegrityError:
            return False
    # def update_volunteer(self, volunteer: Volunteer):
    #     try:
    #         with self.conn:





