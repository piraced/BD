import discord
import src.db_operations as db
import src.ui.battle_view


class Battle_commands(discord.ext.commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.slash_command(name = "start_encounter", description = "Command to start an encounter in the current channel")
    @discord.commands.default_permissions(administrator=True)
    async def start_encounter(self, ctx: discord.ApplicationContext, encounter: discord.Option(str)):
        if(db.get_selected_ruleset(ctx.guild_id) is None):
            await ctx.respond("Please select a ruleset first", ephemeral=True)
        elif(db.get_ruleset(db.get_selected_ruleset(ctx.guild_id)["name"], ctx.guild_id)["initiative_formula"] == ""):
            await ctx.respond("Please setup the ruleset combat configuration first", ephemeral=True)
        else:

            characters = [{"name" : "test", "length_coord" : 3, "height_coord" : 3}, {"name" : "warrior", "length_coord" : 3, "height_coord" : 5}]
            view = src.ui.battle_view.Battle_view(encounter_name=encounter, server_id=ctx.guild_id, characters=characters)
            await ctx.respond("Start the encounter", view=view)









def setup(bot):
    bot.add_cog(Battle_commands(bot))