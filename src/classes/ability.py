





class Ability():
    x = 0
    y = 0
    speed = 0

    def __init__(self, ability, server_id, player):
        self.player = player
        self.server_id = server_id
        self.ruleset = ability["ruleset"]
        self.name = ability["name"]
        self.description = ability["description"]
        self.type = ability["type"]
        self.range = int(ability["range"])
        self.self_effects = ability["self_effects"]
        self.effects = ability["effects"]