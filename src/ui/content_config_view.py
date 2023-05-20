import discord
import d20
import src.ui.macro_config_modal
import src.ui.ability_config_modal
import src.ui.effect_config_modal
import src.ui.creature_config_modal
import src.ui.character_config_modal
import src.ui.creature_assign_img_modal
import src.ui.character_assign_img_modal
import src.ui.map_config_modal
import src.ui.encounter_config_modal
import src.db_operations as db
import src.utils



class Content_config_view(discord.ui.View):
    page = 1
    alt_mode=0

    def __init__(self, content_type, server_id, alt_mode=0, assign_user=None):
        super().__init__(timeout=None)
        self.content_type = content_type
        self.server_id = server_id
        self.alt_mode = alt_mode
        self.assign_user = assign_user
        self.add_buttons()
        self.update_view(server_id)

        ### a bit hacky way to disabled the return to admin config menu button
        ### should be fine since this is the only way of a regular user getting to this view
        if content_type == "macros" and alt_mode == 2:
            self.get_item("return_button").disabled = True

    def add_buttons(self):

        ###########Content buttons
        buttons = [self.Content_button(label="Empty", style=discord.ButtonStyle.gray, disabled=True, server_id=self.server_id, content_type=self.content_type, alt_mode=self.alt_mode, assign_user=self.assign_user, custom_id="content_config_button_" + str(i)) for i in range(20)]
        for button in buttons:
            self.add_item(button)

        ####back to main settings button
        async def return_button_callback(interaction:discord.Interaction):
            view = src.ui.admin_config_view.Admin_config_view(interaction.guild_id)
            await interaction.response.edit_message(content="Admin configuration panel", view=view)

        return_button = discord.ui.Button(label="", emoji="↩", style=discord.ButtonStyle.gray, row=4, custom_id="return_button")
        return_button.callback = return_button_callback
        self.add_item(return_button)

        ##########Previous page button
        async def back_page_button_callback(interaction: discord.Interaction):
            page = page - 1
            self.update_view(interaction.guild_id)
            await interaction.response.edit_message(view=self)
            

        back_page_button = discord.ui.Button(label="", style=discord.ButtonStyle.blurple, emoji="◀", disabled=True, custom_id="back_page_button")
        back_page_button.callback = back_page_button_callback
        self.add_item(back_page_button)

        ###########Current page number button
        page_num_button = discord.ui.Button(label=self.page, disabled=True, style=discord.ButtonStyle.green, custom_id="page_num_button")
        self.add_item(page_num_button)

        ###########Next page button
        async def forward_page_button_callback(interaction: discord.Interaction):
            page = page + 1
            self.update_view(interaction.guild_id)
            await interaction.response.edit_message(view=self)

        forward_page_button = discord.ui.Button(label="", style=discord.ButtonStyle.blurple, emoji="▶", disabled=True, custom_id="forward_page_button")
        forward_page_button.callback = forward_page_button_callback
        self.add_item(forward_page_button)
    
        ############Refresh button
        async def refresh_button_callback(interaction: discord.Interaction):
            self.update_view(interaction.guild_id)
            await interaction.response.edit_message(view=self)
        
        refresh_button = discord.ui.Button(label="", style=discord.ButtonStyle.gray, emoji="🔁", disabled=False, custom_id="refresh_button")
        refresh_button.callback = refresh_button_callback
        self.add_item(refresh_button)
    

    def update_view(self, server_id):
        content_list = list(db.get_all_objects(self.content_type, server_id))
        self.labels = [obj["name"] for obj in content_list]
        appended = False
        min_index = self.page * 20 - 20
        max_index = self.page * 20

        if self.page == 1:
            self.get_item("back_page_button").disabled = True
        else:
            self.get_item("back_page_button").disabled = False
        self.get_item("page_num_button").label = self.page

        if max_index >= len(self.labels):
            self.labels.append("New")
            appended = True
            labels_to_use = self.labels[min_index:]
            self.get_item("forward_page_button").disabled = True
        else:
            labels_to_use = self.labels[min_index:max_index]
            self.get_item("forward_page_button").disabled = False

        for index in range(20):
            self.get_item("content_config_button_" + str(index)).style = discord.ButtonStyle.gray
            if index < len(labels_to_use):
                self.get_item("content_config_button_" + str(index)).label= labels_to_use[index]
                self.get_item("content_config_button_" + str(index)).disabled = False
                if labels_to_use[index] == "New":
                    self.get_item("content_config_button_" + str(index)).style = discord.ButtonStyle.green
                    if self.alt_mode != 0:
                        self.get_item("content_config_button_" + str(index)).disabled = True
            else:
                self.get_item("content_config_button_" + str(index)).label= "Empty"
                self.get_item("content_config_button_" + str(index)).disabled = True

        if appended == True:
            self.labels.pop()




    class Content_button(discord.ui.Button):
        def __init__(self, label:str, style:discord.ButtonStyle, disabled:bool, custom_id:str, content_type:str, server_id, alt_mode, assign_user=None):
            super().__init__(label=label, style=style, disabled=disabled, custom_id=custom_id)
            self.content_type = content_type
            self.server_id = server_id
            self.alt_mode = alt_mode
            self.assign_user = assign_user

        async def callback(self, interaction:discord.Interaction):
            if self.alt_mode != 2:
                await interaction.response.send_modal(self.modal_selector())
            else:
                match self.content_type:
                    case 'characters':
                        msg = self.assign_character(self.assign_user, interaction.guild_id, str(self.label))
                        message_id = interaction.message.id
                        await interaction.response.send_message(msg, ephemeral=True)
                        await interaction.followup.delete_message(message_id)
                    case 'macros':
                        msg = self.run_macro(self.assign_user, self.server_id, str(self.label))
                        await interaction.response.send_message(msg)


        def modal_selector(self):
            if self.alt_mode == 0:
                match self.content_type:
                    case 'macros':
                        modal = src.ui.macro_config_modal.Macro_config_modal(title= str(self.label) + " macro", server_id= self.server_id)
                    case 'abilities':
                        modal = src.ui.ability_config_modal.Ability_config_modal(title= str(self.label) + " ability", server_id= self.server_id)
                    case'effects':
                        modal = src.ui.effect_config_modal.Effect_config_modal(title= str(self.label) + " effect", server_id= self.server_id)
                    case 'characters':
                        modal = src.ui.character_config_modal.Character_config_modal(title = str(self.label) + " character", server_id= self.server_id)
                    case 'creatures':
                        modal = src.ui.creature_config_modal.Creature_config_modal(title = str(self.label) + " creature", server_id= self.server_id)
                    case 'maps':
                        modal = src.ui.map_config_modal.Map_config_modal(title = str(self.label) + " map", server_id= self.server_id)
                    case 'encounters':
                        modal = src.ui.encounter_config_modal.Encounter_config_modal(title = str(self.label) + " encounter", server_id= self.server_id)
            elif self.alt_mode == 1:
                match self.content_type:
                    case 'characters':
                        modal = src.ui.character_assign_img_modal.Character_assign_img_modal(title = str(self.label) + " character", server_id= self.server_id)
                    case 'creatures':
                        modal = src.ui.creature_assign_img_modal.Creature_assign_img_modal(title = str(self.label) + " creature", server_id= self.server_id)
                        
            return modal

        def assign_character(self, user, server_id, character_name):
            db.reset_character_player(user.id, self.server_id)
            character = db.get_object("characters", character_name, server_id)
            character['player'] = user.id
            db.replace_object('characters', character_name, server_id, character)
            return "" + character_name +" is now assigned to: " + user.display_name

        def run_macro(self, user, server_id, macro_name):
            macro = db.get_object("macros", macro_name, server_id)
            character = db.get_character_by_player(user.id, server_id)
            stat_names = db.get_ruleset(db.get_selected_ruleset(server_id)["name"], server_id)["statistics"]
            dictionary = {}

            for stat in stat_names:
                dictionary[stat] = character["statistics"][stat]["value"]

            ### dont seem to be able to use dict type objects in f-strings
            character_name = character["name"]
            user_nick = user.display_name

            roll = d20.roll(src.utils.add_values_to_formula_string(dictionary, macro["formula"]))
            msg = f"{character_name}({user_nick}) used the {macro_name} macro:\n" + roll.result
            return msg


