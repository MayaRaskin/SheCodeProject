import sqlite3
import os
from datetime import date


class Volunteer(object):
    def __init__(self, volunteer_id, mail, first_name, last_name, area, district, branch, role):  # handled, channel):
        """

        :rtype: object
        """
        self._volunteer_id = volunteer_id
        self._mail = mail
        self._first_name = first_name
        self._last_name = last_name
        self._area = area
        self._district = district
        self._branch = branch
        self._role = role

    @property
    def volunteer_id(self):
        return self._volunteer_id

    @property
    def mail(self):
        return self._mail

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

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

    def get_my_values(self, values_list):
        my_members = dir(self)
        result = {}
        for value in values_list:
            value_to_member = "_" + value
            for member in my_members:
                if member.startswith(value_to_member):
                    result[value] = getattr(self, member)
        return result


class DbManagerException(Exception):
    pass


class DbManager(object):

    def __init__(self, path=None):
        if path is None:
            self._path_db = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "she_codes_account_manager_db_v1.db")
        else:
            self._path_db = path
        self.conn = sqlite3.connect(self._path_db)

    def get_slack_channels_for_volunteer(self, volunteer_data_id_add):
        if self.conn is None:
            self.conn = sqlite3.connect(self._path_db)
        cur = self.conn.cursor()
        sql = 'SELECT slack_channel FROM LocationAndRoleOfVolunteer ' \
              'INNER JOIN RoleToSlackChannel ON RoleToSlackChannel.role_id = ' \
              'LocationAndRoleOfVolunteer.role_id ' \
              'INNER JOIN SheCodesSlackChannels ON RoleToSlackChannel.slack_channel_id = ' \
              'SheCodesSlackChannels.slack_channel_id ' \
              'WHERE (volunteer_data_id = ?)'
        cur.execute(sql, (volunteer_data_id_add,))
        db_result = cur.fetchall()
        self.close_db()
        # volunter_list = []
        # for row in db_result:
        #     volunteers_list.append(
        #         Volunteer(mail=row[0], first_name=row[1], last_name=row[2], area=row[1], district=row[2], branch=row[3],
        #                   role=row[4],
        #                   handled=row[5], channel=row[7]))
        return [channel[0] for channel in db_result]

    def role_to_role_id(self, role):
        cur = self.conn.cursor()
        sql = 'SELECT role_id FROM SheCodesRoles WHERE (role = ?)'

        cur.execute(sql, (role,))
        db_result = cur.fetchall()
        if len(db_result) == 0:
            raise DbManagerException("no such role - check details")

        return db_result[0][0]

    def close_db(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def insert_new_volunteer_to_slack_user_polling_table(self, volunteer_data_id):
        if self.conn is None:
            self.conn = sqlite3.connect(self._path_db)
        with self.conn:
            cur = self.conn.cursor()
            sql = 'Insert INTO SlackPollingStatus(volunteer_data_id, status, create_date) VALUES(?,?,CURRENT_TIMESTAMP)'
            cur.execute(sql, [volunteer_data_id, "NOT_IN_WORKSPACE"])
        self.close_db()

    def get_volunteer_to_check_new_status_on_slack(self):
        '''
        retrieve mail list of all volunteer which currently note as "NOT_IN_WORKSPACE"
        :return: list of volunteers mails.
        '''
        if self.conn is None:
            self.conn = sqlite3.connect(self._path_db)
        cur = self.conn.cursor()
        sql = 'SELECT SlackPollingStatus.volunteer_data_id,mail FROM SlackPollingStatus' \
              ' INNER JOIN VolunteerData ON VolunteerData.volunteer_data_id = SlackPollingStatus.volunteer_data_id' \
              ' WHERE (status = ?)'
        cur.execute(sql, ("NOT_IN_WORKSPACE",))
        db_result = cur.fetchall()
        volunteer_mail_check_status_list = [mail[1] for mail in db_result]
        volunteer_id_check_status_list = [volunteer[0] for volunteer in db_result]
        self.close_db()
        return volunteer_mail_check_status_list, volunteer_id_check_status_list

    def update_slack_user_status(self, volunteer_data_id_list, status):
        '''
        :param volunteer_data_id_list: list of volunteer which their status needed to be changed
        :param status: The status message to update
        '''
        for volunteer_data_id in volunteer_data_id_list:
            try:
                if self.conn is None:
                    self.conn = sqlite3.connect(self._path_db)
                cur = self.conn.cursor()
                sql = """UPDATE SlackPollingStatus SET status = ? WHERE volunteer_data_id = ?"""
                cur.execute(sql, (status, volunteer_data_id))
                self.conn.commit()
            # except sqlite3.Error as error:
            #     print("failed to update SlackPollingStatus table")
            finally:
                self.close_db()

    def get_location_id(self, values_list):
        cur = self.conn.cursor()
        sql = 'SELECT location_id FROM Location WHERE ((area = ?) AND (district = ?) AND (branch = ?))'

        cur.execute(sql, (values_list['area'], values_list['district'], values_list['branch'],))

        db_result = cur.fetchall()
        if len(db_result) == 0:
            raise DbManagerException("no such location - check details")

        return db_result[0][0]

    def get_volunteer_data_id(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self._path_db)
        cur = self.conn.cursor()
        cur.execute('SELECT volunteer_data_id FROM VolunteerData WHERE volunteer_data_id = (SELECT MAX(volunteer_data_id) '
                    'FROM VolunteerData)')
        db_result = cur.fetchall()
        return db_result[0][0]

    def insert_into_volunteer_data_table(self, volunteer):
        if self.conn is None:
            self.conn = sqlite3.connect(self._path_db)
        try:
            with self.conn:
                cur = self.conn.cursor()
                values_to_get = ["volunteer_id", "mail", "first_name", "last_name"]
                sql = f'Insert INTO VolunteerData({", ".join(values_to_get)},create_date) VALUES(?,?,?,?,CURRENT_TIMESTAMP)'
                values_as_dict = volunteer.get_my_values(values_to_get)
                cur.execute(sql, list(values_as_dict.values()))
        except sqlite3.IntegrityError:
            print('Can not update table volunteer id is already in db')

    def insert_volunteer(self, volunteer: Volunteer):
        self.insert_into_volunteer_data_table(volunteer)
        self._last_volunteer_id_add = self.get_volunteer_data_id()
        try:
            with self.conn:
                cur = self.conn.cursor()
                # volunteer_id_cur = volunteer.get_my_values(['VolunteerDataId'])['VolunteerDataId']
                location_id_cur = self.get_location_id(volunteer.get_my_values(['area', 'district', 'branch']))
                role_id_cur = self.role_to_role_id(volunteer.get_my_values(['role'])['role'])
                sql1 = 'Insert INTO LocationAndRoleOfVolunteer(volunteer_data_id, location_id, role_id) VALUES(?,?,?)'
                cur.execute(sql1, [self._last_volunteer_id_add, location_id_cur, role_id_cur])
            return True
        except sqlite3.IntegrityError:
            print('can not update table location_and_role_of_volunteer - volunteer id is already in db')
            return False
        finally:
            self.close_db()
    # def update_volunteer(self, volunteer: Volunteer):
    #     try:
    #         with self.conn:
