import json


def create_json_of_slack_tokens(slack_signing_secret, slack_user_token):
    data = {'slack_signing_secret': slack_signing_secret,
            'slack_user_token': slack_user_token}

    with open('shecodes_user_manager/slack_token.json', 'w') as filepointer:
        json.dump(data, filepointer)


def create_json_of_invitation_link(slack_link, password, source_mail, destination_mail):
    data = {'invitation link': slack_link,
            'pass': password,
            'source_mail': source_mail,
            'destination_mail': destination_mail}

    with open('shecodes_user_manager/invitation_link.json', 'w') as filepointer:
        json.dump(data, filepointer)


def main():
    slack_signing_secret = input("Enter slack_signing_secret")
    slack_user_token = input("Enter slack_user_token")
    source_mail = input("Enter source email for invitation to workspace")
    google_app_pass = input("Enter goodle app password of email")
    slack_link = input("Enter slack link to invite new volunteers to workspace")
    destination_mail = input("Enter email which get all emails send to new volunteer as BCC")
    create_json_of_slack_tokens(slack_signing_secret, slack_user_token)
    create_json_of_invitation_link(slack_link, google_app_pass, source_mail, destination_mail)


if __name__ == "__main__":
    main()
