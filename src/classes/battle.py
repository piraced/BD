import src.db_operations as db
import src.classes.creature
import src.classes.character
from openpyxl.utils.cell import get_column_letter



class Battle():

    def __init__(self, encounter, server_id, characters):
        self.server_id = server_id
        self.map = db.get_object("maps", encounter["map"], server_id)
        self.map_length = self.map["length"]
        self.map_height = self.map["height"]
        self.name = encounter["name"]
        self.description = encounter["description"]
        self.entities = []
        self.turn = 1
        self.char_turn = 0

        self.thread = None

        self.current_char_actual_x = 0
        self.current_char_actual_y = 0
        self.current_char_actual_moves = 0
        self.current_char_moved = False

        for creature in encounter["creatures"]:
            creature_data = db.get_object("creatures", creature["name"], self.server_id)
            self.entities.append(src.classes.creature.Creature(creature_data, creature["length_coord"], creature["height_coord"], self.server_id, self.thread))

        for character in characters:
            character_data = db.get_object("characters", character["name"], self.server_id)
            self.entities.append(src.classes.character.Character(character_data, character["length_coord"], character["height_coord"], self.server_id, self.thread))

        self.entities.sort(reverse=True, key=lambda x: x.initiative)






    def get_current_entity(self):
        return self.entities[self.char_turn]
    

    async def initialize_char_turn(self):
        self.current_char_actual_x = self.get_current_entity().x
        self.current_char_actual_y = self.get_current_entity().y
        self.current_char_moved = False
        await self.get_current_entity().initialize_turn(self.thread)
        self.current_char_actual_moves = self.get_current_entity().speed

    async def initiative_logs(self):
        msg = ""
        for entity in self.entities:
            msg = msg + entity.init_log_rez + "\n"
        await self.thread.send(msg)

    async def confirm_move(self):
        msg = f"{self.name} moved from {get_column_letter(self.current_char_actual_x)}{self.current_char_actual_y} to {get_column_letter(self.get_current_entity().x)}{self.get_current_entity().y}"

        self.current_char_actual_x = self.get_current_entity().x
        self.current_char_actual_y = self.get_current_entity().y
        self.get_current_entity().speed = 0
        self.current_char_moved = True

        await self.thread.send(msg)

    async def end_turn(self):
        msg = f"{self.get_current_entity().name} ends their turn."
        entity_count = len(self.entities)
        if self.char_turn + 1 == entity_count:
            self.char_turn = 0
        else:
            self.char_turn = self.char_turn + 1
        await self.thread.send(msg)
        await self.initialize_char_turn()
    