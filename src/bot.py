import discord

class TTRPGbot(discord.Bot):
    selected_user = ""
    
    async def on_ready(self):
        print(f"{self.user} is ready and online!")



