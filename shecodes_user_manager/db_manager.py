import sqlite3
import os
from datetime import date
from shecodes_user_manager import logging_manager
import sys


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
    """
    For a safe transaction you must create a scope of DbManager using the with statement.
    Methods in this class throw DbMangerException in cases where the DB enters an invalid state.
    The idea is that when DbMangerException is thrown, then any changes will be rollback at the end of the scope.
    """
    def __init__(self, path=None):
        if path is None:
            self._path_db = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "she_codes_account_manager_db_v1.db")
        else:
            self._path_db = path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self._path_db)
        # This begins a transaction
        self.conn.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # This commits or rollbacks a transaction depending on whether an exception occurred.
        self.conn.__exit__(exc_type, exc_val, exc_tb)
        self.close_db()

    def get_slack_channels_for_volunteer(self, volunteer_data_id_add):
        try:
            cur = self.conn.cursor()
            sql = 'SELECT slack_channel FROM LocationAndRoleOfVolunteer ' \
                  'INNER JOIN RoleToSlackChannel ON RoleToSlackChannel.role_id = ' \
                  'LocationAndRoleOfVolunteer.role_id ' \
                  'INNER JOIN SheCodesSlackChannels ON RoleToSlackChannel.slack_channel_id = ' \
                  'SheCodesSlackChannels.slack_channel_id ' \
                  'WHERE (volunteer_data_id = ?)'
            cur.execute(sql, (volunteer_data_id_add,))
            db_result = cur.fetchall()
            if db_result is not None and len(db_result) > 0:
                return [channel[0] for channel in db_result]
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
        raise DbManagerException("Slack channels couldn't be retrieved.")

    def get_current_location_id(self, volunteer_data_id_to_update):
        try:
            cur = self.conn.cursor()
            sql = 'SELECT location_id FROM LocationAndRoleOfVolunteer WHERE (volunteer_data_id = ?)'
            cur.execute(sql, (volunteer_data_id_to_update,))
            db_result = cur.fetchall()
            if db_result is not None and len(db_result) > 0:
                return db_result[0][0]
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
        raise DbManagerException(f"Location Id couldn't been retrieve for{volunteer_data_id_to_update}")

    def role_to_role_id(self, role):
        try:
            cur = self.conn.cursor()
            sql = 'SELECT role_id FROM SheCodesRoles WHERE (role = ?)'
            cur.execute(sql, (role,))
            db_result = cur.fetchall()
            if len(db_result) == 0:
                logging_manager.logger.error(f"no such role - check details{role}")
            else:
                return db_result[0][0]
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
        raise DbManagerException(f"Role id couldn't been retrieved for role:{role}")

    def close_db(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def volunteer_in_polling_table_check(self, volunteer_data_id):
        try:
            cur = self.conn.cursor()
            sql = 'SELECT volunteer_data_id FROM SlackPollingStatus WHERE volunteer_data_id = ?'
            cur.execute(sql, (volunteer_data_id, ))
            db_result = cur.fetchall()
            if len(db_result) > 0:
                return True
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
            raise DbManagerException("Something went wrong please check log")
        return False

    def insert_new_volunteer_to_slack_user_polling_table(self, volunteer_data_id):
        try:
            cur = self.conn.cursor()
            sql = 'Insert INTO SlackPollingStatus(volunteer_data_id, status, create_date) VALUES(?,?,CURRENT_TIMESTAMP)'
            cur.execute(sql, [volunteer_data_id, "NOT_IN_WORKSPACE"])
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
            raise DbManagerException("Error in insert volunteer please check log")

    def get_volunteer_to_check_new_status_on_slack(self):
        '''
        retrieve mail list of all volunteer which currently note as "NOT_IN_WORKSPACE"
        :return: list of volunteers mails and ids.
        '''
        try:
            cur = self.conn.cursor()
            sql = 'SELECT SlackPollingStatus.volunteer_data_id,mail FROM SlackPollingStatus' \
                  ' INNER JOIN VolunteerData ON VolunteerData.volunteer_data_id = SlackPollingStatus.volunteer_data_id' \
                  ' WHERE (status = ?)'
            cur.execute(sql, ("NOT_IN_WORKSPACE",))
            db_result = cur.fetchall()
            volunteer_mail_check_status_list = [mail[1] for mail in db_result]
            volunteer_id_check_status_list = [volunteer[0] for volunteer in db_result]
            return volunteer_mail_check_status_list, volunteer_id_check_status_list
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
            raise DbManagerException("Something went wrong please check logs")

    def update_volunteer_data(self, volunteer: Volunteer):
        if (len(volunteer.volunteer_id) > 0) and (len(volunteer.first_name) > 0) and (len(volunteer.last_name) > 0):
            volunteer_data_id_to_update = self.get_volunteer_data_id_to_update(volunteer.volunteer_id)
            if volunteer_data_id_to_update is None:
                return False
            if volunteer.mail != "0":
                self.update_volunteer_mail(volunteer)
                logging_manager.logger.info(f'mail updated successfully to {volunteer.mail}')
            try:
                role_id_cur = 0
                cur = self.conn.cursor()
                # volunteer_id_cur = volunteer.get_my_values(['VolunteerDataId'])['VolunteerDataId']
                location_id_cur = self.get_current_location_id(volunteer_data_id_to_update)
                location_id_new = self.new_location_id_to_update(location_id_cur, volunteer.get_my_values(
                    ['area', 'district', 'branch']))
                if location_id_cur != location_id_new:
                    location_to_update = location_id_new
                else:
                    location_to_update = location_id_cur
                if volunteer.role != '0':
                    role_id_cur = self.role_to_role_id(volunteer.role)
                if location_id_cur is None or role_id_cur is None or location_id_new is None:
                    return False
                if (location_id_cur != location_id_new) or (role_id_cur != 0):
                    sql1 = 'UPDATE LocationAndRoleOfVolunteer SET location_id = ?, role_id = ?, ' \
                           'modified_date = CURRENT_TIMESTAMP WHERE volunteer_data_id = ?'
                    cur.execute(sql1, (location_to_update, role_id_cur, volunteer_data_id_to_update))
                else:
                    logging_manager.logger.info("no updates preformed in location nor role")
                return True
            except sqlite3.IntegrityError:
                logging_manager.logger.error(
                    "Some error occurred can't update location_and_role_of_volunteer table")
                return False
            except sqlite3.DatabaseError as e:
                logging_manager.logger("Unexpected DB error" + e)
                raise DbManagerException("Something went wrong please check log")
        else:
            logging_manager.logger.error("volunteer_id+first name+last name must be entered")
            return False

    def update_volunteer_mail(self, volunteer):
        try:
            cur = self.conn.cursor()
            values_to_get = ["volunteer_id", "mail", "first_name", "last_name"]
            sql = """UPDATE VolunteerData SET mail = ?, modified_date = CURRENT_TIMESTAMP WHERE volunteer_id = ? AND first_name = ? AND last_name = ?"""
            values_as_dict = volunteer.get_my_values(values_to_get)
            cur.execute(sql, (values_as_dict["mail"], values_as_dict["volunteer_id"], values_as_dict["first_name"],
                              values_as_dict["last_name"]))
        except sqlite3.IntegrityError:
            logging_manager.logger.error("Can not update table volunteer_id + first&last name doesn't exist on DB")
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception('unexpected DB error')
            raise DbManagerException("Something went wrong please check log")

    def update_slack_user_status(self, volunteer_data_id_list, status):
        '''
        :param volunteer_data_id_list: list of volunteer which their status needed to be changed
        :param status: The status message to update
        '''
        for volunteer_data_id in volunteer_data_id_list:
            try:
                cur = self.conn.cursor()
                sql = """UPDATE SlackPollingStatus SET status = ?, modified_date = CURRENT_TIMESTAMP WHERE volunteer_data_id = ?"""
                cur.execute(sql, (status, volunteer_data_id))
            except sqlite3.Error as error:
                logging_manager.logger.error("failed to update SlackPollingStatus table")
                raise DbManagerException("Something went wrong please check log")

    def get_location_id(self, values_list):
        try:
            with self.get_safe_db_conn():
                cur = self.conn.cursor()
                sql = 'SELECT location_id FROM Location WHERE ((area = ?) AND (district = ?) AND (branch = ?))'

                cur.execute(sql, (values_list['area'], values_list['district'], values_list['branch'],))

                db_result = cur.fetchall()
                if len(db_result) == 0:
                    logging_manager.logger.error(f"no such location - value_list = {values_list}")
                else:
                    return db_result[0][0]
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e + f" no such location - value_list = {values_list}")
        return None

    def new_location_id_to_update(self, location_id_curr, value_list):
        try:
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
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
            raise DbManagerException("Something went wrong please check log")
        return self.get_location_id(new_value_list)

    def get_volunteer_data_id(self):
        try:
            cur = self.conn.cursor()
            cur.execute(
                'SELECT volunteer_data_id FROM VolunteerData WHERE volunteer_data_id = (SELECT MAX(volunteer_data_id) '
                'FROM VolunteerData)')
            db_result = cur.fetchall()
            return db_result[0][0]
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
            raise DbManagerException("Something went wrong please check log")
        return None

    def get_volunteer_data_id_to_update(self, volunteer_id):
        try:
            cur = self.conn.cursor()
            sql = f'SELECT volunteer_data_id FROM VolunteerData WHERE volunteer_id = {volunteer_id}'
            cur.execute(sql)
            db_result = cur.fetchall()
            if len(db_result) == 0:
                logging_manager.logger.error(f"no such volunteer id in DB to update: {volunteer_id}")
            else:
                return db_result[0][0]
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception(e)
            raise DbManagerException("Something went wrong please check log")
        return None

    def insert_into_volunteer_data_table(self, volunteer):
        try:
            cur = self.conn.cursor()
            values_to_get = ["volunteer_id", "mail", "first_name", "last_name"]
            sql = f'Insert INTO VolunteerData({", ".join(values_to_get)},create_date,modified_date) VALUES(?,?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)'
            values_as_dict = volunteer.get_my_values(values_to_get)
            cur.execute(sql, list(values_as_dict.values()))
        except sqlite3.IntegrityError:
            logging_manager.logger.error('Can not update table volunteer id is already in db')
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception("Unexpected DB error")
            raise DbManagerException("Something went wrong please check log")

    def get_safe_db_conn(self):
        if self.conn is None:
            logging_manager.log_error_with_stacktrace("DB connection is closed!", end_program=True)
        else:
            return self.conn

    def insert_volunteer(self, volunteer: Volunteer):
        self.insert_into_volunteer_data_table(volunteer)
        self._last_volunteer_id_add = self.get_volunteer_data_id()
        if self._last_volunteer_id_add is None:
            return False
        try:
            cur = self.conn.cursor()
            # volunteer_id_cur = volunteer.get_my_values(['VolunteerDataId'])['VolunteerDataId']
            location_id_cur = self.get_location_id(volunteer.get_my_values(['area', 'district', 'branch']))
            role_id_cur = self.role_to_role_id(volunteer.get_my_values(['role'])['role'])
            if location_id_cur is None or role_id_cur is None:
                return False
            sql1 = 'Insert INTO LocationAndRoleOfVolunteer(volunteer_data_id, location_id, role_id, create_date,modified_date) VALUES(?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)'
            cur.execute(sql1, [self._last_volunteer_id_add, location_id_cur, role_id_cur])
            return True
        except sqlite3.IntegrityError:
            logging_manager.logger.error(
                'can not update table location_and_role_of_volunteer - volunteer id is already in db')
            return False
        except sqlite3.DatabaseError as e:
            logging_manager.logger.exception("Unexpected DB error")
            raise DbManagerException("Something went wrong please check log")


    def get_data_from_volunteer_data_table(self, volunteer_data_id):
        cur = self.conn.cursor()
        sql = f'SELECT first_name, last_name, mail, create_date, modified_date FROM VolunteerData WHERE volunteer_data_id = ?'
        cur.execute(sql, (volunteer_data_id,))
        db_result = cur.fetchall()
        if len(db_result) == 0:
            logging_manager.logger.exception(f"no such volunteer id in DB to update: {volunteer_data_id}")
            raise DbManagerException(f"no such volunteer id in DB to update: {volunteer_data_id}")
        value_as_dict = {"first_name": db_result[0][0],
                         "last_name": db_result[0][1],
                         "mail": db_result[0][2],
                         "create_date": db_result[0][3],
                         "modified_date": db_result[0][4]}
        return value_as_dict

    def view_volunteer_data(self, volunteer: Volunteer):
        volunteer_data_id = self.get_volunteer_data_id_to_update(volunteer.volunteer_id)
        if volunteer_data_id is None:
            return None
        slack_channel = self.get_slack_channels_for_volunteer(volunteer_data_id)
        volunteer_data_info = self.get_data_from_volunteer_data_table(volunteer_data_id)
        cur = self.conn.cursor()
        sql = 'SELECT area, district, branch, role FROM SheCodesRoles ' \
              'INNER JOIN LocationAndRoleOfVolunteer ON SheCodesRoles.role_id = ' \
              'LocationAndRoleOfVolunteer.role_id ' \
              'INNER JOIN Location ON Location.location_id = ' \
              'LocationAndRoleOfVolunteer.location_id ' \
              'WHERE (volunteer_data_id = ?)'
        cur.execute(sql, (volunteer_data_id,))
        db_result = cur.fetchall()

        dict_values = {"volunteer id": volunteer.volunteer_id,
                       "email": volunteer_data_info["mail"],
                       "first name": volunteer_data_info["first_name"],
                       "last name": volunteer_data_info["last_name"],
                       "create date": volunteer_data_info["create_date"],
                       "modified date": volunteer_data_info["modified_date"],
                       "area": db_result[0][0],
                       "district": db_result[0][1],
                       "branch": db_result[0][2],
                       "role": db_result[0][3],
                       "channels": slack_channel
                       }
        return dict_values
