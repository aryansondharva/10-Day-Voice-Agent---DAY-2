import json
import random
import time
from datetime import datetime


class WorldState:
    def __init__(self):
        self.state = {
            "player": {
                "name": "Wanderer",
                "hp": 100,
                "max_hp": 100,
                "fear": 0,            # 0–100 scale
                "status": [],
            },
            "inventory": [
                {"item": "Rusty Dagger", "description": "Metal flakes off the blade like dead skin."},
                {"item": "Dim Soulstone", "description": "A faint heartbeat pulses inside."},
                {"item": "Torn Map", "description": "Stains look disturbingly like dried blood."},
            ],
            "location": {
                "name": "The Whispering Gravepath",
                "description": (
                    "A narrow trail lined with crooked gravestones. The soil shifts beneath your feet as if something "
                    "moves just under the surface. Cold mist coils around your legs like grasping hands."
                ),
            },
            "time_started": time.time(),
        }

    # --------------------------
    #     CORE GAME METHODS
    # --------------------------

    def get_state(self):
        return self.state

    # Dice roll with horror flavor
    def roll_dice(self, sides=20):
        result = random.randint(1, sides)

        # Increase fear when rolling poorly
        if result <= 5:
            self.state["player"]["fear"] += random.randint(3, 7)
        elif result >= 18:
            self.state["player"]["fear"] = max(0, self.state["player"]["fear"] - random.randint(1, 5))

        # HP decay when fear is high
        if self.state["player"]["fear"] >= 70:
            self.state["player"]["hp"] -= random.randint(1, 4)

        return result

    # --------------------------
    #       INVENTORY
    # --------------------------

    def get_inventory_description(self):
        desc = "Your bag creaks open... Inside, wrapped in shadows:\n"
        for item in self.state["inventory"]:
            desc += f"• {item['item']}: {item['description']}\n"
        return desc

    def add_inventory_item(self, item_name):
        creepy_descriptions = [
            "It feels warm... like it's breathing.",
            "It whispers faintly when touched.",
            "Its shadow doesn't match its shape.",
            "Holding it makes your heartbeat slow unnaturally.",
            "A black ooze seeps from tiny cracks in it.",
        ]

        self.state["inventory"].append({
            "item": item_name,
            "description": random.choice(creepy_descriptions)
        })

        return f"{item_name} added to your cursed inventory."

    def remove_inventory_item(self, item_name):
        for item in self.state["inventory"]:
            if item["item"].lower() == item_name.lower():
                self.state["inventory"].remove(item)
                return f"You discard {item_name}. The darkness seems displeased."
        return f"{item_name} is not in your inventory."

    # --------------------------
    #       CHARACTER SHEET
    # --------------------------

    def get_character_sheet(self):
        p = self.state["player"]
        sheet = (
            f"🩸 CHARACTER SHEET – {p['name']} 🩸\n"
            f"HP: {p['hp']} / {p['max_hp']}\n"
            f"Fear: {p['fear']} / 100\n"
            f"Status Effects: {', '.join(p['status']) if p['status'] else 'None'}\n"
        )
        return sheet

    # --------------------------
    #       HORROR EVENTS
    # --------------------------

    def random_horror_event(self):
        events = [
            "A whisper brushes against your ear: 'Don't turn around.'",
            "Your shadow moves a moment later than you do.",
            "Something small and cold grabs your ankle... then lets go.",
            "You hear distant footsteps—but they match your heartbeat.",
            "Your vision flickers; for a split second, everything turns red.",
        ]

        # Chance increases with fear
        chance = 10 + int(self.state["player"]["fear"] / 10)
        if random.randint(1, 100) <= chance:
            event = random.choice(events)
            self.state["player"]["fear"] += random.randint(2, 5)
            return event
        return None

    # --------------------------
    #       SAVE & LOAD
    # --------------------------

    def save_game(self):
        try:
            with open("shadowrealm_save.json", "w") as f:
                json.dump(self.state, f, indent=4)
            return "Your suffering has been preserved."
        except:
            return "The shadows refuse to save your progress."

    def load_game(self):
        try:
            with open("shadowrealm_save.json", "r") as f:
                self.state = json.load(f)
            return "The darkness remembers you well..."
        except:
            return "No echoes of your past exist here."


