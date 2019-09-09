from slackeventsapi import SlackEventAdapter
from slack import WebClient
import json
import smtplib, ssl
import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from shecodes_user_manager.db_manager import DbManager

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
        new_user_mail = "maximus.raskin@gmail.com"
        channel_to_add = "tests"
        return new_user_mail, channel_to_add

    def get_mail_to_user(self, add_user):
        value_return_from_api = self.slack_client.api_call("users.lookupByEmail", params={'email': add_user})
        user_name_retrieve = value_return_from_api["user"]["id"]
        return user_name_retrieve

    def get_channel_id(self, channel_to_add):
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

    def adding_member_to_channel(self):
        @self._slack_events_adapter.on("member_joined_channel")
        def new_user_in_default_channel(event_data):
            add_user, channel_to_add = self.get_channel_user_to_add()
            user_name = self.get_mail_to_user(add_user)

            channel_id = self.get_channel_id(channel_to_add)
            self.slack_client_for_user.api_call("channels.invite", params={"channel": channel_id, "user": user_name})

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
        with smtplib.SMTP_SSL(GMAIL_ADDRESS, self.port, context=self.context) as self.server:
            self.server.login(self.invitation_links["source_mail"], self.invitation_links["pass"])
            self._send_mail()

    def _send_mail(self):
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

        self.server.sendmail(self.invitation_links["source_mail"], self.invitation_links["destination_mail"], msg.as_string())


def main():
    with open("slack_token.json", "rb") as fp:
        my_tokens = json.load(fp)
    slack_invitation_mail = WorkspaceInvitation()
    slack_invitation_mail.send_invitation_mail()
    slack_api_helper = SlackApiHelper(my_tokens["slack_signing_secret"], my_tokens["slack_bot_token"],
                                      my_tokens["slack_user_token"])
    # Once we have our event listeners configured, we can start the
    # Flask server with the default `/events` endpoint on port 3000
    db_manager = DbManager("shecodes_account_manager_db.db")
    db_manager.volunteer_to_handle()

    slack_api_helper.start_server()


main()
