import discord
import src.db_operations as db

class Ability_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    type=""
    range=""
    effects=""

### placeholders are quite shortened due to Discord api limit of 100 characters for placeholders
    type_placeholder = """single, line, cone, aoe_projectile"""

    range_placeholder = """Max ability range in tiles, 0=self
2nd line if type= cone or aoe_projectile enter degrees or radius"""

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
        self.add_item(discord.ui.InputText(label="Ability type", placeholder=self.type_placeholder, value=self.type))
        self.add_item(discord.ui.InputText(label="Ability range", placeholder=self.range_placeholder, value=self.range, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Granted effects", placeholder=self.effects_placeholer, value=self.effects, style=discord.InputTextStyle.long))


    async def callback(self, interaction: discord.Interaction):

        range_rez = self.children[3].value.splitlines()
        effects_rez = self.children[4].value.splitlines()

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
        elif str.lower(self.children[2].value) not in ["single", "line", "cone", "aoe_projectile", "aoe projectile"]:
            msg = "Ability creation cancelled due to an incorrect value in the type field. Allowed types are: single, line, cone, aoe_projectile"
            await interaction.response.send_message(msg, ephemeral=True)
        #####If ability range field contain incorrect values cancel object creation/ modification
        elif not range_rez[0].isdecimal() or (self.children[2].value in ["cone", "aoe_projectile", "aoe projectile"] and (range_rez.count() < 2 or not range_rez[1].isdecimal())):
            msg = "Ability creation cancelled due to an incorrect value in the range field. The value must be an non negative integer and if the type is cone or aoe_projectile there must be another number in the second line"
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
                "type" : self.children[2].value,
                "range" : range_rez,
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
        self.type = ability['type']
        self.range = '\n'.join(ability['range'])
        self.effects = '\n'.join(ability['effects'])
