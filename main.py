import os
from src.db_operations import initialize_database
from dotenv import load_dotenv
from src.bot import TTRPGbot

cogs_list = [
    "content_config",
    "use_commands"
]

load_dotenv()
bot = TTRPGbot()
initialize_database()



@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")


for cog in cogs_list:
    bot.load_extension(f'src.cogs.{cog}')

bot.run(os.getenv('TOKEN'))



######## There is no collision between tokens in battle
########