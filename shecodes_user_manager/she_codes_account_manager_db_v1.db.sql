BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "LocationAndRoleOfVolunteer" (
	"volunteer_data_id"	INTEGER NOT NULL,
	"location_id"	INTEGER NOT NULL,
	"role_id"	INTEGER NOT NULL,
	"create_date"	TEXT,
	"modified_date"	TEXT,
	PRIMARY KEY("volunteer_data_id","location_id","role_id")
);
CREATE TABLE IF NOT EXISTS "SlackPollingStatus" (
	"volunteer_data_id"	INTEGER NOT NULL UNIQUE,
	"status"	TEXT NOT NULL,
	"create_date"	TEXT,
	"modified_date"	TEXT
);
CREATE TABLE IF NOT EXISTS "VolunteerData" (
	"volunteer_data_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"volunteer_id"	TEXT NOT NULL UNIQUE,
	"mail"	TEXT NOT NULL,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"create_date"	TEXT,
	"modified_date"	INTEGER
);
CREATE TABLE IF NOT EXISTS "SheCodesRoles" (
	"role_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"role"	TEXT NOT NULL,
	"create_date"	TEXT NOT NULL,
	"modified_date"	TEXT
);
CREATE TABLE IF NOT EXISTS "SheCodesSlackChannels" (
	"slack_channel_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"slack_channel"	INTEGER NOT NULL,
	"create_date"	TEXT NOT NULL,
	"modified_date"	TEXT
);
CREATE TABLE IF NOT EXISTS "RoleToSlackChannel" (
	"role_id"	INTEGER NOT NULL,
	"slack_channel_id"	INTEGER NOT NULL,
	PRIMARY KEY("role_id","slack_channel_id")
);
CREATE TABLE IF NOT EXISTS "Location" (
	"location_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"area"	TEXT NOT NULL,
	"district"	TEXT NOT NULL,
	"branch"	TEXT NOT NULL,
	"create_date"	TEXT NOT NULL,
	"modified_date"	TEXT NOT NULL
);

INSERT INTO "SheCodesRoles" VALUES (1,'branch_manager','0',NULL);
INSERT INTO "SheCodesRoles" VALUES (2,'area_manager','0',NULL);
INSERT INTO "SheCodesRoles" VALUES (3,'district_manager','0',NULL);
INSERT INTO "SheCodesRoles" VALUES (4,'volunteer','0',NULL);
INSERT INTO "SheCodesSlackChannels" VALUES (1,'t_area_district','0',NULL);
INSERT INTO "SheCodesSlackChannels" VALUES (2,'t_area_district_nat','0',NULL);
INSERT INTO "SheCodesSlackChannels" VALUES (3,'t_branches_area_mang','0',NULL);
INSERT INTO "SheCodesSlackChannels" VALUES (4,'branches_manag','0',NULL);
INSERT INTO "SheCodesSlackChannels" VALUES (5,'teams','0',NULL);
INSERT INTO "RoleToSlackChannel" VALUES (1,3);
INSERT INTO "RoleToSlackChannel" VALUES (1,4);
INSERT INTO "RoleToSlackChannel" VALUES (1,5);
INSERT INTO "RoleToSlackChannel" VALUES (2,1);
INSERT INTO "RoleToSlackChannel" VALUES (2,2);
INSERT INTO "RoleToSlackChannel" VALUES (2,5);
INSERT INTO "RoleToSlackChannel" VALUES (3,1);
INSERT INTO "RoleToSlackChannel" VALUES (3,2);
INSERT INTO "RoleToSlackChannel" VALUES (3,5);
INSERT INTO "RoleToSlackChannel" VALUES (4,5);
INSERT INTO "Location" VALUES (1,'haifa','north','technion','0','');
COMMIT;
