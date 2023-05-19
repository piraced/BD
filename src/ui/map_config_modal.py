import discord
import src.db_operations as db
import src.utils

class Map_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    map_size=""
    grid_size=""
    image=""

    image_placeholder="link to an image of the map, must start with http/https eg: https://imgur.com/"

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id


        if(self.title!="New map"):
            self.get_map_values()
            self.new = False


        self.add_item(discord.ui.InputText(label="Map name", placeholder="Map name (leave empty when saving to delete the map)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Map description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Grid size", placeholder="Enter map square size in pixels. eg: 40", value=self.grid_size))
        self.add_item(discord.ui.InputText(label="Map size", placeholder="Enter map length and width in squares, one per line. eg:\n10\n15", value=self.map_size, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Map image", placeholder=self.image_placeholder, value=self.image))


    async def callback(self, interaction: discord.Interaction):
        is_img = src.utils.is_link_image(self.children[4].value)
        map_dim = self.children[3].value.splitlines()

        ####If name field is empty cancel map creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("maps", self.name, interaction.guild_id)
                msg = f"Map {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Map creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if a map with that name already exists
        elif db.does_object_exist_in_ruleset("maps", self.children[0].value, interaction.guild_id) and  self.children[0].value != self.name:
            msg = "a map with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        #### Check if grid size is a positive integer
        elif not self.children[2].value.isdigit() or int(self.children[2].value) < 1:
            msg = "The grid size must be a positive integer"
            await interaction.response.send_message(msg, ephemeral=True)
        #### Check if map length is a positive integer
        elif not map_dim[0].isdigit() or int(map_dim[0]) < 1:
            msg = "The map length (1st value in the map size field) must be a positive integer"
            await interaction.response.send_message(msg, ephemeral=True)
        #### Check if map height is a positive integer
        elif not map_dim[1].isdigit() or int(map_dim[1]) < 1:
            msg = "The map height (2nd value in the map size field) must be a positive integer"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if the link is to an image
        elif isinstance(is_img, bool) and is_img == False:
            msg = "The link entered in the Map image field does not link to an image (allowed formats: png, jpeg, webp)"
            await interaction.response.send_message(msg, ephemeral=True)
        elif isinstance(is_img, str):
            msg = "The link entered in the Map image field did not work due to: \n" + is_img
            await interaction.response.send_message(msg, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "length" : map_dim[0],
                "height" : map_dim[1],
                "grid_size" : self.children[2].value,
                "image" : self.children[4].value
            }
            if self.new == True:
                db.insert_object("maps", document)
                msg = f"Map {self.children[0].value} created successfully\nBelow is an image of the map:"
            else:
                db.replace_object("maps", self.name, interaction.guild_id, document)
                msg = f"Map {self.children[0].value} changed successfully\nBelow is an image of the map:"
            e = discord.Embed()
            url = "https://otfbm.io/" + map_dim[0] + "x" + map_dim[1] + "/@dc" + self.children[2].value + "/?bg=" + self.children[4].value
            e.set_image(url=url)
            await interaction.response.send_message(msg, embed=e, ephemeral=True)


    def get_map_values(self):
        map = db.get_object("maps", self.title[:-4], self.server_id)
        self.name = map['name']
        self.description = map['description']
        self.map_size = map['length'] + "\n" + map['height']
        self.grid_size = map['grid_size']
        self.image = map['image']

