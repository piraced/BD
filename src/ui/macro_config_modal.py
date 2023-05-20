import discord
import src.db_operations as db
import src.utils

class Macro_config_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    formula=""


    formula_placeholer = "Enter the formula for the macro e.g: str * 5 - 1 + 1d6"

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id

        if(self.title!="New macro"):
            self.get_macro_values()
            self.new = False

        self.add_item(discord.ui.InputText(label="Macro name", placeholder="Macro name (leave empty when saving to delete macro)", value=self.name, required= False))
        self.add_item(discord.ui.InputText(label="Macro description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Formula", placeholder=self.formula_placeholer, value=self.formula))


    async def callback(self, interaction: discord.Interaction):
        rez = src.utils.test_formula(db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)["statistics"], self.children[2].value)

        ####If name field is empty cancel macro creation/ delete object being modified
        if self.children[0].value == "":
            if self.new == False:
                db.delete_object("macros", self.name, interaction.guild_id)
                msg = f"Macro {self.name} deleted sucessfully"
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                msg = "Macro creation cancelled"
                await interaction.response.send_message(msg, ephemeral=True)
        ####Check if macro with that name already exists
        elif db.does_object_exist_in_ruleset("macros", self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "a macro with this name already exists for the current ruleset"
            await interaction.response.send_message(msg, ephemeral=True)
        #### heck if the formula works
        elif isinstance(rez, str):
            msg = "The formula failed validation due to:\n" + rez
            await interaction.response.send_message(msg, ephemeral=True)
        else:        
            document = {
                "server_id" : interaction.guild_id,
                "ruleset": db.get_selected_ruleset(interaction.guild_id)["name"],
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "formula" : self.children[2].value
            }
            if self.new == True:
                db.insert_object("macros", document)
                msg = f"Macro {self.children[0].value} created successfully"
            else:
                db.replace_object("macros", self.name, interaction.guild_id, document)
                msg = f"Macro {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_macro_values(self):
        macro = db.get_object("macros", self.title[:-6], self.server_id)
        self.name = macro['name']
        self.description = macro['description']
        self.formula = macro['formula']

