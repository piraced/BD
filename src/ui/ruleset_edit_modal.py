import discord
import src.db_operations as db


class Ruleset_modal(discord.ui.Modal):
    new = True
    name=""
    description=""
    base_stats=""
    default_equip_slots=""
    defeat_stats = []
    movement_formula = ""
    initiative_formula = ""

    base_stats_placeholder="""
Health
Strength
Dexterity
..."""

    default_equip_placeholder="""
torso
ring1
ring2
..."""

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id

        if(self.title!="Create a new ruleset"):
            self.get_ruleset_values()
            self.new = False

        self.add_item(discord.ui.InputText(label="Ruleset name", placeholder="Name", value=self.name))
        self.add_item(discord.ui.InputText(label="Ruleset description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Base statistics", placeholder=self.base_stats_placeholder, value=self.base_stats, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Default equipment slots", placeholder=self.default_equip_placeholder, value=self.default_equip_slots, style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        base_stats_rez = self.children[2].value
        default_equip_rez = self.children[3].value

        ####Check if ruleset with that name already exists
        if db.does_ruleset_exist( self.children[0].value, interaction.guild_id) and (self.new == True or self.children[0].value != self.name):
            msg = "a ruleset with this name already exists"
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            document = {
                "server_id" : interaction.guild_id,
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "statistics" : list(dict.fromkeys(base_stats_rez.splitlines())),
                "default_equipment" : list(dict.fromkeys(default_equip_rez.splitlines())),
                "defeat_statistics" : self.defeat_stats,
                "movement_formula" : self.movement_formula,
                "initiative_formula" : self.initiative_formula
            }
            if self.new == True:
                db.insert_object("rulesets", document)
                msg = f"ruleset for {self.children[0].value} created successfully"
            else:
                db.replace_ruleset(self.name, interaction.guild_id, document)
                msg = f"ruleset for {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_ruleset_values(self):
        self.ruleset = db.get_ruleset(self.title, self.server_id)
        self.name = self.ruleset['name']
        self.description = self.ruleset['description']
        self.base_stats = '\n'.join(self.ruleset['statistics'])
        self.default_equip_slots = '\n'.join(self.ruleset['default_equipment'])
        self.defeat_stats = self.ruleset['defeat_statistics']
        self.movement_formula = self.ruleset['movement_formula']
        self.initiative_formula = self.ruleset['initiative_formula']