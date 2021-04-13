import sqlite3
import json

# Einstellungen

DATABASE = "discord_bot.db"
class GUILD_SETTINGS:
    COMMAND_PREFIX = "command_prefix"

    def __setattr__(self, key, value):
        raise AttributeError("Can't assign to constants")

GUILD_SETTINGS = GUILD_SETTINGS()

# Init
def init():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("create table if not exists guild_setting (guild_id int, setting_name string, setting_value string, UNIQUE (guild_id, setting_name))")

    c.execute("INSERT INTO guild_setting (guild_id, setting_name, setting_value) VALUES (?, ?, ?)"
              "ON CONFLICT DO NOTHING", [
                  0,
                  GUILD_SETTINGS.COMMAND_PREFIX,
                  json.dumps("!"),
              ]
    )

    conn.commit()

# Setter und Getter
def get_guild_setting(guild_id, setting_name):
    if not isinstance(guild_id, int):
        guild_id = guild_id.id

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute(f"SELECT setting_value FROM guild_setting WHERE guild_id = ? and setting_name = ?", [guild_id, setting_name])
    row = c.fetchone()

    if row is None:
        # guild_id = 0 ist die Standardeinstellung
        c.execute(f"SELECT setting_value FROM guild_setting WHERE guild_id = ? and setting_name = ?",
                  [0, setting_name])
        row = c.fetchone()

    if row is None:
        return None
    else:
        return json.loads(row[0])

'''
Implementierte guild_settings bisher:
    command_prefix: Bestimmt das command prefix pro Server. wird in der Funktion get/set_command_prefix verwendet
'''
def set_guild_setting(guild_id, setting_name, setting_value):
    if guild_id is None:
        guild_id = 0
    elif not isinstance(guild_id, int):
        guild_id = guild_id.id

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    value = json.dumps(setting_value)

    c.execute("INSERT INTO guild_setting (guild_id, setting_name, setting_value) VALUES (?, ?, ?)"
              "ON CONFLICT (guild_id, setting_name) DO UPDATE SET setting_value = ?", [
        guild_id,
        setting_name,
        value,
        value,
    ])

    conn.commit()

# Funktionen

def get_default_setting(setting_name):
    return get_guild_setting(0, setting_name)

def set_default_setting(setting_name, setting_value):
    set_guild_setting(0, setting_name, setting_value)

def get_command_prefix(bot, message):
    if message.guild:
        return get_guild_setting(message.guild.id, GUILD_SETTINGS.COMMAND_PREFIX)
    else:
        return get_guild_setting(0, GUILD_SETTINGS.COMMAND_PREFIX)

def set_command_prefix(guild, prefix):
    set_guild_setting(guild.id, GUILD_SETTINGS.COMMAND_PREFIX, prefix)


