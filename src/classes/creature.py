import src.classes.effect
import src.classes.ability
import src.db_operations as db
import src.utils
import d20
import discord



class Creature():
    

    def __init__(self, creature, length_coord, height_coord, server_id, thread:discord.Thread):
        self.server_id = server_id
        self.name = creature["name"]
        self.abilities = []
        self.thread = thread
        self.statistics = {}
        self.effects = []
        self.token = creature["token"]
        self.x = int(length_coord)
        self.y = int(height_coord)
        self.speed = 0
        self.initiative = 0
        self.log_msg = ""
        self.effect_logs = []
        self.player_id = 0
        self.defeated = False

        rules = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"],self.server_id)
        self.speed_formula = rules["movement_formula"]
        self.initiative_formula = rules["initiative_formula"]

        for key, value in creature["statistics"].items():
            self.statistics[key] = {"value" : value, "max" : value}

        for ability in creature["abilities"]:
            ability_data = db.get_object("abilities", ability, self.server_id)
            self.abilities.append(src.classes.ability.Ability(ability_data, self.server_id, self.player_id))

        for effect in creature["effects"]:
            effect_data = db.get_object("effects", effect, self.server_id)
            self.effects.append(src.classes.effect.Effect(effect_data, self.server_id, self.statistics))

        rez = self.calculate_initiative()
        self.init_log_rez = f"Initiative for: {self.name} is {rez}"

    async def initialize_turn(self, thread:discord.Thread):
        self.effect_logs = []

        for effect in self.effects:
            self.statistics = effect.apply_effect(self.statistics)
            self.effect_logs.append(effect.log_msg)
            if effect.delete:
                self.effects.remove(effect)

        rez = self.calculate_speed()
        self.log_msg = f"Starting turn for: {self.name}\nMovement points this turn: {rez}"
        await thread.send(self.log_msg)

        ### for some reason this is where it stops before error
        for effect_log in self.effect_logs:
            if effect_log != "":
                await thread.send(effect_log)
        
        self.is_defeated()


    def calculate_speed(self):
        roll = d20.roll(src.utils.add_values_to_formula_string(self.get_current_stats_dict(), self.speed_formula))
        self.speed = roll.total
        return roll.result

    def calculate_initiative(self):
        roll = d20.roll(src.utils.add_values_to_formula_string(self.get_current_stats_dict(), self.initiative_formula))
        self.initiative = roll.total
        return roll.result


    def get_current_stats_dict(self):
        rez={}
        for key, value in self.statistics.items():
            rez[key] = value["value"]
        return rez
    
    async def lower_over_max_stats(self):
        for key, value in self.statistics.items():
            if value["max"] < value["value"]:
                self.statistics[key]["value"] = value["max"]

    
    def is_defeated(self):
        defeat_stats = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)["defeat_statistics"]

        for defeat_stat in defeat_stats:
            if int(self.statistics[defeat_stat]["value"]) <= 0:
                self.defeated = True
    
