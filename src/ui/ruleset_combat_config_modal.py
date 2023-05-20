import discord
import src.db_operations as db
import src.utils


class Ruleset_combat_config_modal(discord.ui.Modal):
    name=""
    description=""
    defeat_stats=""
    movement_formula=""
    initiative_formula=""

    defeat_stats_placeholder="Character is defeated when one of these statistics hit 0"
    movement_formula_placeholder="Formula to get number of squares a character can move per turn. eg: Speed / 5 + 1d6"
    initiative_formula_placeholder="Formula to decide turn order. Highest number goes first. eg: Speed * 5 + 1d20"

    def __init__(self, server_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server_id = server_id
        self.get_ruleset_values()

        self.add_item(discord.ui.InputText(label="Ruleset name", placeholder="Name", value=self.name))
        self.add_item(discord.ui.InputText(label="Ruleset description", placeholder="Description...", value=self.description, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Defeat statistics", placeholder=self.defeat_stats_placeholder, value=self.defeat_stats, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Movement formula", placeholder=self.movement_formula_placeholder, value=self.movement_formula))
        self.add_item(discord.ui.InputText(label="Initiative formula", placeholder=self.initiative_formula_placeholder, value=self.initiative_formula))

    async def callback(self, interaction: discord.Interaction):
        test_movement_formula = src.utils.test_formula(db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)["statistics"], self.children[3].value)
        test_initiative_formula = src.utils.test_formula(db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)["statistics"], self.children[4].value)

        ####Check if ruleset with that name already exists
        if db.does_ruleset_exist(self.children[0].value, interaction.guild_id) and self.children[0].value != self.name:
            msg = "a ruleset with this name already exists"
            await interaction.response.send_message(msg, ephemeral=True)
        ### Check if the values in the defeat statistics exist in ruleset
        elif not db.do_stats_exist_in_ruleset(self.children[2].value.splitlines(), interaction.guild_id):
            msg = "One of the statistics in the Defeat statistics field do not exist"
            await interaction.response.send_message(msg, ephemeral=True)
        #### Test movement formula
        elif isinstance(test_movement_formula, str):
            msg = "Movement formula failed validation due to:\n" + test_movement_formula
            await interaction.response.send_message(msg, ephemeral=True)
        #### Test initiative formula
        elif isinstance(test_initiative_formula, str):
            msg = "Initiative formula failed validation due to:\n" + test_initiative_formula
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            document = {
                "server_id" : interaction.guild_id,
                "name" : self.children[0].value,
                "description" : self.children[1].value,
                "statistics" : self.ruleset["statistics"],
                "defeat_statistics" : self.children[2].value.splitlines(),
                "movement_formula" : self.children[3].value,
                "initiative_formula" : self.children[4].value
            }
            db.replace_ruleset(self.name, interaction.guild_id, document)
            msg = f"ruleset {self.children[0].value} changed successfully"
            await interaction.response.send_message(msg, ephemeral=True)


    def get_ruleset_values(self):
        self.ruleset = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)
        self.name = self.ruleset['name']
        self.description = self.ruleset['description']
        self.defeat_stats = '\n'.join(self.ruleset['defeat_statistics'])
        self.movement_formula = self.ruleset['movement_formula']
        self.initiative_formula = self.ruleset['initiative_formula']