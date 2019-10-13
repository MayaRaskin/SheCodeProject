import sqlite3
import os
from datetime import date
from . import logging_manager


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

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        logging_manager.logger.exception(self)

class DbManager(object):

    def __init__(self, path=None):
        if path is None:
            self._path_db = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "she_codes_account_manager_db_v1.db")
        else:
            self._path_db = path
        self.conn = sqlite3.connect(self._path_db)

    def __enter__(self):
        self.conn = sqlite3.connect(self._path_db)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_db()

    def get_slack_channels_for_volunteer(self, volunteer_data_id_add):
        with self.conn:
            cur = self.conn.cursor()
            sql = 'SELECT slack_channel FROM LocationAndRoleOfVolunteer ' \
                  'INNER JOIN RoleToSlackChannel ON RoleToSlackChannel.role_id = ' \
                  'LocationAndRoleOfVolunteer.role_id ' \
                  'INNER JOIN SheCodesSlackChannels ON RoleToSlackChannel.slack_channel_id = ' \
                  'SheCodesSlackChannels.slack_channel_id ' \
                  'WHERE (volunteer_data_id = ?)'
            cur.execute(sql, (volunteer_data_id_add,))
            db_result = cur.fetchall()

        return [channel[0] for channel in db_result]

    def get_current_location_id(self, volunteer_data_id_to_update):
        with self.conn:
            cur = self.conn.cursor()
            sql = 'SELECT location_id FROM LocationAndRoleOfVolunteer WHERE (volunteer_data_id = ?)'
            cur.execute(sql, (volunteer_data_id_to_update,))
            db_result = cur.fetchall()
        return db_result[0][0]

    def get_current_role_id(self, volunteer_data_id_to_update):
        with self.conn:
            cur = self.conn.cursor()
            sql = 'SELECT role_id FROM LocationAndRoleOfVolunteer WHERE (volunteer_data_id = ?)'
            cur.execute(sql, (volunteer_data_id_to_update,))
            db_result = cur.fetchall()
        return db_result[0][0]

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
        with self.conn:
            cur = self.conn.cursor()
            sql = 'Insert INTO SlackPollingStatus(volunteer_data_id, status, create_date) VALUES(?,?,CURRENT_TIMESTAMP)'
            cur.execute(sql, [volunteer_data_id, "NOT_IN_WORKSPACE"])

    def get_volunteer_to_check_new_status_on_slack(self):
        '''
        retrieve mail list of all volunteer which currently note as "NOT_IN_WORKSPACE"
        :return: list of volunteers mails.
        '''
        cur = self.conn.cursor()
        sql = 'SELECT SlackPollingStatus.volunteer_data_id,mail FROM SlackPollingStatus' \
              ' INNER JOIN VolunteerData ON VolunteerData.volunteer_data_id = SlackPollingStatus.volunteer_data_id' \
              ' WHERE (status = ?)'
        cur.execute(sql, ("NOT_IN_WORKSPACE",))
        db_result = cur.fetchall()
        volunteer_mail_check_status_list = [mail[1] for mail in db_result]
        volunteer_id_check_status_list = [volunteer[0] for volunteer in db_result]
        return volunteer_mail_check_status_list, volunteer_id_check_status_list

    def update_volunteer_data(self, volunteer: Volunteer):
        values_to_get = ["volunteer_id", "first_name", "last_name", "mail"]
        if (len(volunteer.volunteer_id) > 0) and (len(volunteer.first_name) > 0) and (len(volunteer.last_name) > 0):
            if volunteer.mail != "0":
                self.update_volunteer_mail(volunteer)
                logging_manager.logger.info(f'mail updated successfully to {volunteer.mail}')
            volunteer_data_id_to_update = self.get_volunteer_data_id_to_update(volunteer.volunteer_id)
            try:
                with self.conn:
                    role_id_cur = 0
                    cur = self.conn.cursor()
                    # volunteer_id_cur = volunteer.get_my_values(['VolunteerDataId'])['VolunteerDataId']
                    location_id_cur = self.get_current_location_id(volunteer_data_id_to_update)
                    location_id_new = self.new_location_id_to_update(location_id_cur, volunteer.get_my_values(['area', 'district', 'branch']))
                    if location_id_cur != location_id_new:
                        location_to_update = location_id_new
                    else:
                        location_to_update = location_id_cur
                    if volunteer.role != '0':
                        role_id_cur = self.role_to_role_id(volunteer.role)
                    if (location_id_cur != location_id_new) or (role_id_cur != 0):
                        sql1 = 'UPDATE LocationAndRoleOfVolunteer SET location_id = ?, role_id = ?, ' \
                               'modified_date = CURRENT_TIMESTAMP WHERE volunteer_data_id = ?'
                        cur.execute(sql1, (location_to_update, role_id_cur, volunteer_data_id_to_update))
                    else:
                        logging_manager.logger.info('no updates preformed in location nor role')
                return True
            except sqlite3.IntegrityError:
                logging_manager.logger.error(
                    "Some error occurred can't update location_and_role_of_volunteer table")
                return False

    def update_volunteer_mail(self, volunteer):
        try:
            with self.conn:
                cur = self.conn.cursor()
                values_to_get = ["volunteer_id", "mail", "first_name", "last_name"]
                sql = """UPDATE VolunteerData SET mail = ?, modified_date = CURRENT_TIMESTAMP WHERE volunteer_id = ? AND first_name = ? AND last_name = ?"""
                values_as_dict = volunteer.get_my_values(values_to_get)
                cur.execute(sql, (values_as_dict["mail"], values_as_dict["volunteer_id"], values_as_dict["first_name"], values_as_dict["last_name"]))
        except sqlite3.IntegrityError:
            logging_manager.logger.error("Can not update table volunteer_id + first&last name doesn't exist on DB")


    def update_slack_user_status(self, volunteer_data_id_list, status):
        '''
        :param volunteer_data_id_list: list of volunteer which their status needed to be changed
        :param status: The status message to update
        '''
        for volunteer_data_id in volunteer_data_id_list:
            try:
                with self.conn:
                    cur = self.conn.cursor()
                    sql = """UPDATE SlackPollingStatus SET status = ? WHERE volunteer_data_id = ?"""
                    cur.execute(sql, (status, volunteer_data_id))
            except sqlite3.Error as error:
                logging_manager.logger.error("failed to update SlackPollingStatus table")

    def get_location_id(self, values_list):
        with self.conn:
            cur = self.conn.cursor()
            sql = 'SELECT location_id FROM Location WHERE ((area = ?) AND (district = ?) AND (branch = ?))'

            cur.execute(sql, (values_list['area'], values_list['district'], values_list['branch'],))

            db_result = cur.fetchall()
            if len(db_result) == 0:
                raise DbManagerException(f"no such location - value_list = {values_list}")

        return db_result[0][0]

    def new_location_id_to_update(self, location_id_curr, value_list):
        with self.conn:
            cur = self.conn.cursor()
            sql = 'SELECT area, district, branch FROM Location WHERE location_id = ?'
            cur.execute(sql, (location_id_curr,))
            db_result = cur.fetchall()
            new_value_list = {}
            cur_area, cur_district, cur_branch = db_result[0][0], db_result[0][1], db_result[0][2]
            if value_list['area'] != '0' and value_list['area'] != cur_area:
                new_value_list['area'] = value_list['area']
            else:
                new_value_list['area'] = cur_area
            if value_list['district'] != '0' and value_list['district'] != cur_district:
                new_value_list['district'] = value_list['district']
            else:
                new_value_list['district'] = cur_district
            if value_list['branch'] != '0' and value_list['branch'] != cur_branch:
                new_value_list['branch'] = value_list['branch']
            else:
                new_value_list['branch'] = cur_branch
        return self.get_location_id(new_value_list)


    def get_volunteer_data_id(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('SELECT volunteer_data_id FROM VolunteerData WHERE volunteer_data_id = (SELECT MAX(volunteer_data_id) '
                        'FROM VolunteerData)')
            db_result = cur.fetchall()
        return db_result[0][0]

    def get_volunteer_data_id_to_update(self, volunteer_id):
        with self.conn:
            cur = self.conn.cursor()
            sql = f'SELECT volunteer_data_id FROM VolunteerData WHERE volunteer_id = {volunteer_id}'
            cur.execute(sql)
            db_result = cur.fetchall()
        return db_result[0][0]

    def insert_into_volunteer_data_table(self, volunteer):
        try:
            with self.conn:
                cur = self.conn.cursor()
                values_to_get = ["volunteer_id", "mail", "first_name", "last_name"]
                sql = f'Insert INTO VolunteerData({", ".join(values_to_get)},create_date) VALUES(?,?,?,?,CURRENT_TIMESTAMP)'
                values_as_dict = volunteer.get_my_values(values_to_get)
                cur.execute(sql, list(values_as_dict.values()))
        except sqlite3.IntegrityError:
            logging_manager.logger.error('Can not update table volunteer id is already in db')

    def insert_volunteer(self, volunteer: Volunteer):
        self.insert_into_volunteer_data_table(volunteer)
        self._last_volunteer_id_add = self.get_volunteer_data_id()
        try:
            with self.conn:
                cur = self.conn.cursor()
                # volunteer_id_cur = volunteer.get_my_values(['VolunteerDataId'])['VolunteerDataId']
                location_id_cur = self.get_location_id(volunteer.get_my_values(['area', 'district', 'branch']))
                role_id_cur = self.role_to_role_id(volunteer.get_my_values(['role'])['role'])
                sql1 = 'Insert INTO LocationAndRoleOfVolunteer(volunteer_data_id, location_id, role_id, create_date) VALUES(?,?,?,CURRENT_TIMESTAMP)'
                cur.execute(sql1, [self._last_volunteer_id_add, location_id_cur, role_id_cur])
            return True
        except sqlite3.IntegrityError:
            logging_manager.logger.error('can not update table location_and_role_of_volunteer - volunteer id is already in db')
            return False

