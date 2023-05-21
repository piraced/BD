import discord
import src.db_operations as db

class Ability_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    type_n_range=""
    self_effects=""
    effects=""

### placeholders are quite shortened due to Discord api limit of 100 characters for placeholders
    type_n_range_placeholder = """single, line, cone, area
Max range in tiles, 0=self
cone width (if cone), otherwise nothing"""

    self_effects_placeholder = """Enter the names (1/line) of effects using this ability gives to the caster
for example:
mana_down"""

    effects_placeholer = """Enter the names (1/line) of effects this ability gives the target
for example:
poisoned
armor_inc"""

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id
        if(self.title!="New ability"):
            self.get_ability_values()
            self.new = False

        self.add_item(discord.ui.InputText(label="Ability name", placeholder="Ability name (leave empty when saving to delete ability)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Ability description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Ability settings", placeholder=self.type_n_range_placeholder, value=self.type_n_range, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Caused effects to the caster", placeholder=self.self_effects_placeholder, value=self.self_effects, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Granted effects to the target", placeholder=self.effects_placeholer, value=self.effects, style=discord.InputTextStyle.long))


    async def callback(self, interaction: discord.Interaction):

        self_effect_rez = self.children[3].value.splitlines()
        effects_rez = self.children[4].value.splitlines()

        parts = self.children[2].value.splitlines()
        ability_type = parts[0].strip().lower()
        ability_range = []
        ability_range.append(parts[1])
        if len(parts) > 2:
            ability_range.append(parts[2])

        ####If name field is empty cancel object creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("abilities", self.name, interaction.guild_id)
                msg = f"Ability {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Ability creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if ability with that name already exists
        elif db.does_object_exist_in_ruleset("abilities", self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "an Ability with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        #####If ability type field contains an incorrect value cancel object creation/ modification
        elif ability_type not in ["single", "line", "cone", "area"]:
            msg = "Ability creation cancelled due to an incorrect value in the settings field. Allowed types are: single, line, cone, area"
            await interaction.response.send_message(msg, ephemeral=True)
        #####If ability range field contain incorrect values cancel object creation/ modification
        elif not ability_range[0].isdecimal() or (ability_type in ["cone"] and (ability_range.count() < 2 or not ability_range[1].isdecimal())):
            msg = "Ability creation cancelled due to an incorrect value in the settings field. The range value must be an non negative integer and if the type is cone there must be another number in the following line"
            await interaction.response.send_message(msg, ephemeral=True)
        #### check if the caused effects exist
        elif not db.does_object_exist_in_ruleset("effects", self_effect_rez, interaction.guild_id):
            msg = "One or more of the effects in the caused effects field do not exist. Please create the effects first"
            await interaction.response.send_message(msg, ephemeral=True)
        #### check if the effects entered exist
        elif not db.does_object_exist_in_ruleset("effects", effects_rez, interaction.guild_id):
            msg = "One or more of the effects in the granted effects field do not exist. Please create the effects first"
            await interaction.response.send_message(msg, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "type" : ability_type,
                "range" : ability_range,
                "self_effects" : list(dict.fromkeys(self_effect_rez)),
                "effects" : list(dict.fromkeys(effects_rez))
            }
            if self.new == True:
                db.insert_object("abilities", document)
                msg = f"Ability {self.children[0].value} created successfully"
            else:
                db.replace_object("abilities", self.name, interaction.guild_id, document)
                msg = f"Ability {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_ability_values(self):
        ability = db.get_object("abilities", self.title[:-8], self.server_id)
        self.name = ability['name']
        self.description = ability['description']
        self.type_n_range = ability['type'] + '\n' + '\n'.join(ability['range'])
        self.self_effects = '\n'.join(ability['self_effects'])
        self.effects = '\n'.join(ability['effects'])
