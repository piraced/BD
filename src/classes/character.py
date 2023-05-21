import src.classes.creature
import src.classes.ability
import src.db_operations as db
import src.classes.effect
import discord



class Character(src.classes.creature.Creature):
    def __init__(self, character, length_coord, height_coord, server_id, thread:discord.Thread):
        self.server_id = server_id
        self.name = character["name"]
        self.abilities = []
        self.statistics = character["statistics"]
        self.effects = []
        self.thread = thread
        self.token = character["token"]
        self.x = int(length_coord)
        self.y = int(height_coord)
        self.speed = 0
        self.initiative = 0
        self.log_msg = ""
        self.player_id = character["player"]

        rules = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"],self.server_id)
        self.speed_formula = rules["movement_formula"]
        self.initiative_formula = rules["initiative_formula"]

        rez = self.calculate_initiative()
        self.init_log_rez = f"Initiative for: {self.name} is {rez}"


        for effect in character["effects"]:
            effect_data = db.get_object("effects", effect, self.server_id)
            self.effects.append(src.classes.effect.Effect(effect_data, self.server_id, self.statistics))

        for ability in character["abilities"]:
            ability_data = db.get_object("abilities", ability, self.server_id)
            self.abilities.append(src.classes.ability.Ability(ability_data, self.server_id))