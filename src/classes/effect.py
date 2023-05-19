import src.db_operations as db
import src.utils
import d20




class Effect():
    def __init__(self, effect, server_id, caster_stats):
        self.name = effect["name"]
        self.server_id = server_id
        self.stats = db.get_ruleset(db.get_selected_ruleset(self.server_id)["name"], self.server_id)["statistics"]
        self.description = effect['descritpion']
        self.duration = effect['duration']
        self.every_turn = effect["every_turn"]
        self.undoes_itself = effect["undoes_itself"]
        self.formulas = effect["formulas"]
        self.needed_statistics = effect["needed_statistics"]
        self.caster_stats = caster_stats
        self.modified_values = {}

        self.log_msg = ""
        
        for stat in self.stats:
            self.modified_values[stat] = {"value" : 0, "max" : 0}

        if self.every_turn == False:
            self.ticks_remaining = 1
        else:
            self.ticks_remaining = self.duration
        if self.duration == 0:
            self.infinite_duration = True
        else:
            self.infinite_duration = False



    def get_stats_for_formula(self, recipient_stats):
        rez = {}
        for needed_stat in self.needed_statistics:
            if needed_stat["stat_source"] == "caster":
                if needed_stat["max"] == False:
                    rez[needed_stat["name"]] = self.caster_stats[needed_stat["stat_name"]]["value"]
                else:
                    rez[needed_stat["name"]] = self.caster_stats[needed_stat["stat_name"]]["max"]
            else:
                if needed_stat["max"] == False:
                    rez[needed_stat["name"]] = recipient_stats[needed_stat["stat_name"]]["value"]
                else:
                    rez[needed_stat["name"]] = recipient_stats[needed_stat["stat_name"]]["max"]
        return rez
    
    def needed_stat_to_self_stat(self, stat_name:str):
        for needed_stat in self.needed_statistics:
                if needed_stat["name"] == stat_name:
                    return [needed_stat["stat_name"], needed_stat["max"]]

    def apply_effect(self, recipient_stats):
        self.log_msg = ""
        #### Apply effect
        if self.ticks_remaining != 0:
            self.log_msg = "Applying effect: " + self.name + "\n"
            for formula in self.formulas:
                parts = formula.split("=")
                formula_rez = d20.roll(src.utils.add_values_to_formula_string(self.get_stats_for_formula(recipient_stats), parts[1]))
                affected_stat = self.needed_stat_to_self_stat(parts[0].strip())
                if self.undoes_itself:
                    if affected_stat[1]:
                        self.modified_values[affected_stat[0]]["max"] =  self.modified_values[affected_stat[0]]["max"] + formula_rez.total
                    else:
                        self.modified_values[affected_stat[0]]["value"] =  self.modified_values[affected_stat[0]]["value"] + formula_rez.total
                if affected_stat[1]:
                    recipient_stats[affected_stat[0]]["max"] = formula_rez.total
                    if recipient_stats[affected_stat[0]]["max"] < recipient_stats[affected_stat[0]]["value"]:
                        recipient_stats[affected_stat[0]]["value"] = recipient_stats[affected_stat[0]]["max"]
                    self.log_msg = self.log_msg + "maximum " + affected_stat[0] + " " + str(formula_rez) + "\n"
                else:
                    recipient_stats[affected_stat[0]]["value"] = formula_rez.total
                    self.log_msg = self.log_msg + "current " + affected_stat[0] + " " + str(formula_rez) + "\n"

            if not self.infinite_duration:
                self.log_msg = self.log_msg + "\n Turns remaining: " + str(self.duration) + "\n"
            else:
                self.log_msg = self.log_msg + "\n Turns remaining: Infinite\n"
            
            self.ticks_remaining = self.ticks_remaining - 1
        
        if self.duration < 1 and not self.infinite_duration:
            self.effect_cleanup(recipient_stats)

        self.duration = self.duration - 1

        return recipient_stats

        


    #### Undoes effect if the modfied values were tracked (aka if undoes_itself == True)
    def effect_cleanup(self, recipient_stats):
        self.log_msg = self.log_msg + "Duration for the effect: " + self.name + " is over."
        if self.undoes_itself:
            self.log_msg = self.log_msg + " Effect is being undone. \n"
            for stat in self.stats:
                recipient_stats[stat]["max"] = recipient_stats[stat]["max"] - self.modified_values[stat]["max"]
                recipient_stats[stat]["value"] = recipient_stats[stat]["value"] - self.modified_values[stat]["value"]
                if self.modified_values[stat]["max"] != 0:
                    self.log_msg = self.log_msg + stat + "maximum changed by: " + str(-self.modified_values[stat]["max"]) + "\n"
                if self.modified_values[stat]["value"] != 0:
                    self.log_msg = self.log_msg + stat + "current value changed by: " + str(-self.modified_values[stat]["value"]) + "\n"

        
        


