import discord
import src.db_operations as db
import src.utils
import src.classes.creature

class Encounter_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    map=""
    creatures=""

    creatures_placeholder="Enter the names of creatures and their location on the map(in numbers) one per line. eg:\n imp 5 5"

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id


        if(self.title!="New encounter"):
            self.get_encounter_values()
            self.new = False


        self.add_item(discord.ui.InputText(label="Encounter name", placeholder="Encounter name (leave empty when saving to delete the encounter)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Encounter description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Map name", placeholder="Enter the name of the map that will be used", value=self.map))
        self.add_item(discord.ui.InputText(label="Creatures", placeholder= self.creatures_placeholder, value=self.creatures, style=discord.InputTextStyle.long))


    async def callback(self, interaction: discord.Interaction):
        creature_rez = self.creature_string_to_obj(self.children[3].value.splitlines())

        #### skip doing validation if creature string to obj failed
        if not isinstance(creature_rez, str):
            creature_validation = self.validate_creatures(self.children[2].value, interaction.guild_id, creature_rez)

        ####If name field is empty cancel encounter creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("encounters", self.name, interaction.guild_id)
                msg = f"Encounter {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Encounter creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if an encounter with that name already exists
        elif db.does_object_exist_in_ruleset("encounters", self.children[0].value, interaction.guild_id) and  self.children[0].value != self.name:
            msg = "An encounter with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if a map with the given name exists
        elif not db.does_object_exist_in_ruleset("maps", self.children[2].value, interaction.guild_id):
            msg = "A map with the name given in the Map name field does not exist"
            await interaction.response.send_message(msg, ephemeral=True)
        ####If converting creature from string ran into an error
        elif isinstance(creature_rez, str):
            await interaction.response.send_message(creature_rez, ephemeral=True)
        ####If creature validation failed (creature does not exist or is out of bounds)
        elif isinstance(creature_validation, str):
            await interaction.response.send_message(creature_validation, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "map" : self.children[2].value,
                "creatures" : creature_rez,
            }
            if self.new == True:
                db.insert_object("encounters", document)
                msg = f"Encounter {self.children[0].value} created successfully\nBelow is an image of the encounter:"
            else:
                db.replace_object("encounters", self.name, interaction.guild_id, document)
                msg = f"Encounter {self.children[0].value} changed successfully\nBelow is an image of the map:"

            entities = []
            for creature in creature_rez:
                creature_data = db.get_object("creatures", creature["name"], self.server_id)
                entities.append(src.classes.creature.Creature(creature_data, creature["length_coord"], creature["height_coord"], self.server_id, interaction.channel))

            e = discord.Embed()
            url = src.utils.map_url_constructor(db.get_object("maps", self.children[2].value, interaction.guild_id), entities)
            e.set_image(url=url)
            await interaction.response.send_message(msg, embed=e, ephemeral=True)


    def get_encounter_values(self):
        encounter = db.get_object("encounters", self.title[:-10], self.server_id)
        self.name = encounter['name']
        self.description = encounter['description']
        self.map = encounter['map']
        self.creatures = self.creature_obj_to_string(encounter['creatures'])



    def creature_string_to_obj(self, creatures):
        rez = []
        for creature in creatures:
            if creature.count(" ") != 2:
                return "The format to add creatures must be creature_name length_coordinate height_coordinate"
            parts = creature.split(" ")
            if not parts[1].isdecimal() or not parts[2].isdecimal() or parts[1] == "0" or parts[2] == "0":
                return "The coordinates for the creatures must be positive integers"
            rez.append({"name": parts[0], "length_coord" : parts[1], "height_coord" : parts[2]})
        return rez
    
    def creature_obj_to_string(self, creatures):
        rez = ""
        for creature in creatures:
            rez = rez + creature["name"] + " " + creature["length_coord"] + " " + creature["height_coord"] + "\n"
        return rez
    
    def validate_creatures(self, map_name, server_id, creatures):
        map = db.get_object("maps", map_name, server_id)
        max_length = int(map['length'])
        max_height = int(map['height'])

        for creature in creatures:
            if not db.does_object_exist_in_ruleset("creatures", creature["name"], server_id):
                return "Creature \"" + creature["name"] + "\" does not exist in the current ruleset"
            if int(creature["length_coord"]) > max_length or int(creature["height_coord"]) > max_height:
                return "Creature \"" + creature["name"] + "\" is in an incorrect location. Its coordinates are " + creature["length_coord"] + " " + creature["height_coord"] + " While map size is " + max_length + " " + max_height
        return True