CREATE TABLE IF NOT EXISTS guilds (
    GuildID integer PRIMARY KEY,
    Prefix text DEFAULT "!"
);

CREATE TABLE IF NOT EXISTS exp (
    UserID INTEGER PRIMARY KEY,
    XP INTEGER,
    Level INTEGER,
    XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mutes (
    UserID integer PRIMARY KEY,
    RoleIDs text,
    EndTime text
);