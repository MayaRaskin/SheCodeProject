from slackeventsapi import SlackEventAdapter
from slack import WebClient
from slack import errors
import json
import smtplib, ssl
import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from server import main

GMAIL_ADDRESS = "smtp.gmail.com"


class SlackApiHelper(object):
    _slack_events_adapter: SlackEventAdapter

    def __init__(self, signingSecret, botToken, userToken):
        # Our app's Slack Event Adapter for receiving actions via the Events API
        self._slack_events_adapter = SlackEventAdapter(signingSecret, "/slack/events")

        # Create a WebClient for your bot to use for Web API requests
        self.slack_client = WebClient(botToken)

        # Create a WebClient for user only Web API requests
        self.slack_client_for_user = WebClient(userToken)

    def get_channel_user_to_add(self):
        self._new_user_mails = ["maximus.raskin@gmail.com", "maya.mnkr@gmail.com", "hadasstr@gmail.com"]
        self._channel_to_add = "tests"

    def get_mail_to_user(self):
        self.user_names_to_handle = {}
        for user_mail in self._new_user_mails:
            try:
                value_return_from_api = self.slack_client.api_call("users.lookupByEmail", params={'email': user_mail})
                user_name_retrieve = value_return_from_api["user"]["id"]
                self.user_names_to_handle[user_mail] = user_name_retrieve
            except errors.SlackApiError as e:
                if (e.response['error'] == "users_not_found"):
                    print("The following mail isn't a member in the workspace:" + user_mail)
        print(self.user_names_to_handle)

    def _get_channel_id(self, channel_to_add):
        '''

        :param channel_to_add = The channel name to add the new user:
        :return: method retrieve list of all channels in env and stop and return the channel_id of the channel needed to
        be added.
        '''
        channel_lists = self.slack_client.api_call("conversations.list")
        channel_id = 'Null'
        for channel in channel_lists["channels"]:
            print(channel)
            channel_name = channel["name_normalized"]
            if channel_name == channel_to_add:
                channel_id = channel["id"]
                break
        return channel_id

    # def adding_member_to_channel(self):
    # @self._slack_events_adapter.on("member_joined_channel")
    # def new_user_in_default_channel(event_data):
    # add_user, channel_to_add = self.get_channel_user_to_add()
    # self.get_mail_to_user()

    # channel_id = self._get_channel_id(channel_to_add)
    # self.slack_client_for_user.api_call("channels.invite", params={"channel": channel_id, "user": user_name})

    def start_server(self):
        self._slack_events_adapter.start(port=3000, debug=True)


class WorkspaceInvitation(object):
    def __init__(self):
        self.context = ssl.create_default_context()
        self.port = 465  # For SSL
        with open("invitation_link.json", "rb") as fp:
            self.invitation_links = json.load(fp)

    def send_invitation_mail(self):
        # Create a secure SSL context
        with smtplib.SMTP_SSL(GMAIL_ADDRESS, self.port, context=self.context) as self._server:
            self._server.login(self.invitation_links["source_mail"], self.invitation_links["pass"])
            self._build_mail_context()

    def _build_mail_context(self):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "She-codes slack workspace invitation link"
        msg['From'] = self.invitation_links["source_mail"]
        msg['To'] = self.invitation_links["destination_mail"]

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

        self._server.sendmail(self.invitation_links["source_mail"], self.invitation_links["destination_mail"],
                              msg.as_string())


