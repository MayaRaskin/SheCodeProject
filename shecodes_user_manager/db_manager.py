import sqlite3


class Volunteer(object):
    def __init__(self, mail, area, district, branch, role):
        self._mail = mail
        self._area = area
        self._district = district
        self._branch = branch
        self._role = role

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



class DbManager(object):

    def __init__(self, path):
        self._path_db = path
        self.conn = sqlite3.connect(self._path_db)
        self.cur = self.conn.cursor()

    def volunteer_to_handle(self):
        self.cur.execute('SELECT * FROM slack_volunteer_data WHERE (handled = 0)')
        db_result = self.cur.fetchall()

        volunteers_list = []

        for row in db_result:
            volunteers_list.append(Volunteer(mail=row[0], area=row[1], district=row[2], branch=row[3], role=row[4]))

        return volunteers_list