import discord
import src.db_operations as db
import src.classes.battle
import src.utils
from openpyxl.utils.cell import get_column_letter




class Battle_view(discord.ui.View):


    def __init__(self, encounter_name, server_id, characters):
        super().__init__(timeout=None)
        self.server_id = server_id
        self.thread = None

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
        ##########top left blank button
        top_left_blank_button = discord.ui.Button(emoji="⬛", style=discord.ButtonStyle.gray, disabled=True, row=0)
        self.add_item(top_left_blank_button)

        ##########up button
        async def up_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
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
                self.battle.get_current_entity().x = self.battle.current_char_actual_x
                self.battle.get_current_entity().y = self.battle.current_char_actual_y
                self.battle.get_current_entity().speed = self.battle.current_char_actual_moves

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

        undo_move_button = discord.ui.Button(emoji="↩", style=discord.ButtonStyle.gray, row=0, custom_id="undo_move_button")
        undo_move_button.callback = undo_move_button_callback
        self.add_item(undo_move_button)

        ##########left button
        async def left_button_callback(interaction: discord.Interaction):
            if self.battle.get_current_entity().player_id == interaction.user.id or interaction.user.guild_permissions.administrator:
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
                await self.battle.end_turn()

                await self.update_view(interaction)
            else:
                await interaction.response.send_message("It is currently not your turn", ephemeral=True)

        end_turn_button = discord.ui.Button(label="End turn", style=discord.ButtonStyle.gray, row=2, custom_id="end_turn_button")
        end_turn_button.callback = end_turn_button_callback
        self.add_item(end_turn_button)


    async def update_view(self, interaction:discord.Interaction):
        if self.battle.get_current_entity().player_id != 0:
            id = self.battle.get_current_entity().player_id
            member = await interaction.guild.fetch_member(id)
            player_msg = "(" + member.display_name + ")"
        else:
            player_msg = "(DM)"


        msg = f"Turn: {self.battle.turn}\nCurrently its turn for: {self.battle.get_current_entity().name} {player_msg}\nLocation: {get_column_letter(self.battle.get_current_entity().x)}{self.battle.get_current_entity().y}\nMovement points: {self.battle.get_current_entity().speed}"

        self.get_item("up_button").disabled = False
        self.get_item("left_button").disabled = False
        self.get_item("right_button").disabled = False
        self.get_item("down_button").disabled = False
        self.get_item("undo_move_button").disabled = False

        ####Disbale buttons if moving would put token out of bounds
        if self.battle.get_current_entity().x == 1:
            self.get_item("left_button").disabled = True
        if self.battle.get_current_entity().x == self.battle.map_length:
            self.get_item("right_button").disabled = True
        if self.battle.get_current_entity().y == 1:
            self.get_item("up_button").disabled = True
        if self.battle.get_current_entity().y == self.battle.map_height:
            self.get_item("down_button").disabled = True

        #####Disable buttons if out of movement points
        if self.battle.get_current_entity().speed == 0:
            self.get_item("up_button").disabled = True
            self.get_item("left_button").disabled = True
            self.get_item("right_button").disabled = True
            self.get_item("down_button").disabled = True

        if self.battle.current_char_moved == True:
            self.get_item("undo_move_button").disabled = True

        battlemap = src.utils.map_url_constructor(self.battle.map, self.battle.entities)
        e = discord.Embed()
        e.set_image(url=battlemap)

        await interaction.response.edit_message(content=msg,embed=e,view=self)

        

