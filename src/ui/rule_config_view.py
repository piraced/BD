import discord
import src.db_operations as db
import src.ui.ruleset_edit_modal
import src.ui.admin_config_view





class Rule_config_view(discord.ui.View):

    ruleset_selection_remove_clicked = False

    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id
        self.add_ui()



    def add_ui(self):
        ###Ruleset select menu
        async def ruleset_select_menu_callback(interaction:discord.Interaction):
            self.ruleset_selection_remove_clicked = False
            if(ruleset_select_menu.values[0] == "Create a new ruleset"):
                self.get_item("remove_button").disabled = True
                self.get_item("select_button").disabled = True
                self.get_item("edit_button").label = "Create"
            else:
                self.get_item("remove_button").disabled = False
                self.get_item("select_button").disabled = False
                self.get_item("edit_button").label = "Edit"
            self.get_item("edit_button").disabled = False
            self.get_item("ruleset_select_menu").placeholder = ruleset_select_menu.values[0]
            self.get_item("remove_button").label = "Delete"
            await interaction.response.edit_message(view=self)

        ruleset_select_menu = discord.ui.Select(placeholder= "Select a ruleset", options= self.construct_ruleset_select_options(self.server_id), custom_id ="ruleset_select_menu" )
        ruleset_select_menu.callback = ruleset_select_menu_callback
        self.add_item(ruleset_select_menu)

        ####back to main settings button
        async def return_button_callback(interaction:discord.Interaction):
            view = src.ui.admin_config_view.Admin_config_view(interaction.guild_id)
            await interaction.response.edit_message(content="Admin configuration panel", view=view)

        return_button = discord.ui.Button(label="", emoji="↩", style=discord.ButtonStyle.gray, row=4, custom_id="return_button")
        return_button.callback = return_button_callback
        self.add_item(return_button)


        ####Delete ruleset button
        async def ruleset_delete_button_callback(interaction:discord.Interaction):
            if(self.ruleset_selection_remove_clicked == False):
                self.ruleset_selection_remove_clicked = True
                self.get_item("remove_button").label = "Click again to confirm"
            elif(self.ruleset_selection_remove_clicked == True):
                self.ruleset_selection_remove_clicked = False
                self.get_item("remove_button").label = "Delete"
                db.delete_ruleset(ruleset_select_menu.values[0], interaction.guild_id)
                ruleset_select_menu.options = self.construct_ruleset_select_options(interaction.guild_id)
            await interaction.response.edit_message(view=self)

        ruleset_delete_button = discord.ui.Button(label="Delete", style=discord.ButtonStyle.red, row=4, disabled=True, custom_id="remove_button")
        ruleset_delete_button.callback = ruleset_delete_button_callback
        self.add_item(ruleset_delete_button)

        ####Call edit ruleset modal
        async def ruleset_edit_button_callback(interaction: discord.Interaction):
            modal = src.ui.ruleset_edit_modal.Ruleset_modal(title=ruleset_select_menu.values[0], server_id=interaction.guild_id)
            await interaction.response.send_modal(modal=modal)
            self.construct_ruleset_select_options(interaction.guild_id)

        ruleset_edit_button = discord.ui.Button(label="Edit", style=discord.ButtonStyle.blurple, row=4, disabled=True, custom_id="edit_button")
        ruleset_edit_button.callback = ruleset_edit_button_callback
        self.add_item(ruleset_edit_button)

        ####Select current ruleset button
        async def ruleset_select_button_callback(interaction: discord.Interaction):
            db.select_ruleset(ruleset_select_menu.values[0], interaction.guild_id)
            await interaction.response.send_message("Active ruleset changed to " + ruleset_select_menu.values[0], ephemeral=True)
        
        ruleset_select_button = discord.ui.Button(label="Select", style=discord.ButtonStyle.green, row= 4, disabled=True, custom_id="select_button")
        ruleset_select_button.callback = ruleset_select_button_callback
        self.add_item(ruleset_select_button)

        ####Refresh ruleset view
        async def ruleset_refresh_button_callback(interaction: discord.Interaction):
            ruleset_select_menu.options = self.construct_ruleset_select_options(interaction.guild_id)
            await interaction.response.edit_message(view=self)

        ruleset_refresh_button = discord.ui.Button(label="", style=discord.ButtonStyle.gray, row= 4, custom_id="refresh_button", emoji="🔁")
        ruleset_refresh_button.callback = ruleset_refresh_button_callback
        self.add_item(ruleset_refresh_button)
    


    def construct_ruleset_select_options(self, server_id):
        options = db.get_rulesets(server_id)
        select_options = []
        if (len(options) < 5):
            options.append({"name" : "Create a new ruleset", "description" : "Create a new ruleset"})
        for item in options:
            select_options.append(discord.SelectOption(
                label = item['name'], description= item['description'][:100]
            ))
        return select_options