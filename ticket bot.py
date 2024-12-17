from discord.ui import Button, View
from discord import app_commands
import colorama
import datetime
import discord
import asyncio
import json
import threading
import subprocess

# Set this to false if you dont want to run the webui

WEBUI: bool = True
# WEBUI: bool = False     <-- like this


# ------------------------------

TOKEN: str = ""

# ------------------------------

Red_Text = colorama.Fore.RED
Green_Text = colorama.Fore.GREEN
Reset_Color = colorama.Fore.RESET

def get_ticket_number():
    try:
        with open('database.json', 'r') as f:
            data = json.load(f)
            tickets = data.get('tickets', [])
            new_number = len(tickets) + 1
            tickets.append({
                "ticket_number": new_number,
                "messages": [],
                "creator": None,  
                "created_at": None
            })
        with open('database.json', 'w') as f:
            json.dump({"tickets": tickets}, f, indent=4)
        return new_number
    except FileNotFoundError:
        with open('database.json', 'w') as f:
            json.dump({"tickets": [{"ticket_number": 1, "messages": [], "creator": None, "created_at": None}]}, f, indent=4)
        return 1

def log_message(ticket_number, author, content, timestamp):
    try:
        with open('database.json', 'r') as f:
            data = json.load(f)
        
        for ticket in data['tickets']:
            if ticket['ticket_number'] == ticket_number:
                message_data = {
                    "author": author,
                    "content": content,
                    "timestamp": timestamp
                }
                ticket['messages'].append(message_data)
                break
        
        with open('database.json', 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"{Red_Text}Error logging message: {e}{Reset_Color}")

def update_ticket_creator(ticket_number, creator, timestamp):
    try:
        with open('database.json', 'r') as f:
            data = json.load(f)
        
        for ticket in data['tickets']:
            if ticket['ticket_number'] == ticket_number:
                ticket['creator'] = {
                    "name": str(creator),
                    "id": str(creator.id)
                }
                ticket['created_at'] = timestamp
                break
        
        with open('database.json', 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"{Red_Text}Error updating ticket creator: {e}{Reset_Color}")

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="ticket_button")
    async def ticket_button(self, interaction: discord.Interaction, button: Button):
        ticket_number = get_ticket_number()
        
        
        update_ticket_creator(
            ticket_number,
            interaction.user,
            datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        category = discord.utils.get(interaction.guild.categories, name="Tickets")
        if not category:
            category = await interaction.guild.create_category("Tickets")

        channel = await interaction.guild.create_text_channel(
            f"ticket-{ticket_number}",
            category=category,
            overwrites=overwrites
        )

        
        class TicketManageView(View):
            def __init__(self, channel, ticket_number):
                super().__init__(timeout=None)
                self.channel = channel
                self.ticket_number = ticket_number

            @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
            async def close_ticket(self, i: discord.Interaction, b: Button):

                em = discord.Embed(
                    title="Ticket Closed",
                    description="Closing in 5 seconds.",
                    color=discord.Color.red()
                )

                await i.response.send_message(embed=em, ephemeral=True)
                await asyncio.sleep(5)
                await self.channel.delete()

        
        embed = discord.Embed(
            title=f"Ticket #{ticket_number}",
            description=f"Welcome {interaction.user.mention}!\nSupport will be with you shortly.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"Ticket opened by {interaction.user}")
        
        await channel.send(embed=embed, view=TicketManageView(channel, ticket_number))

        em = discord.Embed(
            title="Ticket Created",
            description=f"Your ticket has been created in {channel.mention}.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=em, ephemeral=True)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync() 
            self.synced = True
        print(f"{Green_Text}| --> Logged in as {Reset_Color}{self.user}.")

    async def on_message(self, message):
        if message.author.bot:
            return
            
        if isinstance(message.channel, discord.TextChannel):
            if message.channel.name.startswith("ticket-"):
                try:
                    ticket_number = int(message.channel.name.split("-")[1])
                    log_message(
                        ticket_number,
                        str(message.author),
                        message.content,
                        message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    )
                except ValueError:
                    pass

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name="setup-ticket", description="Setup the ticket system")
async def setup_ticket(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be an administrator to use this command.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎫 Support Ticket",
        description=(
            "Need assistance? Create a ticket by clicking the button below!\n\n"
            "**When should you create a ticket?**\n"
            "• When you need help from our staff team\n"
            "• To report an issue\n"
            "• For general support\n\n"
            "A staff member will assist you as soon as possible."
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Support Ticket System")
    embed.timestamp = datetime.datetime.utcnow()
    await interaction.channel.send(embed=embed, view=TicketView())

    setup_done_embed = discord.Embed(
        title="Ticket System Setup",
        description="The ticket system has been setup!",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=setup_done_embed, ephemeral=True)

@tree.command(name="close-ticket", description="Close a ticket")
async def close_ticket(interaction: discord.Interaction):

    if not isinstance(interaction.channel, discord.TextChannel):
        em2 = discord.Embed(
            title="Invalid Channel",
            description="This command can only be used in a ticket channel.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=em2, ephemeral=True)
        return

    if not interaction.channel.name.startswith("ticket-"):
        em3 = discord.Embed(
            title="Invalid Ticket Channel",
            description="This command can only be used in a ticket channel.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=em3, ephemeral=True)
        return

    try:
        ticket_number = int(interaction.channel.name.split("-")[1])
    except ValueError:
        em4 = discord.Embed(
            title="Invalid Ticket Channel",
            description="This command can only be used in a ticket channel.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=em4, ephemeral=True)
        return

    em5 = discord.Embed(
        title="Ticket Closed",
        description="Closing ticket in 5 seconds...",
        color=discord.Color.red(),
        timestamp=datetime.datetime.utcnow()
    )
    await interaction.response.send_message(embed=em5)
    await asyncio.sleep(5)
    await interaction.channel.delete()

def run_webui():
    subprocess.run(["python", "server.py"])

if WEBUI:
    webui_thread = threading.Thread(target=run_webui)
    webui_thread.start()

client.run(TOKEN)