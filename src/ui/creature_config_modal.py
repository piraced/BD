import discord
import src.db_operations as db

class Creature_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    stats=""
    abilities=""
    effects=""
    image=""
    token=""

    stats_placeholder = """Enter stats (1/line) and their max values for the creature.
eg:
health 99"""

    abilities_placeholder = """Enter the names (1 per line) of abilites this creature has
for example:
fireball
cleave"""

    effects_placeholer = """Enter the names (1 per line) of effects this creature is under
for example:
poisoned
armor_inc"""

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id

        if(self.title!="New creature"):
            self.get_creature_values()
            self.new = False
        else:
            start_stats = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)["statistics"]
            for stat in start_stats:
                self.stats = self.stats + stat + "\n"

        self.add_item(discord.ui.InputText(label="Creature name", placeholder="Creature name (leave empty when saving to delete creature)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Creature description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Creature statistics", placeholder=self.stats_placeholder, value=self.stats, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Available abilities", placeholder=self.abilities_placeholder, value=self.abilities, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Under effects", placeholder=self.effects_placeholer, value=self.effects, style=discord.InputTextStyle.long, required= False))


    async def callback(self, interaction: discord.Interaction):
        stats_rez = self.creature_stats_string_to_dict(self.children[2].value.splitlines())
        abilities_rez = self.children[3].value.splitlines()
        effects_rez = self.children[4].value.splitlines()

        ####If name field is empty cancel creature creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("creatures", self.name, interaction.guild_id)
                msg = f"Creature {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Creature creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if a creature with that name already exists
        elif db.does_object_exist_in_ruleset("creatures", self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "a creature with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        ####Check if name contains spaces
        elif " " in self.children[0].value:
            msg = "A creatures name cannot contain spaces"
            await interaction.response.send_message(msg, ephemeral=True)
        ####print error message if one was returned when converting creature stats to dict
        elif isinstance(stats_rez, str):
            await interaction.response.send_message(stats_rez, ephemeral=True)
        ####check if all of the stats exist
        elif not self.do_all_creature_stats_exist(stats_rez):
            msg = "One or more of the statistics in the creature statistics field is/are missing"
            await interaction.response.send_message(msg, ephemeral=True)
        #### check if the abilities entered exist
        elif not db.does_object_exist_in_ruleset("abilities", abilities_rez, interaction.guild_id):
            msg = "One or more of the abilities in the available abilites field do not exist. Please create the abilities first"
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
                "token" : self.token
            }
            if self.new == True:
                db.insert_object("creatures", document)
                msg = f"Creature {self.children[0].value} created successfully"
            else:
                db.replace_object("creatures", self.name, interaction.guild_id, document)
                msg = f"Creature {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_creature_values(self):
        creature = db.get_object("creatures", self.title[:-9], self.server_id)
        self.name = creature['name']
        self.description = creature['description']
        self.stats = self.creature_stats_dict_to_string(creature['statistics'])
        self.abilities = '\n'.join(creature['abilities'])
        self.effects = '\n'.join(creature['effects'])
        self.image = creature['image']
        self.token = creature['token']


    def creature_stats_string_to_dict(self,stats_rez):
        names = []
        values = []
        for stat in stats_rez:
            if stat.count(" ") > 1:
                return "Creature statistics field must be in the format of statistic name (from the ruleset) space max statistic value. Just statistic name will assume that statistic is equal to 0. This message was sent because a line contains more than one space"
            elif stat.count(" ") == 1:
                parts = stat.split(" ")
                names.append(parts[0])
                values.append(parts[1])
                if not parts[1].isdecimal():
                    return "The value following the statistic name must be a 0 or a positive integer"
            else:
                names.append(stat)
                values.append(0)
        return dict(zip(names, values))
    
    def do_all_creature_stats_exist(self, stats):
        ruleset = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)
        for ruleset_stat in ruleset["statistics"]:
            if not ruleset_stat in stats:
                return False
        return True

    def creature_stats_dict_to_string(self, stats):
        rez = ""
        for name, value in stats.items():
            rez = rez + name + " " + str(value) + "\n"
        return rez
