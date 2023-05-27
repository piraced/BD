import discord
import src.db_operations as db
import src.utils

class Character_assign_img_modal(discord.ui.Modal):
    name=""
    description=""
    stats=""
    abilities=""
    effects=""
    image=""
    token=""

    image_placeholder="link to a small(less than 160x160px or less) image, must start with http(s) eg: https://imgur.com/"

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id
        self.get_character_values()


        self.add_item(discord.ui.InputText(label="Character name", placeholder="Character name (leave empty when saving to delete the character)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Character description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Character image", placeholder=self.image_placeholder, value=self.image))


    async def callback(self, interaction: discord.Interaction):
        token = src.utils.get_image_token(self.children[2].value)

        ####If name field is empty delete character being modified
        if self.children[0].value == "":
            db.delete_object("characters", self.name, interaction.guild_id)
            msg = f"Character {self.name} deleted sucessfully"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if a character with that name already exists
        elif db.does_object_exist_in_ruleset("characters", self.children[0].value, interaction.guild_id) and  self.children[0].value != self.name:
            msg = "a character with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if name contains spaces
        elif " " in self.children[0].value:
            msg = "A characters name cannot contain spaces"
            await interaction.response.send_message(msg, ephemeral=True)
        elif isinstance(token, bool):
            msg = "Failed to generate image token. Perhaps the url is incorrect or the image is bigger than 160x160px"
            await interaction.response.send_message(msg, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "statistics" : self.stats,
                "abilities" : self.abilities,
                "effects" : self.effects,
                "image" : self.children[2].value,
                "token" : token,
                "player" : self.player
            }
            db.replace_object("characters", self.name, interaction.guild_id, document)
            msg = f"Character {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_character_values(self):
        character = db.get_object("characters", self.title[:-10], self.server_id)
        self.name = character['name']
        self.description = character['description']
        self.stats = character['statistics']
        self.abilities = character['abilities']
        self.effects = character['effects']
        self.image = character['image']
        self.token = character['token']
        self.player = character['player']

