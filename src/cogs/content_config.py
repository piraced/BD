import discord
import src.db_operations as db
import src.ui.content_config_view
import src.ui.rule_config_view
import src.ui.admin_config_view

class Content_config(discord.ext.commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.slash_command(name = "content_config", description = "Command to call up the ruleset management interface in the current channel")
    @discord.commands.default_permissions(administrator=True)
    async def content_config(self, ctx: discord.ApplicationContext, content_type: discord.Option(str, choices=['items', 'abilities', 'effects', 'characters', 'creatures'])):
        if(db.get_selected_ruleset(ctx.guild_id) is None):
            await ctx.respond("Please select a ruleset first", ephemeral=True)
            return
        
        view = src.ui.content_config_view.Content_config_view(str(content_type), ctx.guild_id)

        await ctx.respond("list of all " + str(content_type) + " for the current ruleset - " + db.get_selected_ruleset(ctx.guild_id)["name"], view=view, ephemeral=True)

    @discord.slash_command(name = "rule_config", description = "Command to call up the ruleset management interface in the current channel")
    @discord.commands.default_permissions(administrator=True)
    async def rule_config(self, ctx:discord.ApplicationContext):
        view = src.ui.rule_config_view.Rule_config_view(ctx.guild_id)

        await ctx.respond("Select a ruleset", view=view, ephemeral=True)


    @discord.slash_command(name = "admin_config", description= "Command to call up the main admin management interface in the current channel")
    @discord.commands.default_permissions(administrator=True)
    async def admin_config(self, ctx: discord.ApplicationContext):
        view = src.ui.admin_config_view.Admin_config_view(ctx.guild_id)

        await ctx.respond("Admin configuration panel", view=view, ephemeral=True)

    @discord.user_command(name="Assign character")
    async def assign_character(self, ctx: discord.ApplicationContext, member: discord.Member):
        view = src.ui.content_config_view.Content_config_view("characters", ctx.guild_id, alt_mode=2, assign_user=member)

        await ctx.respond("list of all characters for the current ruleset - " + db.get_selected_ruleset(ctx.guild_id)["name"] + "\n Selected character will be assigned to: " + member.display_name, view=view, ephemeral=True)



def setup(bot):
    bot.add_cog(Content_config(bot))