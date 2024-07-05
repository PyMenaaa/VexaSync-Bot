import time, threading, json, os
import discord
from discord.ext import commands
from discord import app_commands

from libs import twitch

class Data():
    tokens_data = open('data/token.txt',"r").read().splitlines()

def update_tok():
    while True:
        Data.tokens_data = open('data/token.txt',"r").read().splitlines()
        time.sleep(20)

threading.Thread(target=update_tok).start()

config = json.loads(open("config.json","r", encoding="utf8").read())

banner = ""
embed_color = 15548997


class Discord_Bot:

    bot = None
    TwitchTools = None
    followed_users = []

    def __init__(self) -> None:

        self.cooldown = {}
        self.followed = {}

        self.TwitchTools = twitch.Tools()
        self.user_slowmode_dict = {}
        self.TwitchFollowers = twitch.Follow()

        self.bot_prefix = config['bot_config']["prefix"]
        self.bot_token = config['bot_config']["token"]
        self.server_id = config['bot_config']["server_id"]
        self.twitch_channel = config['bot_config']["channel"]

        os.system("cls")

        self.run_bot()
        

    def commands(self):

        @self.bot.event
        async def on_ready():
            await self.tree.sync(guild=discord.Object(id=self.server_id))
            await self.bot.change_presence(activity=discord.Game(name=f"VexaSync"))


        # USER
        
        @self.tree.command(name="tfollow", description="[TWITCH] Sends Twitch Followers", guild=discord.Object(id=self.server_id))
        async def tfollow(interaction, username: str):
            if interaction.channel.id == self.twitch_channel:
                user_id = interaction.user.id
                slowmode_seconds = 360


                bypass_role = discord.utils.get(interaction.guild.roles, name="NoCoolDown")
            if bypass_role in interaction.user.roles:
                    slowmode_seconds = 0

            if user_id in self.user_slowmode_dict and time.time() - self.user_slowmode_dict[user_id] < slowmode_seconds:
                    remaining_time = int(slowmode_seconds - (time.time() - self.user_slowmode_dict[user_id]))
                    embed = discord.Embed(color=embed_color, description=f"Please wait {remaining_time}s before using this cmd again.")
                    embed.set_image(url=banner)
                    message = await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
                    return

            self.user_slowmode_dict[user_id] = time.time()
            
            target_id = self.TwitchTools.user_id(username)
            if target_id != False:
                    for role_name in reversed(config['tfollow']):
                        if discord.utils.get(interaction.guild.roles, name=role_name) in interaction.user.roles:
                            follow_count = config['tfollow'][role_name]
                            self.TwitchFollowers.send_follow(target_id, follow_count, Data.tokens_data)
                            self.followed_users.append(target_id)
                            embed = discord.Embed(color=embed_color, description=f"```Followers -> {follow_count}```")
                            embed.set_image(url=banner)
                            message = await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=360)
                            return
            else:
                    embed = discord.Embed(color=embed_color, description=f"Invalid Username")
                    embed.set_image(url=banner)
                    message = await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
                    return
  
        # ADMIN

        
        @self.tree.command(name="nuke",description="[ADMIN] Channel nuke", guild=discord.Object(id=self.server_id))
        @commands.has_permissions(administrator=True)
        async def nuke(interaction, channel: discord.TextChannel):
            if interaction.user.guild_permissions.administrator:
                nuke_channel = discord.utils.get(interaction.guild.channels, name=channel.name)
                if nuke_channel is not None:
                    new_channel = await nuke_channel.clone(reason="Has been Nuked!")
                    await new_channel.edit(position=nuke_channel.position)
                    await nuke_channel.delete()
                    embed = discord.Embed(color=embed_color, description=f"```VexaSync Nuke```")
                    embed.set_image(url=banner)
                    await new_channel.send(embed=embed)
                else:
                    await interaction.send(f"No channel named {channel.name} was found!")

            
        @self.tree.command(name="embed",description="[ADMIN] Send Embed", guild=discord.Object(id=self.server_id))
        @commands.has_permissions(administrator=True)
        async def embed(interaction, embed_description: str, image_url: str = None, ping: bool = False):
            if interaction.user.guild_permissions.administrator:
                embed = discord.Embed(color=embed_color, description=embed_description.replace(r"\n","\n"))
                if image_url != None:
                    embed.set_image(url=image_url)
                else:
                    embed.set_image(url=banner)
                if ping == True:
                    await interaction.channel.send("||@everyone||",embed=embed)
                else:
                    await interaction.channel.send(embed=embed)

                return
        
    def run_bot(self):

        self.bot = discord.Client(
            command_prefix=self.bot_prefix, 
            help_command=None, 
            intents=discord.Intents().all()
        )

        self.tree = app_commands.CommandTree(self.bot)

        self.commands()
        self.bot.run(self.bot_token)
        


if __name__ == "__main__":

    Discord_Bot()
