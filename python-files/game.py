import pygame
import random
import datetime
import sys
import os
import json
import math
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# -- CONFIGURATION ---------------------------------------------------------------
class Config:
    WIDTH, HEIGHT = 800, 600
    FPS = 60
    
    # Font sizes - ADJUSTABLE
    TITLE_FONT_SIZE = 32
    REQUEST_FONT_SIZE = 22
    SMALL_FONT_SIZE = 18
    BUTTON_FONT_SIZE = 20
    INFO_FONT_SIZE = 16
    
    # Game settings
    SEASON_LENGTH = 15
    MAX_HISTORY = 5
    REQUESTS_PER_DAY = 10
    SAVE_FILE = "throne_save.json"
    
    # Colors - Enhanced color scheme
    COLORS = {
        "GOLD": (255, 215, 0),          # Brighter gold
        "HAPPINESS": (50, 205, 50),     # Brighter green
        "FOOD": (255, 140, 0),          # Brighter orange
        "TRUST": (135, 206, 250),       # Brighter blue
        "BACKGROUND": (30, 30, 50),     # Darker background
        "TEXT": (255, 255, 255),        # White text
        "BUTTON_ACCEPT": (34, 139, 34),  # Forest green
        "BUTTON_REJECT": (220, 20, 60),  # Crimson
        "NEXT_DAY": (70, 130, 180),     # Steel blue
        "SEASON_TINT": {
            "Spring": (144, 238, 144, 80),  # Light green
            "Summer": (255, 255, 224, 80),  # Light yellow
            "Autumn": (255, 218, 185, 80),  # Peach
            "Winter": (176, 224, 230, 80)   # Powder blue
        },
        # Kingdom colors for map - more vibrant
        "PLAYER_KINGDOM": (220, 20, 60),      # Crimson
        "NORTHERN_KINGDOM": (50, 205, 50),   # Lime green
        "EASTERN_KINGDOM": (255, 215, 0),    # Gold
        "SOUTHERN_KINGDOM": (30, 144, 255),   # Dodger blue
        "HOUSE": (176, 196, 222),            # Light steel blue
        "RELATIONSHIP_COLORS": {
            "HATE": (220, 20, 60),        # Crimson
            "DISLIKE": (255, 140, 0),     # Dark orange
            "NEUTRAL": (192, 192, 192),   # Silver
            "LIKE": (50, 205, 50),        # Lime green
            "LOVE": (0, 191, 255)         # Deep sky blue
        },
        # UI element colors
        "PANEL_BG": (40, 40, 60),         # Dark blue panel
        "BORDER": (100, 100, 120),       # Border color
        "HIGHLIGHT": (255, 255, 200),     # Highlight color
        "SECTION_HEADER": (255, 215, 0),  # Gold for headers
        "STAT_POSITIVE": (50, 205, 50),   # Green for positive
        "STAT_NEGATIVE": (220, 20, 60),   # Red for negative
    }

# -- ENUMS -----------------------------------------------------------------------
class Scene(Enum):
    THRONE = "throne"
    MAP = "map"
    ACHIEVEMENTS = "achievements"
    GAME_OVER = "game_over"
    DIPLOMACY = "diplomacy"
    CHARACTER_INTERACTION = "character_interaction"

class Difficulty(Enum):
    EASY = {"Gold": 150, "Happiness": 70, "Food": 100, "Trust": 70}
    NORMAL = {"Gold": 100, "Happiness": 50, "Food": 75, "Trust": 50}
    HARD = {"Gold": 50, "Happiness": 30, "Food": 50, "Trust": 30}

class RelationshipLevel(Enum):
    HATE = -2
    DISLIKE = -1
    NEUTRAL = 0
    LIKE = 1
    LOVE = 2

class RegionType(Enum):
    KINGDOM = "kingdom"
    HOUSE = "house"

# -- CLASSES ---------------------------------------------------------------------
class Request:
    def __init__(self, text, effect, source, seasonal=False):
        self.text = text
        self.effect = effect
        self.source = source
        self.seasonal = seasonal

class MapRegion:
    def __init__(self, name, x, y, width, height, color, region_type):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.region_type = region_type
        self.relationship = 50  # 0-100, 50 is neutral
        self.trade_level = 0   # 0-5
        self.military_strength = random.randint(30, 70)
        self.special_resource = random.choice(["Gold", "Food", "Military"])
        self.diplomatic_benefit = {}  # Special benefits from good relations
        
    def draw(self, surface, font, selected=False):
        # Draw region with border
        color = [min(255, c + 50) for c in self.color] if selected else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, Config.COLORS["BORDER"], self.rect, 3, border_radius=8)
        
        # Only show additional info for kingdoms
        if self.region_type == RegionType.KINGDOM:
            # Draw name with background
            name_text = font.render(self.name, True, Config.COLORS["TEXT"])
            name_bg = pygame.Rect(self.rect.centerx - name_text.get_width()//2 - 5, 
                                 self.rect.y + 5, 
                                 name_text.get_width() + 10, 
                                 name_text.get_height() + 4)
            pygame.draw.rect(surface, (0, 0, 0, 180), name_bg, border_radius=4)
            surface.blit(name_text, name_bg.topleft)
            
            # Draw relationship indicator with bar
            rel_y = self.rect.y + 30
            rel_width = 80
            rel_height = 10
            rel_x = self.rect.centerx - rel_width // 2
            
            # Background bar
            pygame.draw.rect(surface, (50, 50, 50), (rel_x, rel_y, rel_width, rel_height), border_radius=5)
            
            # Fill bar based on relationship
            fill_width = int(rel_width * self.relationship / 100)
            if self.relationship >= 70:
                fill_color = Config.COLORS["RELATIONSHIP_COLORS"]["LIKE"]
            elif self.relationship >= 30:
                fill_color = Config.COLORS["RELATIONSHIP_COLORS"]["NEUTRAL"]
            else:
                fill_color = Config.COLORS["RELATIONSHIP_COLORS"]["DISLIKE"]
                
            pygame.draw.rect(surface, fill_color, (rel_x, rel_y, fill_width, rel_height), border_radius=5)
            pygame.draw.rect(surface, Config.COLORS["BORDER"], (rel_x, rel_y, rel_width, rel_height), 1, border_radius=5)
            
            # Draw special resource with icon
            resource_text = font.render(self.special_resource, True, Config.COLORS["HIGHLIGHT"])
            resource_y = self.rect.y + 50
            surface.blit(resource_text, (self.rect.centerx - resource_text.get_width()//2, resource_y))
        
    def contains_point(self, pos):
        return self.rect.collidepoint(pos)

class Character:
    def __init__(self, name, image, position, role):
        self.name = name
        self.image = image
        self.position = position
        self.role = role
        self.rect = pygame.Rect(position[0], position[1], 100, 150)
        self.relationships = {}  # Relationships with other characters
        self.faction_opinions = {}  # Opinions about factions
        self.dialogue = []  # Dialogue lines
        self.personality_traits = []  # Personality traits
        self.backstory = ""  # Character backstory
        
    def set_relationship(self, other_character, level):
        """Set relationship with another character"""
        self.relationships[other_character] = level
        
    def set_faction_opinion(self, faction, level):
        """Set opinion about a faction"""
        self.faction_opinions[faction] = level
        
    def get_relationship_color(self, other_character):
        """Get color for relationship display"""
        if other_character not in self.relationships:
            return Config.COLORS["RELATIONSHIP_COLORS"]["NEUTRAL"]
        
        level = self.relationships[other_character]
        if level <= RelationshipLevel.HATE.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["HATE"]
        elif level <= RelationshipLevel.DISLIKE.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["DISLIKE"]
        elif level <= RelationshipLevel.NEUTRAL.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["NEUTRAL"]
        elif level <= RelationshipLevel.LIKE.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["LIKE"]
        else:
            return Config.COLORS["RELATIONSHIP_COLORS"]["LOVE"]
    
    def get_faction_opinion_color(self, faction):
        """Get color for faction opinion display"""
        if faction not in self.faction_opinions:
            return Config.COLORS["RELATIONSHIP_COLORS"]["NEUTRAL"]
        
        level = self.faction_opinions[faction]
        if level <= RelationshipLevel.HATE.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["HATE"]
        elif level <= RelationshipLevel.DISLIKE.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["DISLIKE"]
        elif level <= RelationshipLevel.NEUTRAL.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["NEUTRAL"]
        elif level <= RelationshipLevel.LIKE.value:
            return Config.COLORS["RELATIONSHIP_COLORS"]["LIKE"]
        else:
            return Config.COLORS["RELATIONSHIP_COLORS"]["LOVE"]
    
    def draw(self, surface, font, selected=False):
        # Draw character image with border
        scaled_image = pygame.transform.scale(self.image, (100, 150))
        surface.blit(scaled_image, self.position)
        
        # Draw selection indicator if selected
        if selected:
            pygame.draw.rect(surface, Config.COLORS["HIGHLIGHT"], self.rect, 3, border_radius=5)
        
        # Draw name with background
        name_text = font.render(self.name, True, Config.COLORS["TEXT"])
        name_bg = pygame.Rect(self.position[0] + 50 - name_text.get_width()//2 - 5, 
                             self.position[1] - 25, 
                             name_text.get_width() + 10, 
                             name_text.get_height() + 4)
        pygame.draw.rect(surface, (0, 0, 0, 180), name_bg, border_radius=4)
        surface.blit(name_text, name_bg.topleft)
        
    def contains_point(self, pos):
        return self.rect.collidepoint(pos)

class FloatingText:
    def __init__(self, x, y, text, color, lifetime=60):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.alpha = 255
        self.offset_x = random.randint(-20, 20)  # Random horizontal offset
        
    def update(self):
        self.y -= 1
        self.lifetime -= 1
        self.alpha = int(255 * (self.lifetime / 60))
        return self.lifetime > 0
        
    def draw(self, surface, font):
        text_surf = font.render(self.text, True, self.color[:3])
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x + self.offset_x, self.y))

class GameState:
    def __init__(self, difficulty=Difficulty.NORMAL):
        self.kingdom_stats = difficulty.value.copy()
        self.advisor_trust = difficulty.value["Trust"]
        self.day_count = 0
        self.season_index = 0
        self.season_names = ["Spring", "Summer", "Autumn", "Winter"]
        self.current_request = None
        self.request_history = []
        self.achievements = {
            "First Decision": False,
            "Generous Ruler": False,
            "Frugal Leader": False,
            "Seasoned Veteran": False,
            "Trusted Advisor": False,
            "Prosperous Kingdom": False,
            "Master Diplomat": False,
            "Bard's Friend": False,
            "People Person": False
        }
        self.achievements_unlocked = []
        self.difficulty = difficulty
        self.game_over = False
        self.victory = False
        self.decision_count = 0
        self.total_gold_spent = 0
        self.total_gold_earned = 0
        self.requests_today = 0  # Track requests processed today
        self.bard_visited = False  # Track if bard has visited
        
        # Initialize map regions with new layout
        self.map_regions = {}
        self.setup_map_regions()
        
        self.selected_region = None
        
        # Initialize characters
        self.characters = {
            "Advisor": Character("Advisor", advisor_img, (200, 400), "Advisor"),
            "Villager": Character("Villager", villager_img, (550, 400), "Villager"),
            "Bard": Character("Bard", bard_img, (700, 400), "Bard")
        }
        
        # Set up character relationships and opinions
        self.setup_character_relationships()
        
        # Initialize diplomatic benefits
        self.update_diplomatic_benefits()
        
        # Track last decision effects for display
        self.last_decision_effects = {}
        
    def setup_map_regions(self):
        """Set up the map regions according to the new vision"""
        # Kingdoms (clickable for diplomacy) - larger and better positioned
        self.map_regions["Player Kingdom"] = MapRegion(
            "Player Kingdom", 350, 250, 120, 120, 
            Config.COLORS["PLAYER_KINGDOM"], RegionType.KINGDOM
        )
        self.map_regions["Northern Kingdom"] = MapRegion(
            "Northern Kingdom", 150, 120, 120, 120, 
            Config.COLORS["NORTHERN_KINGDOM"], RegionType.KINGDOM
        )
        self.map_regions["Eastern Kingdom"] = MapRegion(
            "Eastern Kingdom", 550, 120, 120, 120, 
            Config.COLORS["EASTERN_KINGDOM"], RegionType.KINGDOM
        )
        self.map_regions["Southern Kingdom"] = MapRegion(
            "Southern Kingdom", 350, 400, 120, 120, 
            Config.COLORS["SOUTHERN_KINGDOM"], RegionType.KINGDOM
        )
        
        # Houses (non-interactive, just for visual) - smaller and better distributed
        house_positions = [
            (100, 250), (250, 300), (450, 300), (600, 250),
            (200, 400), (500, 400), (300, 200), (400, 350),
            (150, 350), (550, 350), (350, 150), (450, 500)
        ]
        
        for i, pos in enumerate(house_positions):
            self.map_regions[f"House {i+1}"] = MapRegion(
                f"House {i+1}", pos[0], pos[1], 50, 50, 
                Config.COLORS["HOUSE"], RegionType.HOUSE
            )
    
    def setup_character_relationships(self):
        """Set up character relationships and faction opinions"""
        # Advisor relationships
        self.characters["Advisor"].set_relationship("Villager", RelationshipLevel.DISLIKE.value)
        self.characters["Advisor"].set_relationship("Bard", RelationshipLevel.LIKE.value)
        self.characters["Advisor"].set_faction_opinion("Northern Kingdom", RelationshipLevel.LIKE.value)
        self.characters["Advisor"].set_faction_opinion("Eastern Kingdom", RelationshipLevel.DISLIKE.value)
        self.characters["Advisor"].set_faction_opinion("Southern Kingdom", RelationshipLevel.NEUTRAL.value)
        self.characters["Advisor"].personality_traits = ["Pragmatic", "Loyal", "Cautious"]
        self.characters["Advisor"].backstory = "A trusted advisor who has served the royal family for decades. Values stability and tradition."
        self.characters["Advisor"].dialogue = [
            "Sire, I advise caution in this matter.",
            "We must consider the long-term implications of this decision.",
            "The kingdom's stability must be our foremost concern.",
            "I have served your family for many years, and I wish only the best for our people."
        ]
        
        # Villager relationships
        self.characters["Villager"].set_relationship("Advisor", RelationshipLevel.DISLIKE.value)
        self.characters["Villager"].set_relationship("Bard", RelationshipLevel.NEUTRAL.value)
        self.characters["Villager"].set_faction_opinion("Northern Kingdom", RelationshipLevel.NEUTRAL.value)
        self.characters["Villager"].set_faction_opinion("Eastern Kingdom", RelationshipLevel.DISLIKE.value)
        self.characters["Villager"].set_faction_opinion("Southern Kingdom", RelationshipLevel.LIKE.value)
        self.characters["Villager"].personality_traits = ["Practical", "Hardworking", "Concerned"]
        self.characters["Villager"].backstory = "A representative of the common people, trying to make ends meet in challenging times."
        self.characters["Villager"].dialogue = [
            "My family struggles to make ends meet, Your Majesty.",
            "The people need your help, Sire.",
            "We work hard but have little to show for it.",
            "Please consider the needs of the common folk."
        ]
        
        # Bard relationships
        self.characters["Bard"].set_relationship("Advisor", RelationshipLevel.LIKE.value)
        self.characters["Bard"].set_relationship("Villager", RelationshipLevel.NEUTRAL.value)
        self.characters["Bard"].set_faction_opinion("Northern Kingdom", RelationshipLevel.LOVE.value)
        self.characters["Bard"].set_faction_opinion("Eastern Kingdom", RelationshipLevel.NEUTRAL.value)
        self.characters["Bard"].set_faction_opinion("Southern Kingdom", RelationshipLevel.DISLIKE.value)
        self.characters["Bard"].personality_traits = ["Charismatic", "Well-traveled", "Perceptive"]
        self.characters["Bard"].backstory = "A wandering bard who has seen much of the world and shares tales of distant lands."
        self.characters["Bard"].dialogue = [
            "I have traveled far and wide, Your Majesty, and seen many wonders.",
            "The people sing songs of your rule, Sire.",
            "A good ruler listens to many voices before making a decision.",
            "I have heard tales of the Northern Kingdom's prosperity. Perhaps we could learn from them."
        ]
        
    def update_diplomatic_benefits(self):
        """Update benefits based on diplomatic relationships"""
        self.diplomatic_benefits = {"Gold": 0, "Food": 0, "Happiness": 0, "Trust": 0}
        
        for name, region in self.map_regions.items():
            if region.region_type == RegionType.KINGDOM and region.relationship >= 70:  # Good relations
                if region.special_resource == "Gold" and region.trade_level > 0:
                    self.diplomatic_benefits["Gold"] += region.trade_level * 2
                elif region.special_resource == "Food" and region.trade_level > 0:
                    self.diplomatic_benefits["Food"] += region.trade_level * 3
                elif region.special_resource == "Military" and region.relationship >= 80:
                    self.diplomatic_benefits["Trust"] += 5
                
                # Happiness bonus for good relations with all factions
                self.diplomatic_benefits["Happiness"] += 1
                
    def advance_day(self):
        self.day_count += 1
        self.requests_today = 0  # Reset daily request counter
        self.bard_visited = False  # Reset bard visit status
        
        # Apply diplomatic benefits
        for stat, value in self.diplomatic_benefits.items():
            if stat == "Trust":
                self.advisor_trust = min(100, self.advisor_trust + value)
            else:
                self.kingdom_stats[stat] = min(100, self.kingdom_stats[stat] + value)
        
        # Check if season should advance
        if self.day_count % Config.SEASON_LENGTH == 0:
            self.advance_season()
            
        # Chance for random event
        return trigger_random_event()
        
    def advance_season(self):
        self.season_index = (self.season_index + 1) % len(self.season_names)
        name = self.season_names[self.season_index]
        
        # Apply seasonal stat change
        season_effects = {
            "Spring": {"Happiness": 10},
            "Summer": {"Gold": 20},
            "Autumn": {"Food": 15},
            "Winter": {"Food": -20}
        }
        
        for stat, delta in season_effects[name].items():
            self.kingdom_stats[stat] = max(0, self.kingdom_stats[stat] + delta)
            
        # Check for seasonal achievement
        if self.season_index == 0 and self.day_count >= Config.SEASON_LENGTH * 4:
            self.unlock_achievement("Seasoned Veteran")
            
        # Queue a fresh request at season start
        self.current_request = self.choose_request()
        
    def choose_request(self):
        # 15% chance for bard request if not visited today
        if not self.bard_visited and random.random() < 0.15:
            req = random.choice(bard_requests).copy()
            req["source"] = "Bard"
            return Request(req["text"], req["effect"], req["source"])
            
        # 20% chance the advisor steps forward
        if random.random() < 0.2:
            req = random.choice(advisor_requests).copy()
            req["source"] = "Advisor"
            return Request(req["text"], req["effect"], req["source"])
            
        # Otherwise a villager, with 30% chance season-themed
        if random.random() < 0.3:
            req = random.choice(seasonal_requests[self.season_names[self.season_index]]).copy()
            return Request(req["text"], req["effect"], "Villager", seasonal=True)
        else:
            req = random.choice(base_requests).copy()
            return Request(req["text"], req["effect"], "Villager")
            
    def process_decision(self, accepted):
        if not self.current_request:
            return
            
        self.decision_count += 1
        self.requests_today += 1  # Increment daily request counter
        
        # Track if bard was visited
        if self.current_request.source == "Bard":
            self.bard_visited = True
            if self.decision_count >= 5:  # After a few decisions
                self.unlock_achievement("Bard's Friend")
        
        if self.decision_count == 1:
            self.unlock_achievement("First Decision")
            
        # Apply effects
        mult = 1 if accepted else 0.5
        sign = 1 if accepted else -1
        
        changes = {}
        for stat, delta in self.current_request.effect.items():
            change = int(delta * mult) * sign
            changes[stat] = change
            
            if stat == "Trust":
                self.advisor_trust = max(0, min(100, self.advisor_trust + change))
            else:
                self.kingdom_stats[stat] = max(0, min(100, self.kingdom_stats[stat] + change))
                
                # Track gold for achievements
                if stat == "Gold":
                    if change > 0:
                        self.total_gold_earned += change
                    else:
                        self.total_gold_spent += abs(change)
                        
        # Store last decision effects for display
        self.last_decision_effects = changes
        
        # Add to history
        self.request_history.append({
            "text": self.current_request.text,
            "accepted": accepted,
            "day": self.day_count,
            "season": self.season_names[self.season_index],
            "changes": changes
        })
        
        # Keep history limited
        if len(self.request_history) > Config.MAX_HISTORY:
            self.request_history.pop(0)
            
        # Check achievements
        if self.total_gold_spent >= 100:
            self.unlock_achievement("Generous Ruler")
        if self.total_gold_earned >= 100:
            self.unlock_achievement("Frugal Leader")
        if self.advisor_trust >= 80:
            self.unlock_achievement("Trusted Advisor")
        if all(val >= 100 for val in self.kingdom_stats.values()):
            self.unlock_achievement("Prosperous Kingdom")
            
        # Check for people person achievement (good relations with all characters)
        if all(char.relationships.get(other, RelationshipLevel.NEUTRAL.value) >= RelationshipLevel.LIKE.value 
               for name, char in self.characters.items() 
               for other in self.characters.keys() if other != name):
            self.unlock_achievement("People Person")
            
        # Check game state
        self.check_game_state()
        
        # Get next request if we haven't reached the daily limit
        if self.requests_today < Config.REQUESTS_PER_DAY:
            self.current_request = self.choose_request()
        else:
            self.current_request = None  # No more requests today
            
        return changes
        
    def check_game_state(self):
        # Check for failure
        if self.advisor_trust <= 0 or any(val <= 0 for val in self.kingdom_stats.values()):
            self.game_over = True
            self.victory = False
            return
            
        # Check for victory
        if self.advisor_trust >= 80 and all(val >= 100 for val in self.kingdom_stats.values()):
            self.game_over = True
            self.victory = True
            return
            
    def unlock_achievement(self, name):
        if not self.achievements.get(name, False):
            self.achievements[name] = True
            self.achievements_unlocked.append(name)
            if achievement_sound:
                achievement_sound.play()
            return True
        return False
        
    def to_dict(self):
        return {
            "kingdom_stats": self.kingdom_stats,
            "advisor_trust": self.advisor_trust,
            "day_count": self.day_count,
            "season_index": self.season_index,
            "achievements": self.achievements,
            "difficulty": self.difficulty.name,
            "decision_count": self.decision_count,
            "total_gold_spent": self.total_gold_spent,
            "total_gold_earned": self.total_gold_earned,
            "requests_today": self.requests_today,
            "map_regions": {name: {
                "relationship": region.relationship,
                "trade_level": region.trade_level,
                "military_strength": region.military_strength,
                "special_resource": region.special_resource
            } for name, region in self.map_regions.items() if region.region_type == RegionType.KINGDOM},
            "character_relationships": {
                name: {
                    "relationships": char.relationships,
                    "faction_opinions": char.faction_opinions
                } for name, char in self.characters.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data):
        difficulty = Difficulty[data.get("difficulty", "NORMAL")]
        game = cls(difficulty)
        game.kingdom_stats = data.get("kingdom_stats", difficulty.value.copy())
        game.advisor_trust = data.get("advisor_trust", difficulty.value["Trust"])
        game.day_count = data.get("day_count", 0)
        game.season_index = data.get("season_index", 0)
        game.achievements = data.get("achievements", game.achievements)
        game.decision_count = data.get("decision_count", 0)
        game.total_gold_spent = data.get("total_gold_spent", 0)
        game.total_gold_earned = data.get("total_gold_earned", 0)
        game.requests_today = data.get("requests_today", 0)
        
        # Load map regions
        if "map_regions" in data:
            for name, region_data in data["map_regions"].items():
                if name in game.map_regions:
                    game.map_regions[name].relationship = region_data.get("relationship", 50)
                    game.map_regions[name].trade_level = region_data.get("trade_level", 0)
                    game.map_regions[name].military_strength = region_data.get("military_strength", 50)
                    if "special_resource" in region_data:
                        game.map_regions[name].special_resource = region_data["special_resource"]
        
        # Load character relationships
        if "character_relationships" in data:
            for name, char_data in data["character_relationships"].items():
                if name in game.characters:
                    game.characters[name].relationships = char_data.get("relationships", {})
                    game.characters[name].faction_opinions = char_data.get("faction_opinions", {})
        
        # Update diplomatic benefits
        game.update_diplomatic_benefits()
        
        return game

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, surface, font):
        # Draw button with border
        color = [min(255, c + 30) for c in self.color] if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, Config.COLORS["BORDER"], self.rect, 2, border_radius=6)
        
        # Draw text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# -- HELPER FUNCTIONS -----------------------------------------------------------
def load_image_safe(path, use_alpha=True, colorkey=None):
    try:
        img = pygame.image.load(path)
        if use_alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
            if colorkey is not None:
                img.set_colorkey(colorkey)
        return img
    except pygame.error as e:
        print(f"Error loading image: {path} - {e}")
        # Create a placeholder surface with error text
        surf = pygame.Surface((100, 100))
        if use_alpha:
            surf = surf.convert_alpha()
            surf.fill((255, 0, 255, 128))  # Semi-transparent magenta
        else:
            surf.fill((255, 0, 255))  # Magenta
        
        # Add error text
        font = pygame.font.Font(None, 16)
        error_text = font.render("IMG ERR", True, (255, 255, 255))
        text_rect = error_text.get_rect(center=(50, 50))
        surf.blit(error_text, text_rect)
        return surf

def wrap_text(text, font, max_w):
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        test = cur + ' ' + w
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines

def take_screenshot(screen):
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    fn = f"screenshots/screenshot_{ts}.png"
    pygame.image.save(screen, fn)
    print(f"Saved {fn}")

# -- REQUEST DATA ---------------------------------------------------------------
base_requests = [
    {"text": "A villager asks for gold to fix his roof.", 
     "effect": {"Gold": -10, "Happiness": +5, "Trust": +2}},
    {"text": "A merchant offers food for tax relief.",    
     "effect": {"Gold": -5,  "Food": +10,   "Trust": +1}},
    {"text": "A farmer needs seeds for the next harvest.", 
     "effect": {"Gold": -15, "Food": +20,  "Trust": +4}},
    {"text": "A noble requests funds for a new statue.", 
     "effect": {"Gold": -25, "Happiness": +10, "Trust": -2}},
    {"text": "A blacksmith needs a new forge.", 
     "effect": {"Gold": -30, "Happiness": +5, "Trust": +3}},
    {"text": "A traveler requests provisions for a journey.", 
     "effect": {"Food": -15, "Happiness": +5, "Trust": +2}},
    {"text": "A farmer's well has run dry.", 
     "effect": {"Gold": -20, "Food": -5, "Happiness": +5, "Trust": +3}},
    {"text": "A merchant caravan was robbed.", 
     "effect": {"Gold": -15, "Happiness": -5, "Trust": +2}},
    {"text": "A child found a gold coin in the street.", 
     "effect": {"Gold": +5, "Happiness": +5, "Trust": +1}},
    {"text": "A villager offers to sell their family heirloom.", 
     "effect": {"Gold": +15, "Happiness": -5, "Trust": -1}},
]

# Bard requests
bard_requests = [
    {"text": "A bard asks for patronage to compose an epic about your reign.", 
     "effect": {"Gold": -15, "Happiness": +12, "Trust": +3}},
    {"text": "A bard offers to spread tales of your generosity throughout the land.", 
     "effect": {"Gold": -10, "Happiness": +8, "Trust": +5}},
    {"text": "A bard seeks permission to collect stories from your kingdom.", 
     "effect": {"Gold": -5, "Happiness": +10, "Trust": +2}},
    {"text": "A bard requests gold to travel to distant lands and bring back news.", 
     "effect": {"Gold": -20, "Trust": +4}},
    {"text": "A bard offers to perform at the next festival, boosting morale.", 
     "effect": {"Gold": -12, "Happiness": +15}},
]

seasonal_requests = {
    "Spring": [
        {"text": "Plant saplings along the palace avenue.", 
         "effect": {"Gold": -15, "Happiness": +10, "Trust": +5}},
        {"text": "Organize a spring festival for the villagers.",
         "effect": {"Gold": -20, "Happiness": +15, "Trust": +3}},
        {"text": "Repair flood barriers along the river.",
         "effect": {"Gold": -25, "Happiness": +5, "Trust": +4}},
        {"text": "Celebrate the Spring Equinox with a feast.",
         "effect": {"Gold": -30, "Food": -15, "Happiness": +20, "Trust": +6}},
    ],
    "Summer": [
        {"text": "Fund a traveling joust tournament.",    
         "effect": {"Gold": -20, "Happiness": +15, "Trust": +4}},
        {"text": "Build irrigation canals for the fields.",
         "effect": {"Gold": -30, "Food": +25, "Trust": +5}},
        {"text": "Send aid to villages suffering from drought.",
         "effect": {"Gold": -25, "Food": -20, "Happiness": +15, "Trust": +7}},
        {"text": "Host a midsummer celebration.",
         "effect": {"Gold": -15, "Happiness": +20, "Trust": +5}},
    ],
    "Autumn": [
        {"text": "Host a grand harvest festival.",       
         "effect": {"Gold": -25, "Happiness": +20, "Trust": +6}},
        {"text": "Hire extra workers for the harvest.",
         "effect": {"Gold": -15, "Food": +30, "Trust": +4}},
        {"text": "Store extra food for the winter months.",
         "effect": {"Gold": -10, "Food": +15, "Trust": +3}},
        {"text": "Organize a fair to celebrate the harvest.",
         "effect": {"Gold": -20, "Happiness": +15, "Trust": +4}},
    ],
    "Winter": [
        {"text": "Distribute furs to the poor.",         
         "effect": {"Gold": -30, "Happiness": +25, "Trust": +8}},
        {"text": "Repair roads before winter storms.",
         "effect": {"Gold": -20, "Happiness": +10, "Trust": +6}},
        {"text": "Provide extra firewood to the villagers.",
         "effect": {"Gold": -15, "Food": -5, "Happiness": +15, "Trust": +5}},
        {"text": "Organize a winter feast to boost morale.",
         "effect": {"Gold": -25, "Food": -20, "Happiness": +20, "Trust": +7}},
    ],
}

advisor_requests = [
    {"text": "Invest in granaries to store winter harvests.",
     "effect": {"Gold": -15, "Food": +20, "Trust": +2}},
    {"text": "Raise taxes by 5% to swell the treasury.",
     "effect": {"Gold": +20, "Happiness": -10, "Trust": +3}},
    {"text": "Send diplomats to the eastern kingdom.",
     "effect": {"Gold": -10, "Happiness": +5,  "Trust": +4}},
    {"text": "Build a new marketplace to boost trade.",
     "effect": {"Gold": -40, "Happiness": +10, "Trust": +5}},
    {"text": "Hire more guards to protect the kingdom.",
     "effect": {"Gold": -25, "Happiness": +5, "Trust": +6}},
    {"text": "Invest in better farming equipment.",
     "effect": {"Gold": -30, "Food": +25, "Trust": +4}},
    {"text": "Establish a royal library to attract scholars.",
     "effect": {"Gold": -35, "Happiness": +15, "Trust": +5}},
    {"text": "Improve the roads to boost trade.",
     "effect": {"Gold": -20, "Happiness": +10, "Trust": +4}},
]

# -- RANDOM EVENTS --------------------------------------------------------------
random_events = [
    {
        "text": "A dragon attacks the kingdom!",
        "effect": {"Gold": -30, "Happiness": -20, "Food": -15},
        "probability": 0.05,
        "season": None
    },
    {
        "text": "A merchant caravan arrives with rare goods!",
        "effect": {"Gold": +25, "Happiness": +10},
        "probability": 0.08,
        "season": None
    },
    {
        "text": "A plague spreads through the kingdom!",
        "effect": {"Happiness": -30, "Food": -10},
        "probability": 0.03,
        "season": None
    },
    {
        "text": "Bountiful harvest this season!",
        "effect": {"Food": +40, "Happiness": +15},
        "probability": 0.1,
        "season": ["Autumn"]
    },
    {
        "text": "A harsh winter depletes our food stores!",
        "effect": {"Food": -25, "Happiness": -15},
        "probability": 0.07,
        "season": ["Winter"]
    },
    {
        "text": "A band of thieves has been stealing from the treasury!",
        "effect": {"Gold": -20, "Happiness": -10},
        "probability": 0.04,
        "season": None
    },
    {
        "text": "A traveling circus brings joy to the people!",
        "effect": {"Happiness": +20, "Gold": -5},
        "probability": 0.06,
        "season": ["Spring", "Summer"]
    },
]

# -- DIPLOMACY ACTIONS -----------------------------------------------------------
diplomacy_actions = [
    {"text": "Send gifts (Cost: 20 Gold)", "effect": {"Gold": -20, "relationship": 10}},
    {"text": "Establish trade route (Cost: 30 Gold)", "effect": {"Gold": -30, "relationship": 5, "trade": 1}},
    {"text": "Send diplomats (Cost: 15 Gold)", "effect": {"Gold": -15, "relationship": 8}},
    {"text": "Threaten military action", "effect": {"relationship": -15, "military": -5}},
    {"text": "Propose alliance", "effect": {"relationship": 15, "Gold": -25}},
]

# -- GAME INITIALIZATION --------------------------------------------------------
# Set up the display first
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Throne Room Simulator")
clock = pygame.time.Clock()
fullscreen = False

# Create game surfaces
game_surf = pygame.Surface((Config.WIDTH, Config.HEIGHT))
floating_texts = []

# Now load images after display is set up
king_img = load_image_safe("king.png", use_alpha=True)
advisor_img = load_image_safe("advisor.png", use_alpha=False, colorkey=(0, 0, 0))
villager_img = load_image_safe("villager.png", use_alpha=True)
bard_img = load_image_safe("bard.png", use_alpha=True)  # Load bard image
scroll_img = load_image_safe("scroll.png", use_alpha=False, colorkey=(0, 0, 0))
throne_bg = load_image_safe("throne_room.png", use_alpha=False)
map_bg = load_image_safe("kingdom_map.png", use_alpha=False)

# Load fonts with fallbacks - ADJUSTABLE SIZES
try:
    # Try to load a more readable font
    title_font = pygame.font.Font("Cinzel.ttf", Config.TITLE_FONT_SIZE)
    request_font = pygame.font.Font("Cinzel.ttf", Config.REQUEST_FONT_SIZE)
    small_font = pygame.font.Font("Cinzel.ttf", Config.SMALL_FONT_SIZE)
    button_font = pygame.font.Font("Cinzel.ttf", Config.BUTTON_FONT_SIZE)
    info_font = pygame.font.Font("Cinzel.ttf", Config.INFO_FONT_SIZE)
except:
    # Fallback to default fonts
    title_font = pygame.font.Font(None, Config.TITLE_FONT_SIZE)
    request_font = pygame.font.Font(None, Config.REQUEST_FONT_SIZE)
    small_font = pygame.font.Font(None, Config.SMALL_FONT_SIZE)
    button_font = pygame.font.Font(None, Config.BUTTON_FONT_SIZE)
    info_font = pygame.font.Font(None, Config.INFO_FONT_SIZE)

# Load sounds with fallbacks
try:
    accept_sound = pygame.mixer.Sound("accept.wav")
    reject_sound = pygame.mixer.Sound("reject.wav")
    achievement_sound = pygame.mixer.Sound("achievement.wav")
except:
    accept_sound = None
    reject_sound = None
    achievement_sound = None

# Create buttons
btn_accept = Button(Config.WIDTH//2 - 120, 500, 100, 40, "Accept", 
                   Config.COLORS["BUTTON_ACCEPT"], Config.COLORS["TEXT"])
btn_reject = Button(Config.WIDTH//2 + 20, 500, 100, 40, "Reject", 
                   Config.COLORS["BUTTON_REJECT"], Config.COLORS["TEXT"])
btn_next_day = Button(Config.WIDTH//2 - 60, 560, 120, 40, "Next Day", 
                     Config.COLORS["NEXT_DAY"], Config.COLORS["TEXT"])

# Game state
game_state = None
current_scene = Scene.THRONE
selected_character = None

# -- GAME FUNCTIONS ------------------------------------------------------------
def toggle_fullscreen():
    global screen, fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        info = pygame.display.Info()
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))

def get_advisor_comment():
    g, h, f, t = (game_state.kingdom_stats["Gold"], 
                  game_state.kingdom_stats["Happiness"], 
                  game_state.kingdom_stats["Food"], 
                  game_state.advisor_trust)
    
    if t < 20:
        return "My faith wavers, Sire…"
    if g < 20:
        return "Our treasury is nearly empty, Sire!"
    if f < 30:
        return "We must secure more food before winter."
    if h > 80:
        return "The people sing your praises, my liege."
    if h < 30:
        return "The people grow restless, my lord."
    return "All is stable... for now."

def trigger_random_event():
    try:
        for event in random_events:
            if event["season"] is None or game_state.season_names[game_state.season_index] in event["season"]:
                if random.random() < event["probability"]:
                    # Apply event effects
                    for stat, delta in event["effect"].items():
                        if stat == "Trust":
                            game_state.advisor_trust = max(0, min(100, game_state.advisor_trust + delta))
                        else:
                            game_state.kingdom_stats[stat] = max(0, min(100, game_state.kingdom_stats[stat] + delta))
                    
                    # Show floating text
                    floating_texts.append(
                        FloatingText(Config.WIDTH//2, Config.HEIGHT//2, 
                                    f"EVENT: {event['text']}", (255, 255, 0), 120)
                    )
                    return True
    except Exception as e:
        print(f"Error in trigger_random_event: {e}")
    return False

def save_game():
    try:
        with open(Config.SAVE_FILE, 'w') as f:
            json.dump(game_state.to_dict(), f)
        floating_texts.append(
            FloatingText(Config.WIDTH//2, Config.HEIGHT//2, "Game Saved!", (0, 255, 0))
        )
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        floating_texts.append(
            FloatingText(Config.WIDTH//2, Config.HEIGHT//2, "Save Failed!", (255, 0, 0))
        )
        return False

def load_game():
    global game_state
    try:
        with open(Config.SAVE_FILE, 'r') as f:
            data = json.load(f)
        game_state = GameState.from_dict(data)
        floating_texts.append(
            FloatingText(Config.WIDTH//2, Config.HEIGHT//2, "Game Loaded!", (0, 255, 0))
        )
        return True
    except Exception as e:
        print(f"Error loading game: {e}")
        floating_texts.append(
            FloatingText(Config.WIDTH//2, Config.HEIGHT//2, "Load Failed!", (255, 0, 0))
        )
        return False

# -- DRAWING FUNCTIONS ----------------------------------------------------------
def draw_throne_room(surf):
    try:
        # Background + tint
        surf.blit(pygame.transform.scale(throne_bg, (Config.WIDTH, Config.HEIGHT)), (0, 0))
        overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        overlay.fill(Config.COLORS["SEASON_TINT"][game_state.season_names[game_state.season_index]])
        surf.blit(overlay, (0, 0))
        
        # Resource bars with all four in one line
        keys = ["Gold", "Happiness", "Food", "Trust"]
        cols = [Config.COLORS["GOLD"], Config.COLORS["HAPPINESS"], Config.COLORS["FOOD"], Config.COLORS["TRUST"]]
        bw, bh, gx = 140, 25, 20
        total_w = len(keys) * bw + (len(keys) - 1) * gx
        x0, y0 = (Config.WIDTH - total_w) // 2, 20
        
        for i, k in enumerate(keys):
            # Get value (for Trust, use advisor_trust)
            if k == "Trust":
                val = max(0, min(game_state.advisor_trust, 100))
            else:
                val = max(0, min(game_state.kingdom_stats[k], 100))
                
            fill = int(bw * val / 100)
            x = x0 + i * (bw + gx)
            
            # Draw background bar
            pygame.draw.rect(surf, Config.COLORS["BACKGROUND"], (x, y0, bw, bh), border_radius=12)
            pygame.draw.rect(surf, Config.COLORS["BORDER"], (x, y0, bw, bh), 2, border_radius=12)
            
            # Draw fill
            if fill > 0:
                pygame.draw.rect(surf, cols[i], (x+2, y0+2, fill-4, bh-4), border_radius=10)
            
            # Draw text
            txt = small_font.render(f"{k}: {val}", True, Config.COLORS["TEXT"])
            surf.blit(txt, (x + (bw - txt.get_width()) // 2, y0 + (bh - txt.get_height()) // 2))
        
        # Season/day and requests left with better styling
        requests_left = Config.REQUESTS_PER_DAY - game_state.requests_today
        sd_txt = small_font.render(
            f"{game_state.season_names[game_state.season_index]}  Day {(game_state.day_count % Config.SEASON_LENGTH) + 1}/{Config.SEASON_LENGTH}",
            True, Config.COLORS["TEXT"]
        )
        surf.blit(sd_txt, ((Config.WIDTH - sd_txt.get_width()) // 2, y0 + bh + 15))
        
        rl_txt = small_font.render(
            f"Requests left: {requests_left}",
            True, Config.COLORS["HIGHLIGHT"]
        )
        surf.blit(rl_txt, ((Config.WIDTH - rl_txt.get_width()) // 2, y0 + bh + 40))
        
        # Characters at bottom with better spacing
        for name, character in game_state.characters.items():
            character.draw(surf, small_font, selected_character == name)
            
            # Draw decision effects above characters
            if game_state.last_decision_effects:
                y_offset = character.position[1] - 40
                for stat, change in game_state.last_decision_effects.items():
                    color = Config.COLORS["STAT_POSITIVE"] if change > 0 else Config.COLORS["STAT_NEGATIVE"]
                    effect_text = f"{stat}: {change:+d}"
                    effect_surf = small_font.render(effect_text, True, color)
                    surf.blit(effect_surf, (character.position[0] + 50 - effect_surf.get_width()//2, y_offset))
                    y_offset -= 25
        
        # Draw king
        surf.blit(pygame.transform.scale(king_img, (100, 150)), (50, 400))
        
        # Scroll + source icon + title with better styling
        sw, sh = int(Config.WIDTH * 0.75), 300
        sx, sy = (Config.WIDTH - sw) // 2, 50
        surf.blit(pygame.transform.smoothscale(scroll_img, (sw, sh)), (sx, sy))
        
        # Source icon & label
        if game_state.current_request:
            # Determine which icon to use
            if game_state.current_request.source == "Advisor":
                icon = advisor_img
            elif game_state.current_request.source == "Bard":
                icon = bard_img
            else:
                icon = villager_img
                
            surf.blit(pygame.transform.scale(icon, (60, 90)), (sx + 15, sy + 15))
            title = title_font.render(game_state.current_request.source, True, (60, 30, 0))
            surf.blit(title, (sx + 90, sy + 25))
            
            # Letter text with better spacing
            zx, zy, zw, zh = sx + 110, sy + 100, sw - 180, sh - 180
            letter = pygame.Surface((zw, zh), pygame.SRCALPHA)
            lines = wrap_text(game_state.current_request.text, request_font, zw)
            lh = request_font.get_linesize()
            
            # Calculate available space and adjust if needed
            max_lines = (zh - 30) // lh  # Leave space for advisor comment
            if len(lines) > max_lines:
                lines = lines[:max_lines]
            
            for i, line in enumerate(lines):
                txt = request_font.render(line, True, (20, 20, 20))
                letter.blit(txt, (0, i * (lh + 5)))  # Added line spacing
            surf.blit(letter, (zx, zy))
            
            # Advisor comment with better styling
            cy = zy + len(lines) * (lh + 5) + 15  # Increased spacing
            if cy + small_font.get_height() <= zy + zh:
                comment = get_advisor_comment()
                # Wrap comment if too long
                comment_lines = wrap_text(comment, small_font, zw)
                for i, line in enumerate(comment_lines[:2]):  # Max 2 lines for comment
                    if cy + i * (lh + 3) <= zy + zh:
                        comment_txt = small_font.render(line, True, (60, 30, 0))
                        surf.blit(comment_txt, (zx, cy + i * (lh + 3)))
        else:
            # No more requests today
            no_requests = title_font.render("No more requests today", True, (60, 30, 0))
            surf.blit(no_requests, (sx + (sw - no_requests.get_width()) // 2, sy + 150))
        
        # Buttons with better styling
        if game_state.current_request:
            btn_accept.draw(surf, button_font)
            btn_reject.draw(surf, button_font)
        
        # Show Next Day button if all requests for today are processed
        if game_state.requests_today >= Config.REQUESTS_PER_DAY:
            btn_next_day.draw(surf, button_font)
        
        # Request history with better styling
        hx, hy = 20, Config.HEIGHT - 150
        for i, entry in enumerate(game_state.request_history[-3:]):
            y = hy + i * 35
            color = Config.COLORS["STAT_POSITIVE"] if entry["accepted"] else Config.COLORS["STAT_NEGATIVE"]
            status = "Accepted" if entry["accepted"] else "Rejected"
            txt = small_font.render(f"{entry['season']} Day {entry['day']}: {status}", True, color)
            surf.blit(txt, (hx, y))
        
        # Controls hint with better styling
        hint = small_font.render("M: Map | A: Achievements | S: Save | L: Load | F12: Fullscreen", True, (200, 200, 200))
        surf.blit(hint, (20, Config.HEIGHT - 30))
        
        # Diplomatic benefits indicator with better styling
        if any(val > 0 for val in game_state.diplomatic_benefits.values()):
            dip_y = Config.HEIGHT - 60
            dip_txt = small_font.render("Diplomatic Benefits Active", True, Config.COLORS["HIGHLIGHT"])
            surf.blit(dip_txt, (Config.WIDTH - dip_txt.get_width() - 20, dip_y))
    except Exception as e:
        print(f"Error in draw_throne_room: {e}")

def draw_map(surf):
    try:
        # Background with better styling
        surf.blit(pygame.transform.scale(map_bg, (Config.WIDTH, Config.HEIGHT)), (0, 0))
        
        # Draw map regions with better visibility
        for name, region in game_state.map_regions.items():
            selected = (game_state.selected_region == name)
            region.draw(surf, small_font, selected)
        
        # Draw connections between kingdoms with better styling
        connections = [
            ("Player Kingdom", "Northern Kingdom"),
            ("Player Kingdom", "Eastern Kingdom"),
            ("Player Kingdom", "Southern Kingdom"),
        ]
        
        for start, end in connections:
            if start in game_state.map_regions and end in game_state.map_regions:
                start_region = game_state.map_regions[start]
                end_region = game_state.map_regions[end]
                pygame.draw.line(surf, Config.COLORS["HIGHLIGHT"], 
                                start_region.rect.center, 
                                end_region.rect.center, 3)
        
        # Title and instructions with better styling
        title = title_font.render("Kingdom Map", True, Config.COLORS["TEXT"])
        surf.blit(title, (Config.WIDTH//2 - title.get_width()//2, 20))
        
        hint = small_font.render("Click on a kingdom for diplomacy | T: Throne Room", True, (200, 200, 200))
        surf.blit(hint, (Config.WIDTH//2 - hint.get_width()//2, Config.HEIGHT - 30))
        
        # Legend with better styling
        legend_y = 70
        legend_items = [
            ("Your Kingdom", Config.COLORS["PLAYER_KINGDOM"]),
            ("Northern Kingdom", Config.COLORS["NORTHERN_KINGDOM"]),
            ("Eastern Kingdom", Config.COLORS["EASTERN_KINGDOM"]),
            ("Southern Kingdom", Config.COLORS["SOUTHERN_KINGDOM"]),
            ("Villages", Config.COLORS["HOUSE"])
        ]
        
        for name, color in legend_items:
            pygame.draw.rect(surf, color, (20, legend_y, 20, 20), border_radius=4)
            text = small_font.render(name, True, Config.COLORS["TEXT"])
            surf.blit(text, (50, legend_y))
            legend_y += 30
    except Exception as e:
        print(f"Error in draw_map: {e}")

def draw_diplomacy(surf):
    try:
        # Background with better styling
        surf.fill(Config.COLORS["BACKGROUND"])
        
        if not game_state.selected_region:
            return
        
        region = game_state.map_regions[game_state.selected_region]
        
        # Title with better styling
        title = title_font.render(f"Diplomacy: {region.name}", True, Config.COLORS["TEXT"])
        surf.blit(title, (Config.WIDTH//2 - title.get_width()//2, 30))
        
        # Region info panel with better styling
        panel_rect = pygame.Rect(50, 80, Config.WIDTH - 100, 200)
        pygame.draw.rect(surf, Config.COLORS["PANEL_BG"], panel_rect, border_radius=10)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], panel_rect, 2, border_radius=10)
        
        info_y = 90
        info_texts = [
            f"Relationship: {region.relationship}/100",
            f"Trade Level: {region.trade_level}/5",
            f"Military Strength: {region.military_strength}/100",
            f"Special Resource: {region.special_resource}"
        ]
        
        for text in info_texts:
            txt = small_font.render(text, True, Config.COLORS["TEXT"])
            surf.blit(txt, (70, info_y))
            info_y += 35
        
        # Diplomatic benefits info with better styling
        if region.relationship >= 70:
            benefit_text = "Current Benefits: "
            if region.special_resource == "Gold" and region.trade_level > 0:
                benefit_text += f"+{region.trade_level * 2} Gold per day"
            elif region.special_resource == "Food" and region.trade_level > 0:
                benefit_text += f"+{region.trade_level * 3} Food per day"
            elif region.special_resource == "Military" and region.relationship >= 80:
                benefit_text += "+5 Trust per day"
            
            benefit_txt = small_font.render(benefit_text, True, Config.COLORS["STAT_POSITIVE"])
            surf.blit(benefit_txt, (70, info_y))
            info_y += 35
        
        # Character opinions panel with better styling
        opinion_panel_rect = pygame.Rect(50, 300, Config.WIDTH - 100, 150)
        pygame.draw.rect(surf, Config.COLORS["PANEL_BG"], opinion_panel_rect, border_radius=10)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], opinion_panel_rect, 2, border_radius=10)
        
        # Section header
        header = small_font.render("Character Opinions:", True, Config.COLORS["SECTION_HEADER"])
        surf.blit(header, (70, 310))
        
        info_y = 340
        for name, character in game_state.characters.items():
            if region.name in character.faction_opinions:
                opinion = character.faction_opinions[region.name]
                opinion_color = character.get_faction_opinion_color(region.name)
                opinion_text = f"{name}: "
                
                if opinion <= RelationshipLevel.HATE.value:
                    opinion_text += "Hates"
                elif opinion <= RelationshipLevel.DISLIKE.value:
                    opinion_text += "Dislikes"
                elif opinion <= RelationshipLevel.NEUTRAL.value:
                    opinion_text += "Neutral"
                elif opinion <= RelationshipLevel.LIKE.value:
                    opinion_text += "Likes"
                else:
                    opinion_text += "Loves"
                
                txt = small_font.render(opinion_text, True, opinion_color)
                surf.blit(txt, (90, info_y))
                info_y += 30
        
        # Diplomacy actions with better styling
        action_y = 470
        diplomacy_buttons = []  # Store buttons for event handling
        
        for i, action in enumerate(diplomacy_actions):
            # Check if we can afford this action
            can_afford = True
            if "Gold" in action["effect"] and action["effect"]["Gold"] < 0:
                if game_state.kingdom_stats["Gold"] < abs(action["effect"]["Gold"]):
                    can_afford = False
            
            # Create button for each action
            btn = Button(100, action_y + i * 50, 600, 40, action["text"], 
                        Config.COLORS["BUTTON_ACCEPT"] if can_afford else (100, 100, 100),
                        Config.COLORS["TEXT"] if can_afford else (150, 150, 150))
            btn.draw(surf, button_font)
            diplomacy_buttons.append((btn, action))
        
        # Back button with better styling
        back_btn = Button(Config.WIDTH//2 - 60, Config.HEIGHT - 80, 120, 40, "Back", 
                         Config.COLORS["BUTTON_REJECT"], Config.COLORS["TEXT"])
        back_btn.draw(surf, button_font)
        
        # Store buttons for event handling
        return diplomacy_buttons, back_btn
    except Exception as e:
        print(f"Error in draw_diplomacy: {e}")
        return [], None

def draw_character_interaction(surf):
    try:
        # Background with better styling
        surf.fill(Config.COLORS["BACKGROUND"])
        
        if not selected_character:
            return
        
        character = game_state.characters[selected_character]
        
        # Title with better styling
        title = title_font.render(f"Character: {character.name}", True, Config.COLORS["TEXT"])
        surf.blit(title, (Config.WIDTH//2 - title.get_width()//2, 30))
        
        # Character image with border
        img_rect = pygame.Rect(50, 100, 150, 225)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], img_rect, 2, border_radius=8)
        surf.blit(pygame.transform.scale(character.image, (150, 225)), (50, 100))
        
        # Character info panel with better styling
        panel_rect = pygame.Rect(220, 100, Config.WIDTH - 240, 400)
        pygame.draw.rect(surf, Config.COLORS["PANEL_BG"], panel_rect, border_radius=10)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], panel_rect, 2, border_radius=10)
        
        # Character info with better spacing and colors
        info_x = 240
        info_y = 120
        
        # Role with section header
        role_header = info_font.render("Role:", True, Config.COLORS["SECTION_HEADER"])
        surf.blit(role_header, (info_x, info_y))
        role_text = small_font.render(character.role, True, Config.COLORS["TEXT"])
        surf.blit(role_text, (info_x + 60, info_y))
        info_y += 40
        
        # Personality traits with section header
        traits_header = info_font.render("Personality:", True, Config.COLORS["SECTION_HEADER"])
        surf.blit(traits_header, (info_x, info_y))
        info_y += 25
        
        traits_text = ""
        for i, trait in enumerate(character.personality_traits):
            traits_text += trait
            if i < len(character.personality_traits) - 1:
                traits_text += ", "
        
        # Wrap traits if too long
        traits_lines = wrap_text(traits_text, small_font, Config.WIDTH - info_x - 40)
        for line in traits_lines:
            line_text = small_font.render(line, True, Config.COLORS["HIGHLIGHT"])
            surf.blit(line_text, (info_x, info_y))
            info_y += 25
        
        info_y += 20
        
        # Backstory with section header
        backstory_header = info_font.render("Backstory:", True, Config.COLORS["SECTION_HEADER"])
        surf.blit(backstory_header, (info_x, info_y))
        info_y += 25
        
        backstory_lines = wrap_text(character.backstory, small_font, Config.WIDTH - info_x - 40)
        for line in backstory_lines:
            line_text = small_font.render(line, True, Config.COLORS["TEXT"])
            surf.blit(line_text, (info_x, info_y))
            info_y += 25
        
        info_y += 20
        
        # Relationships with section header and color coding
        rel_header = info_font.render("Relationships:", True, Config.COLORS["SECTION_HEADER"])
        surf.blit(rel_header, (info_x, info_y))
        info_y += 25
        
        for name, other_character in game_state.characters.items():
            if name != selected_character:
                rel_level = character.relationships.get(name, RelationshipLevel.NEUTRAL.value)
                rel_color = character.get_relationship_color(name)
                
                if rel_level <= RelationshipLevel.HATE.value:
                    rel_text = f"Hates {name}"
                elif rel_level <= RelationshipLevel.DISLIKE.value:
                    rel_text = f"Dislikes {name}"
                elif rel_level <= RelationshipLevel.NEUTRAL.value:
                    rel_text = f"Neutral toward {name}"
                elif rel_level <= RelationshipLevel.LIKE.value:
                    rel_text = f"Likes {name}"
                else:
                    rel_text = f"Loves {name}"
                
                rel_render = small_font.render(rel_text, True, rel_color)
                surf.blit(rel_render, (info_x, info_y))
                info_y += 30
        
        info_y += 20
        
        # Faction opinions with section header and color coding
        faction_header = info_font.render("Faction Opinions:", True, Config.COLORS["SECTION_HEADER"])
        surf.blit(faction_header, (info_x, info_y))
        info_y += 25
        
        for name, region in game_state.map_regions.items():
            if region.region_type == RegionType.KINGDOM and name in character.faction_opinions:
                opinion_level = character.faction_opinions[name]
                opinion_color = character.get_faction_opinion_color(name)
                
                if opinion_level <= RelationshipLevel.HATE.value:
                    opinion_text = f"Hates {name}"
                elif opinion_level <= RelationshipLevel.DISLIKE.value:
                    opinion_text = f"Dislikes {name}"
                elif opinion_level <= RelationshipLevel.NEUTRAL.value:
                    opinion_text = f"Neutral toward {name}"
                elif opinion_level <= RelationshipLevel.LIKE.value:
                    opinion_text = f"Likes {name}"
                else:
                    opinion_text = f"Loves {name}"
                
                opinion_render = small_font.render(opinion_text, True, opinion_color)
                surf.blit(opinion_render, (info_x, info_y))
                info_y += 30
        
        # Dialogue panel with better styling
        dialogue_panel_rect = pygame.Rect(50, 340, 150, 160)
        pygame.draw.rect(surf, Config.COLORS["PANEL_BG"], dialogue_panel_rect, border_radius=10)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], dialogue_panel_rect, 2, border_radius=10)
        
        # Section header
        dialogue_header = info_font.render("Quotes:", True, Config.COLORS["SECTION_HEADER"])
        surf.blit(dialogue_header, (60, 350))
        
        # Dialogue lines with better spacing
        dialogue_y = 375
        for line in character.dialogue[:3]:  # Show up to 3 dialogue lines
            dialogue_line = wrap_text(line, info_font, 130)
            for wrapped_line in dialogue_line:
                line_render = info_font.render(wrapped_line, True, Config.COLORS["HIGHLIGHT"])
                surf.blit(line_render, (60, dialogue_y))
                dialogue_y += 20
        
        # Back button with better styling
        back_btn = Button(Config.WIDTH//2 - 60, Config.HEIGHT - 80, 120, 40, "Back", 
                         Config.COLORS["BUTTON_REJECT"], Config.COLORS["TEXT"])
        back_btn.draw(surf, button_font)
        
        return back_btn
    except Exception as e:
        print(f"Error in draw_character_interaction: {e}")
        return None

def draw_achievements(surf):
    try:
        # Background with better styling
        surf.fill(Config.COLORS["BACKGROUND"])
        
        # Title with better styling
        title = title_font.render("Achievements", True, Config.COLORS["TEXT"])
        surf.blit(title, (Config.WIDTH//2 - title.get_width()//2, 30))
        
        # Achievement panel with better styling
        panel_rect = pygame.Rect(50, 80, Config.WIDTH - 100, 300)
        pygame.draw.rect(surf, Config.COLORS["PANEL_BG"], panel_rect, border_radius=10)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], panel_rect, 2, border_radius=10)
        
        # Achievement list with better spacing
        y = 100
        for name, unlocked in game_state.achievements.items():
            color = Config.COLORS["SECTION_HEADER"] if unlocked else (100, 100, 100)
            txt = small_font.render(f"{'✓' if unlocked else '✗'} {name}", True, color)
            surf.blit(txt, (80, y))
            y += 35
        
        # Stats panel with better styling
        stats_panel_rect = pygame.Rect(50, 400, Config.WIDTH - 100, 120)
        pygame.draw.rect(surf, Config.COLORS["PANEL_BG"], stats_panel_rect, border_radius=10)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], stats_panel_rect, 2, border_radius=10)
        
        # Stats with better spacing
        y = 420
        stats = [
            f"Decisions Made: {game_state.decision_count}",
            f"Gold Spent: {game_state.total_gold_spent}",
            f"Gold Earned: {game_state.total_gold_earned}",
            f"Days Ruled: {game_state.day_count}"
        ]
        
        for stat in stats:
            txt = small_font.render(stat, True, Config.COLORS["TEXT"])
            surf.blit(txt, (80, y))
            y += 25
        
        # Instructions with better styling
        hint = small_font.render("Press T to return to throne room", True, (200, 200, 200))
        surf.blit(hint, (Config.WIDTH//2 - hint.get_width()//2, Config.HEIGHT - 30))
    except Exception as e:
        print(f"Error in draw_achievements: {e}")

def draw_game_over(surf):
    try:
        # Background with better styling
        surf.fill((0, 0, 0))
        
        if game_state.victory:
            msg = "Victory! Your reign is legendary!"
            color = Config.COLORS["STAT_POSITIVE"]
            submsg = "Your kingdom will prosper for generations!"
        else:
            msg = "Game Over! Your kingdom has fallen."
            color = Config.COLORS["STAT_NEGATIVE"]
            submsg = "Your legacy is forgotten..."
        
        # Main message with better styling
        txt = title_font.render(msg, True, color)
        surf.blit(txt, ((Config.WIDTH - txt.get_width()) // 2, Config.HEIGHT // 2 - 80))
        
        # Submessage with better styling
        subtxt = small_font.render(submsg, True, Config.COLORS["TEXT"])
        surf.blit(subtxt, ((Config.WIDTH - subtxt.get_width()) // 2, Config.HEIGHT // 2 - 30))
        
        # Stats panel with better styling
        stats_panel_rect = pygame.Rect((Config.WIDTH - 300) // 2, Config.HEIGHT // 2 + 20, 300, 250)
        pygame.draw.rect(surf, Config.COLORS["PANEL_BG"], stats_panel_rect, border_radius=10)
        pygame.draw.rect(surf, Config.COLORS["BORDER"], stats_panel_rect, 2, border_radius=10)
        
        # Stats with better spacing
        y = Config.HEIGHT // 2 + 40
        stats = [
            f"Days Ruled: {game_state.day_count}",
            f"Decisions Made: {game_state.decision_count}",
            f"Final Gold: {game_state.kingdom_stats['Gold']}",
            f"Final Happiness: {game_state.kingdom_stats['Happiness']}",
            f"Final Food: {game_state.kingdom_stats['Food']}",
            f"Final Trust: {game_state.advisor_trust}"
        ]
        
        for stat in stats:
            txt = small_font.render(stat, True, Config.COLORS["TEXT"])
            surf.blit(txt, (Config.WIDTH//2 - txt.get_width()//2, y))
            y += 35
        
        # Achievements earned with better styling
        if game_state.achievements_unlocked:
            y += 20
            txt = small_font.render("Achievements Earned:", True, Config.COLORS["SECTION_HEADER"])
            surf.blit(txt, (Config.WIDTH//2 - txt.get_width()//2, y))
            y += 35
            
            for ach in game_state.achievements_unlocked:
                txt = small_font.render(f"✓ {ach}", True, Config.COLORS["SECTION_HEADER"])
                surf.blit(txt, (Config.WIDTH//2 - txt.get_width()//2, y))
                y += 30
        
        # Instructions with better styling
        hint = small_font.render("Press ESC to exit or N for new game", True, (200, 200, 200))
        surf.blit(hint, (Config.WIDTH//2 - hint.get_width()//2, Config.HEIGHT - 50))
    except Exception as e:
        print(f"Error in draw_game_over: {e}")

# -- MAIN MENU ------------------------------------------------------------------
def show_main_menu():
    menu_active = True
    selected_difficulty = Difficulty.NORMAL
    
    while menu_active:
        try:
            # Background with better styling
            game_surf.fill((20, 20, 40))
            
            # Title with better styling
            title = pygame.font.Font(None, 72).render("Throne Room Simulator", True, Config.COLORS["SECTION_HEADER"])
            game_surf.blit(title, (Config.WIDTH//2 - title.get_width()//2, 80))
            
            # Subtitle with better styling
            subtitle = small_font.render("Rule your kingdom with wisdom and justice", True, (200, 200, 200))
            game_surf.blit(subtitle, (Config.WIDTH//2 - subtitle.get_width()//2, 160))
            
            # Difficulty selection panel with better styling
            panel_rect = pygame.Rect((Config.WIDTH - 300) // 2, 220, 300, 200)
            pygame.draw.rect(game_surf, Config.COLORS["PANEL_BG"], panel_rect, border_radius=10)
            pygame.draw.rect(game_surf, Config.COLORS["BORDER"], panel_rect, 2, border_radius=10)
            
            # Difficulty selection with better styling
            diff_text = small_font.render("Select Difficulty:", True, Config.COLORS["TEXT"])
            game_surf.blit(diff_text, (Config.WIDTH//2 - diff_text.get_width()//2, 240))
            
            difficulties = [
                ("Easy", Difficulty.EASY, 290),
                ("Normal", Difficulty.NORMAL, 340),
                ("Hard", Difficulty.HARD, 390)
            ]
            
            for name, diff, y in difficulties:
                color = Config.COLORS["SECTION_HEADER"] if diff == selected_difficulty else (200, 200, 200)
                txt = button_font.render(name, True, color)
                game_surf.blit(txt, (Config.WIDTH//2 - txt.get_width()//2, y))
                
                # Draw selection indicator
                if diff == selected_difficulty:
                    pygame.draw.rect(game_surf, color, 
                                   (Config.WIDTH//2 - txt.get_width()//2 - 10, y - 5, 
                                    txt.get_width() + 20, txt.get_height() + 10), 2, border_radius=5)
            
            # Instructions with better styling
            inst1 = small_font.render("UP/DOWN: Select Difficulty | ENTER: Start Game | L: Load Game", True, (200, 200, 200))
            inst2 = small_font.render("F12: Toggle Fullscreen", True, (200, 200, 200))
            game_surf.blit(inst1, (Config.WIDTH//2 - inst1.get_width()//2, Config.HEIGHT - 80))
            game_surf.blit(inst2, (Config.WIDTH//2 - inst2.get_width()//2, Config.HEIGHT - 50))
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        difficulties_list = list(Difficulty)
                        current_index = difficulties_list.index(selected_difficulty)
                        selected_difficulty = difficulties_list[(current_index - 1) % len(difficulties_list)]
                    elif event.key == pygame.K_DOWN:
                        difficulties_list = list(Difficulty)
                        current_index = difficulties_list.index(selected_difficulty)
                        selected_difficulty = difficulties_list[(current_index + 1) % len(difficulties_list)]
                    elif event.key == pygame.K_RETURN:
                        menu_active = False
                    elif event.key == pygame.K_l:
                        if load_game():
                            menu_active = False
                    elif event.key == pygame.K_F12:
                        toggle_fullscreen()
            
            # Update display
            if fullscreen:
                w, h = screen.get_size()
                screen.blit(pygame.transform.smoothscale(game_surf, (w, h)), (0, 0))
            else:
                screen.blit(game_surf, (0, 0))
            pygame.display.flip()
            clock.tick(Config.FPS)
        except Exception as e:
            print(f"Error in show_main_menu: {e}")
    
    return selected_difficulty

# -- MAIN GAME LOOP -------------------------------------------------------------
def main():
    global game_state, current_scene, floating_texts, selected_character
    
    try:
        # Show main menu
        difficulty = show_main_menu()
        
        # Initialize game state
        game_state = GameState(difficulty)
        game_state.current_request = game_state.choose_request()
        current_scene = Scene.THRONE
        selected_character = None
        
        # Main game loop
        running = True
        while running:
            try:
                game_surf.fill((0, 0, 0))
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    # Handle scene-specific events
                    if current_scene == Scene.THRONE and not game_state.game_over:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_m:
                                current_scene = Scene.MAP
                            elif event.key == pygame.K_a:
                                current_scene = Scene.ACHIEVEMENTS
                            elif event.key == pygame.K_s:
                                save_game()
                            elif event.key == pygame.K_l:
                                load_game()
                            elif event.key == pygame.K_F12:
                                toggle_fullscreen()
                            elif event.key == pygame.K_F2:
                                take_screenshot(screen)
                            elif event.key == pygame.K_n and game_state.requests_today >= Config.REQUESTS_PER_DAY:
                                # Manual day advancement
                                game_state.advance_day()
                                game_state.current_request = game_state.choose_request()
                        
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            # Check if a character was clicked
                            character_clicked = False
                            for name, character in game_state.characters.items():
                                if character.contains_point(event.pos):
                                    selected_character = name
                                    current_scene = Scene.CHARACTER_INTERACTION
                                    character_clicked = True
                                    break
                            
                            if not character_clicked:
                                if btn_accept.handle_event(event) and game_state.current_request:
                                    changes = game_state.process_decision(True)
                                    if accept_sound:
                                        accept_sound.play()
                                    
                                    # Show floating text for changes
                                    for stat, change in changes.items():
                                        color = Config.COLORS["STAT_POSITIVE"] if change > 0 else Config.COLORS["STAT_NEGATIVE"]
                                        floating_texts.append(
                                            FloatingText(Config.WIDTH//2 + 100 + random.randint(-30, 30), 300, 
                                                        f"{stat}: {change:+d}", color)
                                        )
                                
                                elif btn_reject.handle_event(event) and game_state.current_request:
                                    changes = game_state.process_decision(False)
                                    if reject_sound:
                                        reject_sound.play()
                                    
                                    # Show floating text for changes
                                    for stat, change in changes.items():
                                        color = Config.COLORS["STAT_POSITIVE"] if change > 0 else Config.COLORS["STAT_NEGATIVE"]
                                        floating_texts.append(
                                            FloatingText(Config.WIDTH//2 + 100 + random.randint(-30, 30), 300, 
                                                        f"{stat}: {change:+d}", color)
                                        )
                                
                                elif btn_next_day.handle_event(event) and game_state.requests_today >= Config.REQUESTS_PER_DAY:
                                    # Manual day advancement
                                    game_state.advance_day()
                                    game_state.current_request = game_state.choose_request()
                    
                    elif current_scene == Scene.MAP:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_t:
                                current_scene = Scene.THRONE
                            elif event.key == pygame.K_F12:
                                toggle_fullscreen()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            # Check if a region was clicked
                            for name, region in game_state.map_regions.items():
                                # Only kingdoms are clickable for diplomacy
                                if region.region_type == RegionType.KINGDOM and region.contains_point(event.pos):
                                    game_state.selected_region = name
                                    current_scene = Scene.DIPLOMACY
                                    break
                    
                    elif current_scene == Scene.DIPLOMACY:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_t:
                                current_scene = Scene.THRONE
                            elif event.key == pygame.K_ESCAPE:
                                current_scene = Scene.MAP
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            # Draw diplomacy screen to get buttons
                            diplomacy_buttons, back_btn = draw_diplomacy(game_surf)
                            
                            # Check if back button was clicked
                            if back_btn and back_btn.handle_event(event):
                                current_scene = Scene.MAP
                            
                            # Check if a diplomacy action was clicked
                            if game_state.selected_region:
                                region = game_state.map_regions[game_state.selected_region]
                                for btn, action in diplomacy_buttons:
                                    if btn.handle_event(event):
                                        # Check if we can afford this action
                                        can_afford = True
                                        if "Gold" in action["effect"] and action["effect"]["Gold"] < 0:
                                            if game_state.kingdom_stats["Gold"] < abs(action["effect"]["Gold"]):
                                                can_afford = False
                                        
                                        if can_afford:
                                            # Apply action effects
                                            if "Gold" in action["effect"]:
                                                game_state.kingdom_stats["Gold"] += action["effect"]["Gold"]
                                            if "relationship" in action["effect"]:
                                                region.relationship = max(0, min(100, region.relationship + action["effect"]["relationship"]))
                                            if "trade" in action["effect"]:
                                                region.trade_level = max(0, min(5, region.trade_level + action["effect"]["trade"]))
                                            if "military" in action["effect"]:
                                                region.military_strength = max(0, min(100, region.military_strength + action["effect"]["military"]))
                                            
                                            # Update diplomatic benefits
                                            game_state.update_diplomatic_benefits()
                                            
                                            # Show floating text
                                            floating_texts.append(
                                                FloatingText(Config.WIDTH//2, Config.HEIGHT//2, 
                                                            "Diplomatic action taken!", Config.COLORS["STAT_POSITIVE"])
                                            )
                                            
                                            # Check for master diplomat achievement
                                            if all(r.relationship >= 80 for r in game_state.map_regions.values() 
                                                   if r.region_type == RegionType.KINGDOM):
                                                game_state.unlock_achievement("Master Diplomat")
                                        break
                    
                    elif current_scene == Scene.CHARACTER_INTERACTION:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_t:
                                current_scene = Scene.THRONE
                            elif event.key == pygame.K_ESCAPE:
                                current_scene = Scene.THRONE
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            # Draw character interaction screen to get back button
                            back_btn = draw_character_interaction(game_surf)
                            
                            # Check if back button was clicked
                            if back_btn and back_btn.handle_event(event):
                                current_scene = Scene.THRONE
                    
                    elif current_scene == Scene.ACHIEVEMENTS:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_t:
                                current_scene = Scene.THRONE
                            elif event.key == pygame.K_F12:
                                toggle_fullscreen()
                    
                    elif current_scene == Scene.GAME_OVER:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                            elif event.key == pygame.K_n:
                                # Start new game
                                difficulty = show_main_menu()
                                game_state = GameState(difficulty)
                                game_state.current_request = game_state.choose_request()
                                current_scene = Scene.THRONE
                                floating_texts = []
                
                # Update floating texts
                floating_texts = [ft for ft in floating_texts if ft.update()]
                
                # Draw current scene
                if current_scene == Scene.THRONE:
                    draw_throne_room(game_surf)
                    
                    # Draw floating texts
                    for ft in floating_texts:
                        ft.draw(game_surf, small_font)
                    
                    # Check for game over
                    if game_state.game_over:
                        current_scene = Scene.GAME_OVER
                
                elif current_scene == Scene.MAP:
                    draw_map(game_surf)
                
                elif current_scene == Scene.DIPLOMACY:
                    draw_diplomacy(game_surf)
                    
                    # Draw floating texts
                    for ft in floating_texts:
                        ft.draw(game_surf, small_font)
                
                elif current_scene == Scene.CHARACTER_INTERACTION:
                    draw_character_interaction(game_surf)
                    
                    # Draw floating texts
                    for ft in floating_texts:
                        ft.draw(game_surf, small_font)
                
                elif current_scene == Scene.ACHIEVEMENTS:
                    draw_achievements(game_surf)
                
                elif current_scene == Scene.GAME_OVER:
                    draw_game_over(game_surf)
                
                # Update display
                if fullscreen:
                    w, h = screen.get_size()
                    screen.blit(pygame.transform.smoothscale(game_surf, (w, h)), (0, 0))
                else:
                    screen.blit(game_surf, (0, 0))
                pygame.display.flip()
                clock.tick(Config.FPS)
            except Exception as e:
                print(f"Error in game loop: {e}")
                # Continue running despite errors
    except Exception as e:
        print(f"Fatal error in main: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()