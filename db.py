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
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

c.execute("create table if not exists guild_setting (guild_id int, setting_name string, setting_value string)")


# Setter und Getter
def get_guild_setting(guild_id: int, setting_name):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute(f"SELECT {setting_name} FROM guild_setting WHERE guild_id = ?", [guild_id])
    row = c.fetchone()

    return json.loads(row.setting_value)

'''
Implementierte guild_settings bisher:
    command_prefix: Bestimmt das command prefix pro Server. wird in der Funktion get/set_command_prefix verwendet
'''
def set_guild_setting(guild_id: int, setting_name, setting_value):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("INSERT INTO guild_setting (guild_id, setting_name, setting_type) VALUES (?, ?, ?)", [
        guild_id,
        setting_name,
        json.dumps(setting_value)
    ])

    conn.commit()

# Funktionen

def get_command_prefix(bot, message):
    return get_guild_setting(message.guild.id, GUILD_SETTINGS.COMMAND_PREFIX)

def set_command_prefix(guild, prefix):
    set_guild_setting(guild.id, GUILD_SETTINGS.COMMAND_PREFIX, prefix)


