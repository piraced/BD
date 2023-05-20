import pymongo
import os
import sys
from dotenv import load_dotenv

this = sys.modules[__name__]
this.client = None

def get_database():
    if(this.client is None):
        load_dotenv()
        this.client = pymongo.MongoClient(os.getenv('CONNECTION_STRING'))
    return this.client["TTRPGbot"]
    
def initialize_database():
    names = get_database().list_collection_names()
    if 'rulesets' not in names:
        get_database().create_collection(name='rulesets')
    if 'selected_ruleset' not in names:
        get_database().create_collection(name='selected_ruleset')
    if 'macros' not in names:
        get_database().create_collection(name='items')
    if 'abilities' not in names:
        get_database().create_collection(name='abilities')
    if 'effects' not in names:
        get_database().create_collection(name='effects')
    if 'characters' not in names:
        get_database().create_collection(name='characters')
    if 'creatures' not in names:
        get_database().create_collection(name='creatures')
    if 'maps' not in names:
        get_database().create_collection(name='maps')
    

def get_rulesets(server_id):
    rulesets = get_database()["rulesets"]
    results = rulesets.find({"server_id": server_id})
    return list(results)

def get_ruleset(name, server_id):
    rulesets = get_database()["rulesets"]
    return rulesets.find_one({"name": name, "server_id" : server_id})

def select_ruleset(ruleset_name, server_id):
    get_database()["selected_ruleset"].replace_one(filter= {"selected": True, "server_id" : server_id},replacement= {"name": ruleset_name, "selected": True, "server_id": server_id}, upsert=True)

def get_selected_ruleset(server_id):
     return get_database()["selected_ruleset"].find_one(filter= {"selected": True, "server_id" : server_id })

def delete_ruleset(name, server_id):
    get_database()["rulesets"].delete_one({"name" : name, "server_id" : server_id})

def replace_ruleset(name, server_id, document):
    get_database()["rulesets"].find_one_and_replace(filter={"name" : name, "server_id" : server_id}, replacement=document)

def does_ruleset_exist( name, server_id):
    objects = get_database()["rulesets"]
    rez = objects.find_one({"name": name, "server_id" : server_id})
    if rez is None:
        return False
    else:
        return True



def get_object(object_type, name, server_id):
    objects = get_database()[object_type]
    return objects.find_one({"name": name, "ruleset" : get_selected_ruleset(server_id)["name"], "server_id" : server_id})

def get_all_objects(object_type, server_id):
    return get_database()[object_type].find({"ruleset" : get_selected_ruleset(server_id)["name"], "server_id" : server_id})

def delete_object(object_type, name, server_id):
    get_database()[object_type].delete_one({"name" : name,  "ruleset" : get_selected_ruleset(server_id)["name"], "server_id" : server_id})

def insert_object(object_type, document):
    get_database()[object_type].insert_one(document=document)

def replace_object(object_type, name, server_id, document):
    get_database()[object_type].find_one_and_replace(filter={"name" : name, "server_id" : server_id, "ruleset" : get_selected_ruleset(server_id)["name"]}, replacement=document)

def reset_character_player(player_id, server_id):
    get_database()["characters"].find_one_and_update(filter={ "player": player_id, "server_id": server_id, "ruleset": get_selected_ruleset(server_id)["name"]}, update={ '$set' : {"player": ""}})

def get_character_by_player(player_id, server_id):
    chars = get_database()["characters"]
    return chars.find_one({"server_id" : server_id, "ruleset" : get_selected_ruleset(server_id)["name"], "player": player_id})

def does_object_exist_in_ruleset(object_type, names_in, server_id):
    names = []
    names.clear()
    objects = get_database()[object_type]
    if isinstance(names_in, str):
        names.append(names_in)
    else:
        names = names_in
    for name in names:
        rez = objects.find_one({"name": name, "ruleset" : get_selected_ruleset(server_id)["name"], "server_id" : server_id})
        if rez is not None:
            return True
    return False
    
def does_stat_exist_in_ruleset(stat_name:str, server_id):
    ruleset = get_ruleset(get_selected_ruleset(server_id)["name"], server_id)
    if stat_name in ruleset["statistics"]:
        return True
    else:
        return False
    
def do_stats_exist_in_ruleset(stat_names:list, server_id):
    for stat_name in stat_names:
        if not does_stat_exist_in_ruleset(stat_name, server_id):
            return False
    return True

