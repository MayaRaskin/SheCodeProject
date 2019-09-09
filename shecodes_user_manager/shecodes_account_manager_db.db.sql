BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "slack_volunteer_data" (
	"mail"	TEXT NOT NULL,
	"area"	TEXT NOT NULL,
	"district"	TEXT NOT NULL,
	"branch"	TEXT,
	"role"	TEXT NOT NULL,
	"handled"	INTEGER NOT NULL,
	PRIMARY KEY("mail")
);
CREATE TABLE IF NOT EXISTS "slack_role_channel" (
	"role"	TEXT NOT NULL,
	"channel"	TEXT NOT NULL
);
COMMIT;
