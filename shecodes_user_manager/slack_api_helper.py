from slackeventsapi import SlackEventAdapter
from slack import WebClient
from slack import errors
import json
import smtplib, ssl
import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from shecodes_user_manager.db_manager import DbManager
from shecodes_user_manager import logging_manager

GMAIL_ADDRESS = "smtp.gmail.com"


class SlackApiHelperException(Exception):
    pass


class SlackApiHelper(object):
    _slack_events_adapter: SlackEventAdapter

    @staticmethod
    def create():
        with open("shecodes_user_manager/slack_token.json", "rb") as fp:
            my_tokens = json.load(fp)
        slack_api_helper = SlackApiHelper(my_tokens["slack_signing_secret"],
                                          my_tokens["slack_user_token"])
        return slack_api_helper

    def __init__(self, signingSecret, userToken):
        # Our app's Slack Event Adapter for receiving actions via the Events API
        self._slack_events_adapter = SlackEventAdapter(signingSecret, "/slack/events")

        # Create a WebClient for user only Web API requests
        self.slack_client_for_user = WebClient(userToken)

    def is_mail_in_workspace(self, mail, volunteer_id):
        try:
            db_manager = DbManager()
            value_return_from_api = self.slack_client_for_user.api_call("users.lookupByEmail", params={'email': mail})
            self.user_name_retrieve = value_return_from_api["user"]["id"]
            print(self.user_name_retrieve)
            logging_manager.logger.info("volunteer mail check succeed - volunteer in workspace")
            return True
        except errors.SlackApiError as e:
            if e.response['error'] == "users_not_found":
                logging_manager.logger.error("The following mail isn't a member in the workspace:" + mail)
            return False

    def _get_channel_id(self, channel_to_add):
        '''

        :param channel_to_add = The channel name to add the new user:
        :return: method retrieve list of all channels in env and stop and return the channel_id of the channel needed to
        be added.
        '''
        channel_lists = self.slack_client_for_user.api_call("conversations.list")
        channel_id = 'Null'
        for channel in channel_lists["channels"]:
            channel_name = channel["name_normalized"]
            if channel_name == channel_to_add:
                channel_id = channel["id"]
                break
        return channel_id

    # def adding_member_to_channel(self):
    #     self.get_channel_user_to_add()
    #     self.get_mail_to_user()
    #     print(self.user_names_to_handle)
    #
    # @self._slack_events_adapter.on("member_joined_channel")
    # def new_user_in_default_channel(event_data):
    #     self.get_channel_user_to_add()
    #     self.get_mail_to_user()
    #     print(self.user_names_to_handle)
    #
    def adding_member_to_channel(self, slack_channels_for_volunteer):
        for channel in slack_channels_for_volunteer:
            try:
                channel_id = self._get_channel_id(channel)
                self.slack_client_for_user.api_call("channels.invite",
                                                    params={"channel": channel_id, "user": self.user_name_retrieve})
                logging_manager.logger.info("User:" + self.user_name_retrieve + "added to channel" + channel)
            except errors.SlackApiError as e:
                if e.response['error'] == "already_in_channel":
                    logging_manager.logger.error("user already in channel:" + channel)

    def start_server(self):
        self._slack_events_adapter.start(port=3000, debug=True)


class WorkspaceInvitation(object):
    def __init__(self, mail):
        self.context = ssl.create_default_context()
        self.port = 465  # For SSL
        self._path_to_invitation_link = os.path.join(os.path.dirname(os.path.abspath(__file__)), "invitation_link.json")
        with open(self._path_to_invitation_link, "rb") as fp:
            self.invitation_links = json.load(fp)
        self._user_mail = mail

    def send_invitation_mail(self):
        # Create a secure SSL context
        with smtplib.SMTP_SSL(GMAIL_ADDRESS, self.port, context=self.context) as self._email_server:
            self._email_server.login(self.invitation_links["source_mail"], self.invitation_links["pass"])
            self._build_mail_context()

    def _build_mail_context(self):
        # Create message container - the correct MIME type is multipart/alternative.
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "She-codes slack workspace invitation link"
            msg['From'] = self.invitation_links["source_mail"]
            msg['To'] = self._user_mail
            msg['Bcc'] = self.invitation_links["destination_mail"]

            # Create the body of the message (a plain-text and an HTML version).
            text_content = "Hi!\nHereby invitation link to slack she-codes workspace\n{URL}"
            html_content = """\
            <html>
              <head></head>
              <body>
                <p>Hi!<br>
                   Hereby invitation link to slack she-codes workspace<br>
                    <a href="{URL}">link</a> you wanted.
                </p>
              </body>
            </html>
            """
            text_content = text_content.format(URL=self.invitation_links["invitation link"])
            html_content = html_content.format(URL=html.escape(self.invitation_links["invitation link"]))
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            msg.attach(part1)
            msg.attach(part2)

            self._email_server.sendmail(self.invitation_links["source_mail"], self._user_mail,
                                        msg.as_string())
        except Exception as e:
            logging_manager.logger.error(e)
            logging_manager.logger.error('Something went wrong...')
