import discord
import src.db_operations as db
import src.ui.rule_config_view
import src.ui.content_config_view
import src.ui.ruleset_combat_config_modal





class Admin_config_view(discord.ui.View):


    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id
        self.add_buttons()



    def add_buttons(self):

        ##########ruleset config button
        async def ruleset_config_button_callback(interaction: discord.Interaction):
            view = src.ui.rule_config_view.Rule_config_view(interaction.guild_id)
            await interaction.response.edit_message(content="select a ruleset", view=view)
            
        ruleset_config_button = discord.ui.Button(label="Ruleset configuration", style=discord.ButtonStyle.gray)
        ruleset_config_button.callback = ruleset_config_button_callback
        self.add_item(ruleset_config_button)

        ##########ruleset combat config button
        async def ruleset_combat_config_button_callback(interaction: discord.Interaction):
            modal = src.ui.ruleset_combat_config_modal.Ruleset_combat_config_modal(title = "Ruleset combat configuration",server_id=interaction.guild_id)
            await interaction.response.send_modal(modal=modal)
            
        ruleset_combat_config_button = discord.ui.Button(label="Ruleset combat configuration", style=discord.ButtonStyle.gray)
        ruleset_combat_config_button.callback = ruleset_combat_config_button_callback
        self.add_item(ruleset_combat_config_button)

        ##########effect config button
        async def effect_config_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("effects", interaction.guild_id)
            await interaction.response.edit_message(content="list of all effects for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        effect_config_button = discord.ui.Button(label="Effect configuration", style=discord.ButtonStyle.gray)
        effect_config_button.callback = effect_config_button_callback
        self.add_item(effect_config_button)

        ##########ability config button
        async def ability_config_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("abilities", interaction.guild_id)
            await interaction.response.edit_message(content="list of all abilities for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        ability_config_button = discord.ui.Button(label="Ability configuration", style=discord.ButtonStyle.gray)
        ability_config_button.callback = ability_config_button_callback
        self.add_item(ability_config_button)

        ##########item config button
        async def item_config_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("items", interaction.guild_id)
            await interaction.response.edit_message(content="list of all items for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        item_config_button = discord.ui.Button(label="Item configuration", style=discord.ButtonStyle.gray)
        item_config_button.callback = item_config_button_callback
        self.add_item(item_config_button)

        ##########Creature config button
        async def creature_config_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("creatures", interaction.guild_id)
            await interaction.response.edit_message(content="list of all creatures for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        creature_config_button = discord.ui.Button(label="Creature configuration", style=discord.ButtonStyle.gray)
        creature_config_button.callback = creature_config_button_callback
        self.add_item(creature_config_button)

        ##########Creature add image button
        async def creature_assign_img_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("creatures", server_id= interaction.guild_id, alt_mode=True)
            await interaction.response.edit_message(content="list of all creatures for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        creature_assign_img_button = discord.ui.Button(label="Assign image to creature", style=discord.ButtonStyle.gray)
        creature_assign_img_button.callback = creature_assign_img_button_callback
        self.add_item(creature_assign_img_button)

        ##########Character config button
        async def character_config_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("characters", interaction.guild_id)
            await interaction.response.edit_message(content="list of all characters for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        character_config_button = discord.ui.Button(label="Character configuration", style=discord.ButtonStyle.gray)
        character_config_button.callback = character_config_button_callback
        self.add_item(character_config_button)

        ##########Creature add image button
        async def character_assign_img_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("characters", server_id= interaction.guild_id, alt_mode=True)
            await interaction.response.edit_message(content="list of all characters for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        character_assign_img_button = discord.ui.Button(label="Assign image to character", style=discord.ButtonStyle.gray)
        character_assign_img_button.callback = character_assign_img_button_callback
        self.add_item(character_assign_img_button)

        ##########Map config button
        async def map_config_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("maps", server_id= interaction.guild_id)
            await interaction.response.edit_message(content="list of all maps for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        map_config_button = discord.ui.Button(label="Map configuration", style=discord.ButtonStyle.gray)
        map_config_button.callback = map_config_button_callback
        self.add_item(map_config_button)

        ##########Encounter config button
        async def encounter_config_button_callback(interaction: discord.Interaction):
            view = src.ui.content_config_view.Content_config_view("encounters", server_id= interaction.guild_id)
            await interaction.response.edit_message(content="list of all encounters for the current ruleset - " + db.get_selected_ruleset(interaction.guild_id)["name"], view=view)

        encounter_config_button = discord.ui.Button(label="Encounter configuration", style=discord.ButtonStyle.gray)
        encounter_config_button.callback = encounter_config_button_callback
        self.add_item(encounter_config_button)


