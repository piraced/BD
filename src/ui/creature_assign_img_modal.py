import discord
import src.db_operations as db
import src.utils

class Creature_assign_img_modal(discord.ui.Modal):
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
        self.get_creature_values()


        self.add_item(discord.ui.InputText(label="Creature name", placeholder="Creature name (leave empty when saving to delete creature)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Creature description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Creature image", placeholder=self.image_placeholder, value=self.image))


    async def callback(self, interaction: discord.Interaction):
        token = src.utils.get_image_token(self.children[2].value)

        ####If name field is empty delete creature being modified
        if self.children[0].value == "":
            db.delete_object("creatures", self.name, interaction.guild_id)
            msg = f"Creature {self.name} deleted sucessfully"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if a creature with that name already exists
        elif db.does_object_exist_in_ruleset("creatures", self.children[0].value, interaction.guild_id) and  self.children[0].value != self.name:
            msg = "a creature with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if name contains spaces
        elif " " in self.children[0].value:
            msg = "A creatures name cannot contain spaces"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if the token generated
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
                "token" : token
            }
            db.replace_object("creatures", self.name, interaction.guild_id, document)
            msg = f"Creature {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_creature_values(self):
        creature = db.get_object("creatures", self.title[:-9], self.server_id)
        self.name = creature['name']
        self.description = creature['description']
        self.stats = creature['statistics']
        self.abilities = creature['abilities']
        self.effects = creature['effects']
        self.image = creature['image']
        self.token = creature['token']

