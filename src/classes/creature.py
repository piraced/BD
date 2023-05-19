import src.classes.effect
import src.db_operations as db
import src.utils
import d20
import discord



class Creature():
    

    def __init__(self, creature, length_coord, height_coord, server_id, thread:discord.Thread):
        self.server_id = server_id
        self.name = creature["name"]
        self.abilities = creature["abilities"]
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

        rules = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"],self.server_id)
        self.speed_formula = rules["movement_formula"]
        self.initiative_formula = rules["initiative_formula"]

        for key, value in creature["statistics"].items():
            self.statistics[key] = {"value" : value, "max" : value}

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

        rez = self.calculate_speed()
        self.log_msg = f"Starting turn for :{self.name}\nMovement points this turn: {rez}"
        await thread.send(self.log_msg)
        for effect_log in self.effect_logs:
            await thread.send(effect_log)


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
    
