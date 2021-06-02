import random
import mysql.connector

class SoundEffect:
    regex = None
    text = None
    abkuerzung = None
    filename = None
    tags = None

    def __init__(self, regex, text, abkuerzung, filename, tags=None):
        self.regex = regex
        self.text = text
        self.abkuerzung = abkuerzung
        self.filename = filename
        if tags:
            self.tags = tags


class SoundEffectHelper:
    revision_num = -1
    effects = set()

    def __init__(self):
        self.connection = mysql.connector.connect(
            user="nyanhub",
            database="nyanhub",
            host="tim-discordbot",
            password="4u6ardymu84yw2gu68rnh45y6550w4swj50fdvdn"
        )

    def get_effects(self):
        cursor = self.connection.cursor()

        revision_num_query = "select num from revision_num where type = 'nyanhub_sounds'"
        sounds_query = "select regex, description, abbreviation, filename from sound_effect"

        cursor.execute(revision_num_query)
        if cursor.fetchone()[0] > self.revision_num:
            print("Neue Sounds-Version verfügbar. Lade Daten...")
            cursor.close()
            cursor = self.connection.cursor()

            cursor.execute(sounds_query)
            for (regex, description, abbreviation, filename) in cursor:
                self.effects.add(SoundEffect(regex, description, abbreviation, filename))


        cursor.close()

        return self.effects

#TBA: Motherfucker, Yaas, Hello There, High ground etc., gas gas gas
# https://discord.com/channels/689778353443831809/689778353443831813/839603030113648690
# https://discord.com/channels/689778353443831809/689778353443831813/840712795044839425
# https://discord.com/channels/689778353443831809/689778353443831813/841620633938034689
#assi andreas

"""
array funktioniert folgendermassen:
    elem[0] = regex, um den ganzen satz zu matchen
    elem[1] = anzeigetext für die Hilfeseite
    elem[2] = abkürzung, die auch für das sagen verwendet werden kann (nicht doppelt vergeben)
    elem[3] = filename i Unterverzeichnis sounds/
    elem[4] = tags, für spätere kategorisierung. im format "sg", damit man mit 'if "s" in elem.tags:' matchen kann

"""