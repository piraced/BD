import discord
import src.db_operations as db

class Character_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    stats=""
    abilities=""
    effects=""
    image=""
    token=""
    player=""

    stats_placeholder = """Enter stats (1/line), their current and max values for the character.
eg:
speed 5 9"""

    abilities_placeholder = """Enter the names (1 per line) of abilites this character has
for example:
cleave"""

    effects_placeholer = """Enter the names (1 per line) of effects this character will under in combat
for example:
poisoned"""

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id

        if(self.title!="New character"):
            self.get_character_values()
            self.new = False
        else:
            start_stats = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)["statistics"]
            for stat in start_stats:
                self.stats = self.stats + stat + "\n"

        self.add_item(discord.ui.InputText(label="Character name", placeholder="Character name (leave empty when saving to delete character)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Character description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Character statistics", placeholder=self.stats_placeholder, value=self.stats, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Innate abilities", placeholder=self.abilities_placeholder, value=self.abilities, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Under effects", placeholder=self.effects_placeholer, value=self.effects, style=discord.InputTextStyle.long, required= False))


    async def callback(self, interaction: discord.Interaction):
        stats_rez = self.character_stats_string_to_obj(self.children[2].value.splitlines())
        abilities_rez = self.children[3].value.splitlines()
        effects_rez = self.children[4].value.splitlines()

        ####If name field is empty cancel creature creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("characters", self.name, interaction.guild_id)
                msg = f"Character {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Character creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if a character with that name already exists
        elif db.does_object_exist_in_ruleset("characters", self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "A character with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if name contains spaces
        elif " " in self.children[0].value:
            msg = "A characters name cannot contain spaces"
            await interaction.response.send_message(msg, ephemeral=True)
        ####send error message if one was returned when converting character stats to dict
        elif isinstance(stats_rez, str):
            await interaction.response.send_message(stats_rez, ephemeral=True)
        elif not self.do_all_character_stats_exist(stats_rez):
            msg = "One or more of the statistics in the character statistics field is/are missing"
            await interaction.response.send_message(msg, ephemeral=True)
        #### check if the abilities entered exist
        elif not db.does_object_exist_in_ruleset("abilities", abilities_rez, interaction.guild_id):
            msg = "One or more of the abilities in the innate abilites field do not exist. Please create the abilities first"
            await interaction.response.send_message(msg, ephemeral=True)
        #### check if the effects entered exist
        elif not db.does_object_exist_in_ruleset("effects", effects_rez, interaction.guild_id) and not self.children[4].value == "":
            msg = "One or more of the effects in the under effects field do not exist. Please create the effects first"
            await interaction.response.send_message(msg, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "statistics" : stats_rez,
                "abilities" : list(dict.fromkeys(abilities_rez)),
                "effects" : list(dict.fromkeys(effects_rez)),
                "image" : self.image,
                "token" : self.token,
                "player" : self.player
            }
            if self.new == True:
                db.insert_object("characters", document)
                msg = f"Character {self.children[0].value} created successfully"
            else:
                db.replace_object("characters", self.name, interaction.guild_id, document)
                msg = f"Character {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_character_values(self):
        character = db.get_object("characters", self.title[:-10], self.server_id)
        self.name = character['name']
        self.description = character['description']
        self.stats = self.character_stats_to_string(character['statistics'])
        self.abilities = '\n'.join(character['abilities'])
        self.effects = '\n'.join(character['effects'])
        self.image = character['image']
        self.token = character['token']
        self.player = character['player']


    def character_stats_string_to_obj(self,stats_rez):
        name = str
        value = int
        max = int
        rez = {}
        for stat in stats_rez:
            if stat.count(" ") > 2:
                return "Character statistics field mus be in the format of statistic name (from the ruleset) space current value space maximum value. Just statistic name will assume that the current and max value is 0. One number will assume that the current and max values are the same. This message was sent because a line contained more than 2 spaces"
            elif stat.count(" ") == 2:
                parts = stat.split(" ")
                name = parts[0]
                value = parts[1]
                max = parts[2]
                if not parts[1].isdecimal() or not parts[2].isdecimal():
                    return "The values following the statistic name must be a 0 or a positive integer"
            elif stat.count(" ") == 1:
                parts = stat.split(" ")
                name = parts[0]
                value =parts[1]
                max = parts[1]
                if not parts[1].isdecimal():
                    return "The value folling the statistic name must be a 0 or a positive integer"
            else:
                name = stat
                value = 0
                max = 0
            rez[name] = {"value": value, "max": max}
        
        return rez
        

    def character_stats_to_string(self, stats):
        rez = ""
        for name, value in stats.items():
            rez = rez + name + " " + str(value["value"]) + " " + str(value["max"]) + "\n"
        return rez
    
    
    def do_all_character_stats_exist(self, stats:dict):
        ruleset = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)
        for ruleset_stat in ruleset["statistics"]:
            if not ruleset_stat in stats.keys():
                return False
        return True
