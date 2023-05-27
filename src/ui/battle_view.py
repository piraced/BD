import discord
from discord.interactions import Interaction
import src.db_operations as db
import src.classes.battle
import src.utils
from openpyxl.utils.cell import get_column_letter




class Battle_view(discord.ui.View):


    def __init__(self, encounter_name, server_id, characters):
        super().__init__(timeout=None)
        self.server_id = server_id
        self.thread = None
        self.ability_page = 1

        encounter_data = db.get_object("encounters", encounter_name, self.server_id)
        self.battle = src.classes.battle.Battle(encounter_data, self.server_id, characters)



        ###This block is here because I need an interaction to edit the message
        async def start_button_callback(interaction:discord.Interaction):
            self.add_ui()
            self.remove_item(start_button)
            channel = interaction.channel
            message = await channel.send("Encounter logs")
            self.thread = await message.create_thread(name="Encounter logs", auto_archive_duration=60)
            self.battle.thread = self.thread
            await self.battle.initialize_char_turn()
            await self.battle.initiative_logs()
            await self.update_view(interaction)
        start_button = discord.ui.Button(label="Start", style=discord.ButtonStyle.green)
        start_button.callback = start_button_callback
        self.add_item(start_button)


    def add_ui(self):
        ##########character info button
        async def info_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                msg = await self.character_info(interaction, self.battle.get_current_entity())
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

        info_button = discord.ui.Button(emoji="ℹ", style=discord.ButtonStyle.gray, row=0)
        info_button.callback = info_button_callback
        self.add_item(info_button)

        ##########up button
        async def up_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                if self.battle.ability_mode:
                    self.battle.active_ability.y = self.battle.active_ability.y - 1
                    self.battle.active_ability.speed = self.battle.active_ability.speed - 1
                else:
                    self.battle.get_current_entity().y = self.battle.get_current_entity().y - 1
                    self.battle.get_current_entity().speed = self.battle.get_current_entity().speed - 1

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)
                
        up_button = discord.ui.Button(emoji="🔼", style=discord.ButtonStyle.blurple, row=0, custom_id="up_button")
        up_button.callback = up_button_callback
        self.add_item(up_button)

        ##########undo move button
        async def undo_move_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                if self.battle.ability_mode == False:
                    self.battle.get_current_entity().x = self.battle.current_char_actual_x
                    self.battle.get_current_entity().y = self.battle.current_char_actual_y
                    self.battle.get_current_entity().speed = self.battle.current_char_actual_moves
                else:
                    self.battle.ability_mode = False

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

        undo_move_button = discord.ui.Button(emoji="↩", style=discord.ButtonStyle.gray, row=0, custom_id="undo_move_button")
        undo_move_button.callback = undo_move_button_callback
        self.add_item(undo_move_button)

        ##########left button
        async def left_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                if self.battle.ability_mode:
                    self.battle.active_ability.x = self.battle.active_ability.x - 1
                    self.battle.active_ability.speed = self.battle.active_ability.speed - 1
                else:
                    self.battle.get_current_entity().x = self.battle.get_current_entity().x - 1
                    self.battle.get_current_entity().speed = self.battle.get_current_entity().speed - 1

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)
                
        left_button = discord.ui.Button(emoji="◀", style=discord.ButtonStyle.blurple, row=1, custom_id="left_button")
        left_button.callback = left_button_callback
        self.add_item(left_button)

        ##########confirm button
        async def confirm_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                await self.battle.confirm_move()

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

                
        confirm_button = discord.ui.Button(emoji="✅", style=discord.ButtonStyle.green, row=1, custom_id="confirm_button")
        confirm_button.callback = confirm_button_callback
        self.add_item(confirm_button)

        ##########right button
        async def right_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                if self.battle.ability_mode:
                    self.battle.active_ability.x = self.battle.active_ability.x + 1
                    self.battle.active_ability.speed = self.battle.active_ability.speed - 1
                else:
                    self.battle.get_current_entity().x = self.battle.get_current_entity().x + 1
                    self.battle.get_current_entity().speed = self.battle.get_current_entity().speed - 1

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)
                
        right_button = discord.ui.Button(emoji="▶", style=discord.ButtonStyle.blurple, row=1, custom_id="right_button")
        right_button.callback = right_button_callback
        self.add_item(right_button)

        ##########bottom left blank button
        bottom_left_blank_button = discord.ui.Button(emoji="⬛", style=discord.ButtonStyle.gray, disabled=True, row=2)
        self.add_item(bottom_left_blank_button)

        ##########down button
        async def down_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                if self.battle.ability_mode:
                    self.battle.active_ability.y = self.battle.active_ability.y + 1
                    self.battle.active_ability.speed = self.battle.active_ability.speed - 1
                else:
                    self.battle.get_current_entity().y = self.battle.get_current_entity().y + 1
                    self.battle.get_current_entity().speed = self.battle.get_current_entity().speed - 1

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)
                
        down_button = discord.ui.Button(emoji="🔽", style=discord.ButtonStyle.blurple, row=2, custom_id="down_button")
        down_button.callback = down_button_callback
        self.add_item(down_button)

        ##########end turn button
        async def end_turn_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                ### If lots of enemies died the turn might take too long
                await interaction.response.defer()

                await self.battle.end_turn()

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

        end_turn_button = discord.ui.Button(label="End turn", style=discord.ButtonStyle.gray, row=2, custom_id="end_turn_button")
        end_turn_button.callback = end_turn_button_callback
        self.add_item(end_turn_button)

        #### Abilities 1-5
        ability_buttons_1 = [self.Ability_button(style=discord.ButtonStyle.gray, disabled=True, server_id=self.server_id, row=3, battle=self.battle, custom_id="ability_button_" + str(i)) for i in range(5)]
        for button in ability_buttons_1:
            self.add_item(button)

        #### Previous ability page
        async def ability_previous_page_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                self.ability_page = self.ability_page - 1
                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

        ability_previous_page_button = discord.ui.Button(label="", emoji="⏪", style=discord.ButtonStyle.gray, row=4, custom_id="ability_previous_page_button")
        ability_previous_page_button.callback = ability_previous_page_button_callback
        self.add_item(ability_previous_page_button)

        #### Abilities 6-8
        ability_button_5 = self.Ability_button(style=discord.ButtonStyle.gray, disabled=True, server_id=self.server_id, row=4, battle=self.battle, custom_id="ability_button_5")
        ability_button_6 = self.Ability_button(style=discord.ButtonStyle.gray, disabled=True, server_id=self.server_id, row=4, battle=self.battle, custom_id="ability_button_6")
        ability_button_7 = self.Ability_button(style=discord.ButtonStyle.gray, disabled=True, server_id=self.server_id, row=4, battle=self.battle, custom_id="ability_button_7")
        self.add_item(ability_button_5)
        self.add_item(ability_button_6)
        self.add_item(ability_button_7)

        #### Next ability page
        async def ability_next_page_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                self.ability_page = self.ability_page + 1
                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

        ability_next_page_button = discord.ui.Button(label="", emoji="⏩", style=discord.ButtonStyle.gray, row=4, custom_id="ability_next_page_button")
        ability_next_page_button.callback = ability_next_page_button_callback
        self.add_item(ability_next_page_button)


    async def update_view(self, interaction:discord.Interaction):

        ### Get player nick / write DM if monster
        if self.battle.get_current_entity().player_id != 0:
            id = self.battle.get_current_entity().player_id
            member = await interaction.guild.fetch_member(id)
            player_msg = "(" + member.display_name + ")"
        else:
            player_msg = "(DM)"


        msg = f"Turn: {self.battle.turn}\nCurrently its turn for: {self.battle.get_current_entity().name} {player_msg}\nLocation: {get_column_letter(self.battle.get_current_entity().x)}{self.battle.get_current_entity().y}\nMovement points: {self.battle.get_current_entity().speed}"

        if self.battle.ability_mode:
            msg = msg + f"\n Active ability: {self.battle.active_ability.name}\n"
            if self.battle.active_ability.type == "single":
                msg = msg + "Remaining range: " + str(self.battle.active_ability.speed)

        #### clear ability data if not in ability mode
        if not self.battle.ability_mode:
            self.battle.active_ability = None

        #### Set buttons to their default disabled state
        self.get_item("up_button").disabled = False
        self.get_item("left_button").disabled = False
        self.get_item("right_button").disabled = False
        self.get_item("down_button").disabled = False
        self.get_item("undo_move_button").disabled = False

        self.get_item("ability_next_page_button").disabled = False
        self.get_item("ability_previous_page_button").disabled = False

        for index in range(0, 8):
            self.get_item("ability_button_" + str(index)).disabled = True

        ####Disbale buttons if moving would put token out of bounds
        if self.battle.get_current_entity().x == 1:
            self.get_item("left_button").disabled = True
        if self.battle.get_current_entity().x == int(self.battle.map_length):
            self.get_item("right_button").disabled = True
        if self.battle.get_current_entity().y == 1:
            self.get_item("up_button").disabled = True
        if self.battle.get_current_entity().y == int(self.battle.map_height):
            self.get_item("down_button").disabled = True

        ###Disable buttons if moving would cause a collision
        coords = await self.get_entity_coords()
        if ([self.battle.get_current_entity().x - 1, self.battle.get_current_entity().y] in coords) and not self.battle.ability_mode:
            self.get_item("left_button").disabled = True
        if ([self.battle.get_current_entity().x + 1, self.battle.get_current_entity().y] in coords) and not self.battle.ability_mode:
            self.get_item("right_button").disabled = True
        if ([self.battle.get_current_entity().x, self.battle.get_current_entity().y - 1] in coords) and not self.battle.ability_mode:
            self.get_item("up_button").disabled = True
        if ([self.battle.get_current_entity().x, self.battle.get_current_entity().y + 1] in coords) and not self.battle.ability_mode:
            self.get_item("down_button").disabled = True

        #####Disable buttons if out of movement points
        if (self.battle.get_current_entity().speed == 0 and not self.battle.ability_mode) or (self.battle.ability_mode and self.battle.active_ability.speed == 0):
            self.get_item("up_button").disabled = True
            self.get_item("left_button").disabled = True
            self.get_item("right_button").disabled = True
            self.get_item("down_button").disabled = True

        #### Disable ability page buttons if they would go out of needed range
        if self.battle.ability_pages == self.ability_page:
            self.get_item("ability_next_page_button").disabled = True
        if self.ability_page == 1:
            self.get_item("ability_previous_page_button").disabled = True


        ### Set ability button labels
        for index in range(0, 8):
            if (len(self.battle.ability_labels) > self.ability_page * 8 - 8 + index):
                self.get_item("ability_button_" + str(index)).label = self.battle.ability_labels[self.ability_page * 8 - 8 + index]
            else:
                self.get_item("ability_button_" + str(index)).label = "None"
            if [self.battle.current_char_actual_x, self.battle.current_char_actual_y] == [self.battle.get_current_entity().x, self.battle.get_current_entity().y] and not self.battle.ability_mode and not self.battle.current_char_ability_used and self.get_item("ability_button_" + str(index)).label != "None":
                self.get_item("ability_button_" + str(index)).disabled = False

        if (self.battle.current_char_moved == True and not self.battle.ability_mode) or (self.battle.current_char_ability_used == True and self.battle.ability_mode):
            self.get_item("undo_move_button").disabled = True

        #### End the battle
        end = self.check_for_end()
        if isinstance(end, str):
            msg = end
        

        battlemap = src.utils.map_url_constructor(self.battle.map, self.battle.entities, self.battle.active_ability, [self.battle.get_current_entity().x, self.battle.get_current_entity().y])
        e = discord.Embed()
        e.set_image(url=battlemap)

        if interaction.response.is_done():
            await interaction.followup.edit_message(message_id=interaction.message.id,content=msg,embed=e,view=self)
        else:
            await interaction.response.edit_message(content=msg,embed=e,view=self)


    def check_for_end(self):
        players = 0
        enemies = 0

        for entity in self.battle.entities:
            if entity.player_id == 0:
                enemies = enemies + 1
            else:
                players = players + 1

        if players == 0 or enemies == 0:
            self.disable_all_items()
            if players == 0:
                winner = "creatures"
            else:
                winner = "players"
            return f"The encounter is over. The {winner} won"
        else:
            return False

    async def get_entity_coords(self):
        coords = []
        for entity in self.battle.entities:
            if [entity.x, entity.y] != [self.battle.get_current_entity().x, self.battle.get_current_entity().y]:
                coords.append([entity.x, entity.y])
        return coords

    async def character_info(self, interaction: discord.Interaction, entity):

        stats = db.get_ruleset(db.get_selected_ruleset(interaction.guild_id)["name"], interaction.guild_id)["statistics"]
        if entity.player_id != 0:
            player = await interaction.guild.fetch_member(entity.player_id)
            player_nick = player.display_name
        else:
            player_nick = "DM"

        msg = f"**Character information for: {entity.name}({player_nick})**\n\n**Statistics:**\n\n"

        for stat in stats:
            msg = msg + stat + ": " + str(entity.statistics[stat]["value"]) + "/" + str(entity.statistics[stat]["max"]) + "\n"

        msg = msg + "\n**Abilities:**\n"

        for ability in entity.abilities:

            msg = msg + "**\n" + ability.name + "**\n\n" + ability.description + "\n\nability type: " + ability.type + "\nrange: " + str(ability.range) + "\n"
            if ability.type == "cone":
                msg = msg + "cone width: " + str(ability.range[1]) + "\n"

            msg = msg + "\nAbility cost:\n"
            for self_effect_name in ability.self_effects:
                effect = db.get_object("effects", self_effect_name, interaction.guild_id)
                msg = msg + effect["name"] + ":\n"
                for formula in effect["formulas"]:
                    msg = msg + formula + "\n"

            msg = msg + "\nAbility effects:\n"
            for effect_name in ability.effects:
                effect = db.get_object("effects", effect_name, interaction.guild_id)
                msg = msg + effect["name"] + ":\n"
                for formula in effect["formulas"]:
                    msg = msg + formula + "\n"
            
        msg = msg + "\n**Effects:**\n\n"

        for effect in entity.effects:
            msg = msg + effect.name + "\nRemaining duration: " + str(effect.duration) + "\nUndoes effects on expiry: " + str(effect.undoes_itself) + "\nFormulas:\n"

            for formula in effect.formulas:
                msg = msg + formula + "\n"

        return msg
    

    class Ability_button(discord.ui.Button):
        def __init__(self, style, disabled, custom_id, server_id, row, battle):
            super().__init__(label="None", style=style, disabled=disabled, custom_id=custom_id, row=row)
            self.server_id = server_id
            self.battle = battle
            self.ability = None


        async def callback(self, interaction: Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
                for ability in self.battle.get_current_entity().abilities:
                    if ability.name == self.label:
                        self.ability = ability
                        self.battle.active_ability = self.ability
                        self.battle.ability_mode = True
                        self.battle.active_ability.x = self.battle.get_current_entity().x
                        self.battle.active_ability.y = self.battle.get_current_entity().y
                        
                        match ability.type:
                            case "single":
                                self.battle.active_ability.speed = int(ability.range)
                            case "area":
                                self.battle.active_ability.speed = 0
                            case _:
                                self.battle.active_ability.speed = 9999
                        
                        await self._view.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)