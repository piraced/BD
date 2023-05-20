import discord
import src.db_operations as db
import src.ui.battle_view
import src.ui.content_config_view


class Use_commands(discord.ext.commands.Cog):

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


    @discord.slash_command(name = "macros", description = "Bring up the macro selection")
    async def use_macros(self, ctx: discord.ApplicationContext):
        char = db.get_character_by_player(ctx.user.id, ctx.guild_id)
        if char is None:
            await ctx.respond("There is no character assigned to you. Ask an administrator to assign a character first.", ephemeral=True)
        else:
            view = src.ui.content_config_view.Content_config_view("macros", ctx.guild_id, alt_mode=2, assign_user=ctx.user)
            await ctx.respond("List of available macros", view=view, ephemeral=True)

    @discord.slash_command(name= "character_info", description= "Shows the information of your assigned character")
    async def character_info(self, ctx: discord.ApplicationContext):
        char = db.get_character_by_player(ctx.user.id, ctx.guild_id)
        if char is None:
            await ctx.respond("There is no character assigned to you. Ask an administrator to assign a character first.", ephemeral=True)
        else:
            stats = db.get_ruleset(db.get_selected_ruleset(ctx.guild_id)["name"], ctx.guild_id)["statistics"]
            abilities = []

            for ability in char["abilities"]:
                abilities.append(db.get_object("abilities", ability, ctx.guild_id))

            ## Dont seem to be able to use dict type objects in f-strings
            char_name = char["name"]
            player_nick = ctx.user.display_name

            msg = f"Character information for: {char_name}({player_nick})\n\nStatistics:\n\n"

            for stat in stats:
                msg = msg + stat + ": " + char["statistics"][stat]["value"] + "/" + char["statistics"][stat]["max"] + "\n"

            msg = msg + "\nAbilities:\n\n"

            for ability in abilities:

                msg = msg + ability["name"] + "\n\n" + ability["description"] + "\n\nability type: " + ability["type"] + "\nrange: " + ability["range"][0] + "\n"
                if ability["type"] == "cone":
                    msg = msg + "cone width: " + ability["range"][1] + "\n"
                msg = msg + "\nAbility effects:\n"
                
                for effect_name in ability["effects"]:
                    effect = db.get_object("effects", effect_name, ctx.guild_id)
                    msg = msg + effect["name"] + ":\n"
                    for formula in effect["formulas"]:
                        msg = msg + formula + "\n"
            
            await ctx.respond(msg, ephemeral=True)









def setup(bot):
    bot.add_cog(Use_commands(bot))