import discord
import src.db_operations as db
import src.utils
import src.ui.battle_view

class Encounter_start_modal(discord.ui.Modal):

    characters=""


    characters_placeholder = "Enter characters that will participate and their coords eg:\nMage 1 1"

    def __init__(self, server_id, encounter, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id
        self.encounter = encounter

        self.get_characters()

        self.add_item(discord.ui.InputText(label="Participating characters", placeholder=self.characters_placeholder, value=self.characters, required= True, style=discord.InputTextStyle.long))



    async def callback(self, interaction: discord.Interaction):
        characters = self.split_and_validate_characters()

        ####Check if macro with that name already exists
        if db.does_object_exist_in_ruleset("macros", self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "a macro with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        #### prind validation message
        elif isinstance(characters, str):
            await interaction.response.send_message(characters, ephemeral=True)
        else:        

            view = src.ui.battle_view.Battle_view(encounter_name=self.encounter, server_id=self.server_id, characters=characters)
            await interaction.response.send_message("Start the encounter", view=view)


    def get_characters(self):
        characters = db.get_all_objects("characters", self.server_id)
        for character in characters:
            if character["player"] != "":
                self.characters = self.characters + "\n" + character["name"]


    def split_and_validate_characters(self):
        characters = self.children[0].value.splitlines()
        rez = []

        for index, character in enumerate(characters, start=1):
            if character.count(" ") != 2:
                return f"Validation failed for character {index}: Each line must contain exactly 2 spaces"
            parts = character.split(" ")
            if not db.does_object_exist_in_ruleset("characters", parts[0], self.server_id):
                return f"Validation failed for character {index}: The character \"{parts[0]}\" does not exist"
            char_obj = db.get_object("characters", parts[0], self.server_id)
            if char_obj["player"] == "":
                return f"Validation failed for character {index}: The character \"{parts[0]}\" is not assigned to a player"
            
            for result in rez:
                if parts[1] == result["length_coord"] and parts[2] == result["height_coord"]:
                    overlap_name = result["name"]
                    return f"Validation failed for character {index}: The character \"{parts[0]}\" is in the same coordinates as {overlap_name}"
                
            encounter = db.get_object("encounters", self.encounter, self.server_id)

            for creature in encounter["creatures"]:
                if parts[1] == creature["length_coord"] and parts[2] == creature["height_coord"]:
                    overlap_name = creature["name"]
                    return f"Validation failed for character {index}: The character \"{parts[0]}\" is in the same coordinates as {overlap_name}"
                
            rez.append({"name": parts[0], "length_coord": parts[1], "height_coord": parts[2]})

        return rez

