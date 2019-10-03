import time
from shecodes_user_manager.db_manager import DbManager


def main():
    manager = DbManager()
    while True:
        response = manager.get_slack_user_status()
        if response > 0:
            print("add to channels")
            print("update status table")
        time.sleep(5)


if __name__ == "__main__":
    main()
