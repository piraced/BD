import discord
import src.db_operations as db

class Item_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    slots=""
    abilities=""
    effects=""

    slots_placeholder = """Enter the names (1 per line) of slots this item can be equipped in
for example:
ring1
ring2"""

    abilities_placeholder = """Enter the names (1 per line) of abilites this item grants
for example:
fireball
cleave"""

    effects_placeholer = """Enter the names (1 per line) of effects this item gives the user
for example:
poisoned
armor_inc"""

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id

        if(self.title!="New item"):
            self.get_item_values()
            self.new = False

        self.add_item(discord.ui.InputText(label="Item name", placeholder="Item name (leave empty when saving to delete item)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Item description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Item slots", placeholder=self.slots_placeholder, value=self.slots, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Granted abilities", placeholder=self.abilities_placeholder, value=self.abilities, style=discord.InputTextStyle.long, required= False))
        self.add_item(discord.ui.InputText(label="Granted effects", placeholder=self.effects_placeholer, value=self.effects, style=discord.InputTextStyle.long, required= False))


    async def callback(self, interaction: discord.Interaction):
        equip_slots_rez = self.children[2].value.splitlines()
        abilities_rez = self.children[3].value.splitlines()
        effects_rez = self.children[4].value.splitlines()

        ####If name field is empty cancel item creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("items", self.name, interaction.guild_id)
                msg = f"Item {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Item creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if item with that name already exists
        elif db.does_object_exist_in_ruleset("items", self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "an item with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        #### check if the abilities entered exist
        elif not db.does_object_exist_in_ruleset("abilities", abilities_rez, interaction.guild_id)  and not self.children[3].value == "":
            msg = "One or more of the abilities in the granted abilites field do not exist. Please create the abilities first"
            await interaction.response.send_message(msg, ephemeral=True)
        #### heck if the effects entered exist
        elif not db.does_object_exist_in_ruleset("effects", effects_rez, interaction.guild_id)  and not self.children[4].value == "":
            msg = "One or more of the effects in the granted effects field do not exist. Please create the effects first"
            await interaction.response.send_message(msg, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "equip_slots" : list(dict.fromkeys(equip_slots_rez)),
                "abilities" : list(dict.fromkeys(abilities_rez)),
                "effects" : list(dict.fromkeys(effects_rez))
            }
            if self.new == True:
                db.insert_object("items", document)
                msg = f"Item {self.children[0].value} created successfully"
            else:
                db.replace_object("items", self.name, interaction.guild_id, document)
                msg = f"Item {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_item_values(self):
        item = db.get_object("items", self.title[:-5], self.server_id)
        self.name = item['name']
        self.description = item['description']
        self.slots = '\n'.join(item['equip_slots'])
        self.abilities = '\n'.join(item['abilities'])
        self.effects = '\n'.join(item['effects'])

