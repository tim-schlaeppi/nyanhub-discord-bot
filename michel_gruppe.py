import re

GUILD_ID = 690112280473370627
#GUILD_ID = 766185641146449930 #ID vom Testserver

# Wird bei jeder nicht-Bot-Nachricht auf dem MG-Server ausgeführt
async def process_message(message):
    matches = re.findall(r"ticket ?#? ?(\d+)", message.content.lower())
    output = set()
    for match in matches:
        if match.isnumeric() and 70 < int(match) < 1_000_000:
            output.add(f"http://helpdesk.michel-gruppe.ch/SREdit.jsp?id={match}")

    if len(output) > 0:
        reply = "Hier der Direktlink zum Ticket:\n"
        reply += "\n".join(output)

        await message.channel.send(reply)
