





class Ability():
    def __init__(self, ability, server_id):
        self.server_id = server_id
        self.ruleset = ability["ruleset"]
        self.name = ability["name"]
        self.description = ability["description"]
        self.type = ability["type"]
        self.range = ability["range"]
        self.self_effects = ability["self_effects"]
        self.effects = ability["effects"]