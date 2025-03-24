from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, TypedDict

class GameError(Exception):
    """Base exception for game-related errors."""
    pass

class InventoryFullError(GameError):
    """Raised when inventory is full."""
    pass

class InvalidCommandError(GameError):
    """Raised when an invalid command is entered."""
    pass

class GameCommands(Enum):
    """Available game commands."""
    LOOK = auto()
    TAKE = auto()
    MOVE = auto()
    USE = auto()
    INVENTORY = auto()
    QUIT = auto()
    HELP = auto()

class ObstacleType(Enum):
    """Types of obstacles in the game."""
    LOCKED = "locked"
    GUARD = "guard"
    PIT = "pit"
    CHEST = "chest"
    GATE = "gate"

@dataclass
class Obstacle:
    """Represents an obstacle in the game."""
    type: ObstacleType
    required_item: str
    message: str
    direction: Optional[str] = None

class Room(TypedDict):
    """Type definition for a room in the game world."""
    description: str
    exits: Dict[str, str]
    items: List[str]
    obstacle: Optional[Obstacle]

class Player:
    """Represents a player in the game."""
    
    def __init__(self, name: str, max_inventory: int = 4):
        """
        Initialize a new player.
        
        Args:
            name: Player's name
            max_inventory: Maximum inventory capacity
        """
        self.name = name
        self.inventory: List[str] = []
        self.location = "Dungeon Cell"
        self.max_inventory = max_inventory
    
    def add_item(self, item: str) -> bool:
        """
        Add an item to the player's inventory if there's space.
        
        Args:
            item: Item to add
            
        Returns:
            bool: True if item was added, False if inventory is full
            
        Raises:
            InventoryFullError: If inventory is at capacity
        """
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item)
            return True
        raise InventoryFullError(f"Inventory full! (Max {self.max_inventory} items)")
    
    def has_item(self, item: str) -> bool:
        """Check if the player has a specific item"""
        return item in self.inventory
    
    def remove_item(self, item: str) -> bool:
        """Remove an item from the player's inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def show_inventory(self):
        """Display the player's inventory"""
        if self.inventory:
            print(f"\nInventory ({len(self.inventory)}/{self.max_inventory}):")
            for item in self.inventory:
                print(f"- {item}")
        else:
            print("\nYour bag is empty.")


def create_world():
    """Create the game world with rooms, items, obstacles, and connections"""
    return {
        "Dungeon Cell": {
            "description": "You're in a dark stone cell. A rusty bed sits in the corner.",
            "exits": {"forward": "Corridor"},
            "items": ["Crowbar"],
            "obstacle": {"type": "locked", "required_item": "Cell Key", "message": "The cell door is locked!", "direction": "forward"}
        },
        "Corridor": {
            "description": "A dimly lit corridor stretches before you.",
            "exits": {"forward": "Guard Room", "right": "Storage Room"},
            "items": [],
            "obstacle": None
        },
        "Guard Room": {
            "description": "A guard snores loudly in a chair. There's a door behind him.",
            "exits": {"back": "Corridor", "forward": "Kitchen"},
            "items": [],
            "obstacle": {"type": "guard", "required_item": "Torch", "message": "The guard blocks your path!", "direction": "forward"}
        },
        "Storage Room": {
            "description": "Dusty shelves line the walls. Something glints in the corner.",
            "exits": {"back": "Corridor", "left": "Library"},
            "items": ["Rope"],
            "obstacle": {"type": "locked", "required_item": "Iron Key", "message": "The door to the library is locked!", "direction": "left"}
        },
        "Kitchen": {
            "description": "A filthy kitchen with moldy food. A torch burns on the wall.",
            "exits": {"back": "Guard Room", "right": "Armory"},
            "items": ["Torch", "Food"],
            "obstacle": None
        },
        "Armory": {
            "description": "Weapons rust on racks. A strongbox sits in the center.",
            "exits": {"back": "Kitchen", "north": "Treasury"},
            "items": [],
            "obstacle": {"type": "chest", "required_item": "Crowbar", "message": "The strongbox is jammed shut!", "direction": None}
        },
        "Library": {
            "description": "Ancient books line crumbling shelves. A map peeks from a desk.",
            "exits": {"right": "Storage Room", "forward": "Study"},
            "items": ["Map", "Book"],
            "obstacle": None
        },
        "Study": {
            "description": "A scholar's study with a desk and chair. A note reveals a secret.",
            "exits": {"back": "Library", "down": "Secret Passage"},
            "items": ["Note"],
            "obstacle": None
        },
        "Secret Passage": {
            "description": "A narrow hidden passage with strange markings on the wall.",
            "exits": {"up": "Study", "forward": "Torture Chamber"},
            "items": ["Gem"],
            "obstacle": None
        },
        "Torture Chamber": {
            "description": "A gruesome room with a gaping pit in the floor.",
            "exits": {"back": "Secret Passage", "across": "Courtyard"},
            "items": [],
            "obstacle": {"type": "pit", "required_item": "Rope", "message": "The pit is too wide to jump!", "direction": "across"}
        },
        "Treasury": {
            "description": "Glittering treasures line the walls. A suspicious guard stands watch.",
            "exits": {"south": "Armory"},
            "items": ["Gold Coin"],
            "obstacle": {"type": "guard", "required_item": "Gem", "message": "A guard blocks access to the treasure!", "direction": None}
        },
        "Courtyard": {
            "description": "Moonlight reveals a massive gate. It's locked.",
            "exits": {"forward": "Exit Gate"},
            "items": [],
            "obstacle": {"type": "gate", "required_item": "Cell Key", "message": "The gate is securely locked!", "direction": "forward"}
        },
        "Exit Gate": {
            "description": "Freedom awaits beyond this point!",
            "exits": {},
            "items": [],
            "obstacle": None
        }
    }


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'-'*40}")
    print(f" {text}")
    print(f"{'-'*40}")


def handle_locked_chest(player, world, item):
    """Handle the special case of the strongbox in the armory"""
    if player.location == "Armory" and item == "Crowbar":
        obstacle = world["Armory"]["obstacle"]
        if obstacle and obstacle["type"] == "chest":
            print("\nYou pry open the strongbox with the crowbar!")
            world["Armory"]["items"].append("Cell Key")
            world["Armory"]["items"].append("Iron Key")
            world["Armory"]["obstacle"] = None
            player.remove_item("Crowbar")  # Crowbar breaks after use
            print("You found a Cell Key and an Iron Key inside!")
            return True
    return False


def handle_special_interactions(player, world):
    """Handle special interactions based on location"""
    if player.location == "Library" and "Book" in world["Library"]["items"]:
        print("\nOne of the books looks interesting. The title reads 'Secret Passages'.")
    
    if player.location == "Study" and "Note" in world["Study"]["items"]:
        print("\nA note on the desk reads: 'Pull the third candle to reveal the passage down.'")
    
    if player.location == "Treasury" and player.has_item("Gem"):
        print("\nThe guard is mesmerized by your glittering gem!")
        print("'Such beauty!' he exclaims, stepping aside to let you access the treasure.")
        world["Treasury"]["obstacle"] = None


def handle_look(player, world):
    """Handle the look action"""
    current_room = world[player.location]
    print(f"\n{current_room['description']}")
    
    # Display items in the room
    if current_room["items"]:
        print("\nYou see:")
        for item in current_room["items"]:
            print(f"- {item}")
    else:
        print("\nThere are no items of interest here.")
    
    # Display obstacles if present
    if current_room["obstacle"]:
        print(f"\n! {current_room['obstacle']['message']}")
    
    # Special interactions based on location
    handle_special_interactions(player, world)


def handle_take(player, world):
    """Handle the take action"""
    current_room = world[player.location]
    if not current_room["items"]:
        print("\nThere's nothing to take here.")
        return
    
    print("\nWhat would you like to take?")
    for i, item in enumerate(current_room["items"], 1):
        print(f"{i}. {item}")
    
    try:
        choice = int(input("\nEnter number (0 to cancel): "))
        if choice == 0:
            return
        
        item = current_room["items"][choice - 1]
        if player.add_item(item):
            current_room["items"].remove(item)
            print(f"\nYou picked up the {item}.")
            
            # Special case for finding specific items
            if item == "Book":
                print("You opened the book. It contains information about a secret passage in the study.")
            elif item == "Note":
                print("The note reveals that pulling the third candle in the study reveals a passage.")
    except (ValueError, IndexError):
        print("\nInvalid choice.")


def handle_move(player: Player, world: Dict[str, Room]) -> None:
    """
    Handle player movement between rooms.
    
    Args:
        player: Current player instance
        world: Game world dictionary
        
    Raises:
        InvalidCommandError: If invalid direction is chosen
    """
    current_room = world[player.location]
    available_exits = list(current_room["exits"].keys())
    
    if not available_exits:
        print("\nThere are no exits from here.")
        return
    
    print("\nAvailable directions:")
    for i, direction in enumerate(available_exits, 1):
        print(f"{i}. {direction}")
    
    try:
        choice = int(input("\nEnter number (0 to cancel): "))
        if choice == 0:
            return
        
        if not 0 <= choice - 1 < len(available_exits):
            raise InvalidCommandError("Invalid direction choice")
            
        direction = available_exits[choice - 1]
        handle_movement_execution(player, world, current_room, direction)
        
    except ValueError:
        raise InvalidCommandError("Please enter a valid number")


def handle_movement_execution(player: Player, world: Dict[str, Room], 
                            current_room: Room, direction: str) -> None:
    """
    Execute the movement after validation.
    
    Args:
        player: Current player instance
        world: Game world dictionary
        current_room: Current room data
        direction: Direction to move
    """
    obstacle = current_room["obstacle"]
    if obstacle and (obstacle["direction"] == direction or obstacle["direction"] is None):
        print(f"\n! {obstacle['message']}")
        if input("Would you like to try using an item? (y/n) ").lower() == 'y':
            handle_use_item(player, world, obstacle["required_item"])
        return
    
    new_location = current_room["exits"][direction]
    print(f"\nYou move {direction} to the {new_location}...")
    player.location = new_location


def handle_use_item(player, world, required_item=None):
    """Handle using an item from inventory"""
    if not player.inventory:
        print("\nYou don't have any items to use.")
        return
    
    # If a specific item is required but player doesn't have it
    if required_item and not player.has_item(required_item):
        print(f"\nYou need a {required_item} for this, but you don't have one.")
        return
    
    # If specific item required and player has it
    if required_item and player.has_item(required_item):
        item_to_use = required_item
    # Otherwise let player choose
    else:
        print("\nWhich item would you like to use?")
        for i, item in enumerate(player.inventory, 1):
            print(f"{i}. {item}")
        
        try:
            choice = int(input("\nEnter number (0 to cancel): "))
            if choice == 0:
                return
            
            item_to_use = player.inventory[choice - 1]
        except (ValueError, IndexError):
            print("\nInvalid choice.")
            return
    
    # Handle the strongbox in the armory as a special case
    if handle_locked_chest(player, world, item_to_use):
        return
    
    # Check if item can be used on current obstacle
    current_room = world[player.location]
    obstacle = current_room["obstacle"]
    
    if obstacle and item_to_use == obstacle["required_item"]:
        print(f"\nYou used the {item_to_use} successfully!")
        
        # Special messages for different obstacle types
        if obstacle["type"] == "locked":
            print(f"You unlocked the door with the {item_to_use}.")
        elif obstacle["type"] == "guard":
            print(f"You distracted the guard with the {item_to_use}.")
        elif obstacle["type"] == "pit":
            print(f"You used the {item_to_use} to cross the pit safely.")
        elif obstacle["type"] == "gate":
            print(f"You unlocked the gate with the {item_to_use}.")
        
        # Remove obstacle
        current_room["obstacle"] = None
        
        # Consumable items get removed after use
        if item_to_use in ["Cell Key", "Iron Key"]:
            player.remove_item(item_to_use)
    else:
        print(f"\nYou used the {item_to_use}, but nothing happened.")


def main() -> None:
    """Main game loop."""
    try:
        print_header("DUNGEON ESCAPE ADVENTURE")
        print("You wake up in a mysterious dungeon cell...")
        print("Find a way to escape through the exit gate!")
        print("\nCommands: look, take, move, use, inventory, quit")
        
        player_name = input("\nEnter your character's name: ")
        player = Player(player_name)
        world = create_world()
        
        while True:
            print(f"\n[Current Location: {player.location}]")
            try:
                command = input("\nWhat will you do? ").lower()
                
                if command == "look":
                    handle_look(player, world)
                elif command == "take":
                    handle_take(player, world)
                elif command == "move":
                    handle_move(player, world)
                elif command == "use":
                    handle_use_item(player, world)
                elif command in ("inventory", "i"):
                    player.show_inventory()
                elif command in ("quit", "q"):
                    print("\nThanks for playing!")
                    break
                elif command in ("help", "h"):
                    print("\nCommands: look, take, move, use, inventory, quit")
                else:
                    raise InvalidCommandError("Invalid command. Type 'help' for commands.")
                
                if player.location == "Exit Gate":
                    print_header("VICTORY")
                    print(f"Congratulations {player.name}! You've escaped!")
                    break
                    
            except GameError as e:
                print(f"\nError: {str(e)}")
            
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        
if __name__ == "__main__":
    main()