import discord
import src.db_operations as db
import src.utils

class Effect_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    needed_stats=""
    effect_config=""
    effect_formula=""

### placeholders are quite shortened due to Discord api limit of 100 characters for placeholders
    needed_stats_placeholder = """Assign stats one/line. arguments - name, caster/target, max(opt) eg:
caster_str = strength caster"""

    effect_config_placeholder = """5 (duration 0=permanent)
true (applied every turn?)
true (true/false effect undone after removal?)"""

    effect_formula_placeholer = """target_health = target_health - caster_str * 5
supported: +-*/() dice rolls"""

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id

        if(self.title!="New effect"):
            self.get_effect_values()
            self.new = False

        self.add_item(discord.ui.InputText(label="Effect name", placeholder="Effect name (leave empty when saving to delete ability)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Effect description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Needed statistics", placeholder=self.needed_stats_placeholder, value=self.needed_stats, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Effect configuration", placeholder=self.effect_config_placeholder, value=self.effect_config, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Effect formula", placeholder=self.effect_formula_placeholer, value=self.effect_formula, style=discord.InputTextStyle.long))


    async def callback(self, interaction: discord.Interaction):
        needed_stats_rez = self.deserialize_needed_stats(self.children[2].value)
        effect_config_rez = self.convert_effect_config(self.children[3].value)
        formula_test = self.test_formulas(needed_stats_rez, self.children[4].value)
        effect_formula_rez = self.children[4].value.splitlines()

        ####If name field is empty cancel object creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("effects", self.name, interaction.guild_id)
                msg = f"Effect {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Effect creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if effect with that name already exists
        elif db.does_object_exist_in_ruleset("effects", self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "an effect with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        #### if deserializing needed stats returned an error message instead of the intended result, send the recieved message
        elif isinstance(needed_stats_rez, str):
            await interaction.response.send_message(needed_stats_rez, ephemeral=True)
        #####If needed statistics field contains an incorrect value cancel object creation/ modification
        elif not self.test_needed_stats(needed_stats_rez):
            msg = "Effect creation cancelled due to an incorrect value in the needed statistics field. Each statistic should follow this format: variable_name(for use in effect formula) = statistic_name target/caster max(optional, used if the statistic represented will be the maximum value instead of current)"
            await interaction.response.send_message(msg, ephemeral=True)
        #####If converting effect configs returned an error message instead of the intended result, send the recieved message
        elif isinstance(effect_config_rez, str):
            await interaction.response.send_message(effect_config_rez, ephemeral=True)
        ###########test formula
        elif isinstance(formula_test, str):
            await interaction.response.send_message(formula_test, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "needed_statistics" : needed_stats_rez,
                "duration" : effect_config_rez[0],
                "every_turn" : effect_config_rez[1],
                "undoes_itself" : effect_config_rez[2],
                "formulas" : effect_formula_rez
            }
            if self.new == True:
                db.insert_object("effects", document)
                msg = f"Effect {self.children[0].value} created successfully"
            else:
                db.replace_object("effects", self.name, interaction.guild_id, document)
                msg = f"Effect {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)

    def get_effect_values(self):
        effect = db.get_object("effects",self.title[:-7], self.server_id)
        self.name = effect['name']
        self.description = effect['description']
        self.needed_stats = self.serialize_needed_stats(effect["needed_statistics"])
        self.effect_config = '\n'.join([str(effect["duration"]), str(effect["every_turn"]), str(effect["undoes_itself"])])
        self.effect_formula = '\n'.join(effect['formulas'])   

    def test_needed_stats(self, needed_stats:list):
        for stat in needed_stats:
            if not db.does_stat_exist_in_ruleset(stat["stat_name"], self.server_id):
                return False
            if stat["stat_source"] not in ["caster", "target"]:
                return False
        return True
    
    def test_formulas(self, needed_stats, formulas):
        stats = []
        for needed_stat in needed_stats:
            stats.append(needed_stat["name"])
        for index, formula in enumerate(formulas, start=1):
            ### Check if format matches the needed format of variable = equation
            if formula.count("=") != 1:
                rez_msg = f"Validation failed for formula {index} due to: \nEach formula must contain exactly 1 \"=\""
                return rez_msg
            
            parts = formula.split("=")
            ### Check if the result is for self
            formula_rez_stat = next((item for item in stats if item["name"] == parts[0].strip()), False)
            if formula_rez_stat == False:
                rez_msg = f"Validation failed for formula {index} due to: \nResult variable not found in needed stats"
                return rez_msg
            elif formula_rez_stat["stat_source"] != "target":
                rez_msg = f"Validation failed for formula {index} due to: \nResult variable source is not \"target\""
                return rez_msg
            ### Test formula itself
            rez = src.utils.test_formula(stats, parts[1].strip())
            if isinstance(rez, str):
                rez_msg = f" Validation failed for formula {index} due to:\n" + rez
                return rez_msg
        return True
                

    ###turns needed stats from a string to an array of objects, returns an error message string if the input format is wrong
    def deserialize_needed_stats(self, needed_stats:str):
        stats = needed_stats.splitlines()
        rez = []
        
        for stat in stats:
            if stat.count("=") != 1:
                msg = "Effect creation failed because each line in needed statistics field must contain exactly one = symbol"
                return msg
            else:
                parts = stat.split("=")
                var_name = parts[0].strip()
                part = parts[1].strip()
            if part.count(" ") == 0 or part.count(" ") > 2:
                msg = "Effect creation failed because each line in needed statistics must contain either 2 or 3 words after the = sign separated by spaces"
                return msg
            else:
                var_values = part.split(" ")
                obj = {"name" : var_name, "stat_name" : var_values[0], "stat_source" : var_values[1].lower(), "max" : False}
                if len(var_values) == 3 and var_values[2].lower() == "max":
                    obj["max"] = True
                rez.append(obj)
        return rez
    
    ### turns needed stats from a list of objects to a string
    def serialize_needed_stats(self, needed_stats:list):
        rez = ""
        for stat in needed_stats:
            rez = rez + stat["name"] + " = " + stat["stat_name"] + " " + stat["stat_source"]
            if stat["max"] == True:
                rez = rez + " max"
            rez = rez + "\n"
        return rez
    
    def convert_effect_config(self, effect_config:str):
        configs = effect_config.lower().splitlines()
        if len(configs) != 3:
            return "Effect configuration field must contain exactly 3 lines"
        if configs[1] not in ["true", "false"] or configs[2] not in ["true", "false"]:
            return "Lines 2 and 3 in the effect configuration field must contain true or false"
        if not configs[0].isdigit():
            return "Line 1 in the effect configuration field must contain the effect duration in number of turns (0 for permanent)"
        rez = [configs[0]]
        if configs[1] == "true":
            rez.append(True)
        else:
            rez.append(False)
        if configs[2] == "true":
            rez.append(True)
        else:
            rez.append(False)
        return rez