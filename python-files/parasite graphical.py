import pygame
import sys
import random
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Parasitic Hivemind")

# Colors
BACKGROUND = (10, 10, 30)
PANEL_BG = (20, 20, 50)
PANEL_BORDER = (50, 100, 150)
TEXT_COLOR = (200, 230, 255)
HIGHLIGHT = (100, 180, 255)
WARNING = (255, 100, 100)
SUCCESS = (100, 255, 150)
CONTINENT_COLORS = {
    "AS": (255, 100, 100),    # Asia - Red
    "AF": (100, 255, 100),    # Africa - Green
    "EU": (100, 100, 255),    # Europe - Blue
    "NA": (255, 200, 50),     # North America - Gold
    "SA": (200, 100, 255),    # South America - Purple
    "OC": (50, 200, 255)      # Oceania - Cyan
}

# Fonts
title_font = pygame.font.SysFont('Arial', 36, bold=True)
header_font = pygame.font.SysFont('Arial', 28, bold=True)
normal_font = pygame.font.SysFont('Arial', 22)
small_font = pygame.font.SysFont('Arial', 18)

class Button:
    def __init__(self, x, y, width, height, text, color=(70, 100, 150), hover_color=(100, 150, 200)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hovered = False
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, 2, border_radius=8)
        
        text_surf = normal_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.hovered else self.color
        return self.hovered
        
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Continent:
    def __init__(self, name, code, population, x, y):
        self.name = name
        self.code = code
        self.population = population
        self.x = x
        self.y = y
        self.infection = 0
        self.passive = 0
        self.animals_infected = False
        self.width = 120
        self.height = 160
        
    def draw(self, surface):
        # Draw continent card
        card_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, PANEL_BG, card_rect, border_radius=10)
        pygame.draw.rect(surface, CONTINENT_COLORS[self.code], card_rect, 2, border_radius=10)
        
        # Continent name
        name_text = header_font.render(self.name, True, CONTINENT_COLORS[self.code])
        surface.blit(name_text, (self.x + self.width//2 - name_text.get_width()//2, self.y + 10))
        
        # Infection level
        infect_text = normal_font.render(f"Infected:{self.infection}/10", True, TEXT_COLOR)
        surface.blit(infect_text, (self.x + 3, self.y + 50))
        
        # Passive infection
        passive_text = small_font.render(f"Passive: +{self.passive}/m", True, TEXT_COLOR)
        surface.blit(passive_text, (self.x + 10, self.y + 80))
        
        # Population
        pop_text = small_font.render(f"Pop: {self.population}M", True, TEXT_COLOR)
        surface.blit(pop_text, (self.x + 10, self.y + 100))
        
        # Animals infected indicator
        animal_text = small_font.render("Animals: " + ("YES" if self.animals_infected else "NO"), 
                                      True, SUCCESS if self.animals_infected else WARNING)
        surface.blit(animal_text, (self.x + 10, self.y + 120))
        
        # Infection progress bar
        pygame.draw.rect(surface, (50, 50, 70), (self.x + 10, self.y + 140, 100, 10), border_radius=5)
        pygame.draw.rect(surface, CONTINENT_COLORS[self.code], (self.x + 10, self.y + 140, self.infection * 10, 10), border_radius=5)

class Game:
    def __init__(self):
        self.state = "INTRO"
        self.cap = 10
        self.volatility = 4
        self.infect = 4
        self.death = 4
        self.dist = 4
        self.complexity = 4
        self.curechance = 0
        self.vaccine = False
        self.vcount = 0
        self.cure = False
        self.ccount = 0
        self.concern = 0
        self.loss = False
        self.win = False
        self.statpoints = 6
        self.month = 0
        self.actions_taken = 0
        self.max_actions = 3
        self.message_log = []
        self.selected_action = None
        self.selected_continent = None
        
        # Create continents
        self.continents = {
            "AS": Continent("Asia", "AS", 4840, 50, 150),
            "AF": Continent("Africa", "AF", 1550, 200, 150),
            "EU": Continent("Europe", "EU", 742, 350, 150),
            "NA": Continent("N.America", "NA", 617, 500, 150),
            "SA": Continent("S.America", "SA", 438, 650, 150),
            "OC": Continent("Oceania", "OC", 46, 800, 150)
        }
        self.continents["NA"].infection = 1  # Start in North America
        
        # Create buttons
        self.action_buttons = [
            Button(50, 520, 200, 50, "Infect Area"),
            Button(260, 520, 200, 50, "Infect Animals"),
            Button(470, 520, 200, 50, "Spread via People"),
            Button(680, 520, 200, 50, "Spread via Goods"),
            Button(50, 580, 200, 50, "Mutate"),
            Button(260, 580, 200, 50, "Evolve"),
            Button(470, 580, 200, 50, "Contaminate")
        ]
        
        self.continent_buttons = [
            Button(50, 350, 120, 40, "Asia", CONTINENT_COLORS["AS"]),
            Button(200, 350, 120, 40, "Africa", CONTINENT_COLORS["AF"]),
            Button(350, 350, 120, 40, "Europe", CONTINENT_COLORS["EU"]),
            Button(500, 350, 120, 40, "N. America", CONTINENT_COLORS["NA"]),
            Button(650, 350, 120, 40, "S. America", CONTINENT_COLORS["SA"]),
            Button(800, 350, 120, 40, "Oceania", CONTINENT_COLORS["OC"])
        ]
        
        self.confirm_button = Button(400, 640, 200, 50, "Confirm Action")
        self.next_month_button = Button(680, 580, 200, 50, "Next Month")
        self.stat_buttons = [
            Button(150, 300, 150, 50, "Complexity"),
            Button(150, 370, 150, 50, "Volatility"),
            Button(150, 440, 150, 50, "Infectiousness"),
            Button(150, 510, 150, 50, "Survivability"),
            Button(150, 580, 150, 50, "Distinguisability")
        ]
        
        self.start_button = Button(400, 620, 200, 50, "Start Game")
        self.restart_button = Button(WIDTH//2 - 100, 640, 200, 50, "Play Again")
        
        # Intro messages
        self.add_message("Welcome to the parasitic hivemind")
        self.add_message("You are a biological weapon designed in an American lab")
        self.add_message("You have broken free after gaining sentience")
        self.add_message("Your goal: infect 100% of the planet")
        self.add_message(f"You have {self.statpoints} stat points to assign")
        
    def add_message(self, message):
        self.message_log.append(message)
        if len(self.message_log) > 10:
            self.message_log.pop(0)
    
    def calculate_global_infection(self):
        total_infection = sum(c.infection for c in self.continents.values())
        max_possible = self.cap * len(self.continents)
        return (total_infection / max_possible) * 100
    
    def update_passive_infections(self):
        for continent in self.continents.values():
            if continent.infection < self.cap:
                continent.infection = min(self.cap, continent.infection + continent.passive)
            continent.infection = max(0, min(self.cap, continent.infection))
    
    def check_win_loss(self):
        total_infection = sum(c.infection for c in self.continents.values())
        max_possible = self.cap * len(self.continents)
        
        if total_infection == max_possible:
            self.win = True
            self.state = "GAME_OVER"
            self.add_message("YOU HAVE INFECTED THE ENTIRE WORLD!")
            self.add_message(f"You won in {self.month} months!")
            return True
        
        if self.ccount > 4 and self.vcount > 4:
            self.loss = True
            self.state = "GAME_OVER"
            self.add_message("Cure and vaccine have been distributed worldwide!")
            self.add_message(f"You lost after {self.month} months!")
            return True
        
        return False
    
    def check_vaccine_cure(self):
        total = sum(c.infection for c in self.continents.values()) * 2
        total = total - self.death - self.dist + (self.concern * 5)
        total = max(0, total)
        
        # Vaccine discovery
        if not self.vaccine:
            vac_chance = random.randint(1, 100)
            vac_chance += (self.complexity * 4) - (self.month * 2)
            if vac_chance <= total:
                self.vaccine = True
                self.add_message("A VACCINE HAS BEEN DISCOVERED!")
        
        # Cure discovery
        if not self.cure:
            cure_chance = random.randint(40, 200)
            cure_chance += (self.complexity * 2) - (self.month * 3)
            if cure_chance <= total:
                self.cure = True
                self.add_message("A CURE HAS BEEN DISCOVERED!")
    
    def distribute_vaccine_cure(self):
        if self.vaccine:
            self.vcount += 1
            if self.vcount == 1:
                self.continents["NA"].passive -= 1
                self.continents["EU"].passive -= 1
                self.add_message("VACCINE DISTRIBUTED TO EUROPE AND NORTH AMERICA")
            elif self.vcount == 2:
                self.continents["OC"].passive -= 1
                self.add_message("VACCINE DISTRIBUTED TO OCEANIA")
            elif self.vcount == 3:
                self.continents["AS"].passive -= 1
                self.add_message("VACCINE DISTRIBUTED TO ASIA")
            elif self.vcount == 4:
                self.continents["SA"].passive -= 1
                self.add_message("VACCINE DISTRIBUTED TO SOUTH AMERICA")
            elif self.vcount == 5:
                self.continents["AF"].passive -= 1
                self.add_message("VACCINE DISTRIBUTED WORLDWIDE")
        
        if self.cure:
            self.ccount += 1
            if self.ccount == 1:
                self.continents["NA"].passive -= 1
                self.continents["EU"].passive -= 1
                self.add_message("CURE DISTRIBUTED TO EUROPE AND NORTH AMERICA")
            elif self.ccount == 2:
                self.continents["OC"].passive -= 1
                self.add_message("CURE DISTRIBUTED TO OCEANIA")
            elif self.ccount == 3:
                self.continents["AS"].passive -= 1
                self.add_message("CURE DISTRIBUTED TO ASIA")
            elif self.ccount == 4:
                self.continents["SA"].passive -= 1
                self.add_message("CURE DISTRIBUTED TO SOUTH AMERICA")
            elif self.ccount == 5:
                self.continents["AF"].passive -= 1
                self.add_message("CURE DISTRIBUTED WORLDWIDE")
    
    def next_month(self):
        self.month += 1
        self.actions_taken = 0
        self.selected_action = None
        self.selected_continent = None
        self.add_message(f"--- MONTH {self.month} ---")
        
        # Update passive infections
        self.update_passive_infections()
        
        # Check for vaccine/cure
        self.check_vaccine_cure()
        
        # Distribute vaccine/cure
        self.distribute_vaccine_cure()
        
        # Check win/loss conditions
        if self.check_win_loss():
            return
        
        self.add_message(f"You have {self.max_actions} actions this month")
    
    def execute_action(self, action, continent_code=None):
        if action == "IN":  # Infect Area
            continent = self.continents[continent_code]
            if continent.infection > 0:  # Must have a foothold
                success = random.randint(1, 10 + (self.vcount + self.ccount) / 2)
                if self.infect > success:
                    continent.infection = min(self.cap, continent.infection + 2)
                    self.add_message(f"Infected {continent.name} successfully! +2 infection")
                else:
                    self.add_message(f"Infection attempt in {continent.name} failed")
            else:
                self.add_message("No foothold in this continent!")
        
        elif action == "IA":  # Infect Animals
            continent = self.continents[continent_code]
            if not continent.animals_infected and continent.infection > 0:
                success = random.randint(1, 16 + (self.vcount + self.ccount) / 2)
                if success < self.infect + continent.infection:
                    continent.passive += 1
                    continent.animals_infected = True
                    self.add_message(f"Animals infected in {continent.name}! +1 passive/month")
                else:
                    self.add_message(f"Animal infection attempt in {continent.name} failed")
            else:
                self.add_message("Cannot infect animals here")
        
        elif action == "SP":  # Spread via People
            continent = self.continents[continent_code]
            success = random.randint(1, 9 + self.vcount + self.ccount)
            if self.infect > success:
                continent.infection = min(self.cap, continent.infection + 1)
                self.add_message(f"Spread via people to {continent.name} successful! +1 infection")
                
                if success > 5:
                    self.concern += 1
                    self.add_message("People are worried! Vaccine efforts increased")
                elif success > 8:
                    self.concern += 2
                    self.add_message("Major concern! Vaccine efforts doubled")
            else:
                self.add_message(f"Spread via people to {continent.name} failed")
        
        elif action == "SG":  # Spread via Goods
            continent = self.continents[continent_code]
            success = random.randint(1, 20)
            if self.infect > success:
                continent.infection = min(self.cap, continent.infection + 1)
                self.add_message(f"Spread via goods to {continent.name} successful! +1 infection")
            else:
                self.add_message(f"Spread via goods to {continent.name} failed")
        
        elif action == "MU":  # Mutate
            success = random.randint(1, 10)
            if self.volatility > success:
                self.concern -= 2.5
                self.add_message("Mutation successful! Cure/vaccine progress slowed")
            else:
                self.concern += 0.5
                self.add_message("Mutation failed! Increased concern")
        
        elif action == "EV":  # Evolve
            success = random.randint(1, 10)
            if self.volatility > success:
                self.infect = min(10, self.infect + 1)
                self.add_message(f"Evolution successful! Infectiousness now {self.infect}")
            else:
                self.add_message("Evolution failed")
        
        elif action == "CO":  # Contaminate
            continent = self.continents[continent_code]
            if continent.infection > 0:  # Must have a foothold
                success = random.randint(1, 8)
                if self.infect > success:
                    continent.infection = min(self.cap, continent.infection + 1)
                    self.add_message(f"Contaminated {continent.name} successfully! +1 infection")
                else:
                    self.add_message(f"Contamination attempt in {continent.name} failed")
            else:
                self.add_message("No foothold in this continent!")
    
    def draw(self, surface):
        surface.fill(BACKGROUND)
        
        # Draw title
        title_text = title_font.render("PARASITIC HIVEMIND", True, HIGHLIGHT)
        surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
        
        if self.state == "INTRO":
            self.draw_intro(surface)
        elif self.state == "STATS":
            self.draw_stats(surface)
        elif self.state in ["ACTION_SELECT", "CONTINENT_SELECT", "ACTION_CONFIRM"]:
            self.draw_game(surface)
        elif self.state == "GAME_OVER":
            self.draw_game_over(surface)
    
    def draw_intro(self, surface):
        # Draw intro text
        intro_lines = [
            "You are a biological weapon designed in an American lab,",
            "You have broken free of containment after gaining sentience. You act as a hivemind with one goal in mind:",
            "to spread throughout every continent and infect every host.",
            "You must infect 100% of the planet.",
            f"You have {self.statpoints} stat points to assign.",
            "ACTIONS:",
            "Each month you have 3 actions which you choose from a list of:",
            "Infect area, Infect animals, Spread via goods, Spread via people, Mutate, Evolve, Contanimate",
            "Infect Area: Requires at least one infection point and raises infection level by 2.",
            "Contanimate easier than Infect area and also requires at least one infection point but only raises infection level by 1",
            "Spread via goods - spreads to a new continent, low risk but low chance",
            "Spread via people, spread to a new continent high risk high chance",
            "Mutate, Slows cure and vaccine progress",
            "Evolve, increase infectiousness does not go past 10"
        ]
        
        for i, line in enumerate(intro_lines):
            text = normal_font.render(line, True, TEXT_COLOR)
            surface.blit(text, (WIDTH//2 - text.get_width()//2, 60 + i*40))
        
        # Draw start button
        self.start_button.draw(surface)
    
    def draw_stats(self, surface):
        # Draw title
        stats_title = header_font.render("ASSIGN STAT POINTS", True, HIGHLIGHT)
        surface.blit(stats_title, (WIDTH//2 - stats_title.get_width()//2, 50))
        
        # Draw stat explanations
        explanations = [
            "Complexity: Affects cure/vaccine progress,",
            "Volatility: Affects mutation difficulty",
            "Infectiousness: Affects infection success",
            "Survivability: Affects host survival (higher deaths = faster cure)",
            "Distinguisability: Affects case misattribution"
            
        ]
        
        for i, text in enumerate(explanations):
            rendered = normal_font.render(text, True, TEXT_COLOR)
            surface.blit(rendered, (400, 150 + i*40))
        
        # Draw current stats
        stats_text = [
            f"Complexity: {self.complexity}",
            f"Volatility: {self.volatility}",
            f"Infectiousness: {self.infect}",
            f"Survivability: {self.death}",
            f"Distinguisability: {self.dist}"
            
        ]
        
        for i, text in enumerate(stats_text):
            rendered = normal_font.render(text, True, HIGHLIGHT)
            surface.blit(rendered, (150, 80 + i*40))
        
        # Draw stat buttons
        for button in self.stat_buttons:
            button.draw(surface)
        
        # Draw points remaining
        points_text = normal_font.render(f"Points remaining: {self.statpoints}", True, SUCCESS if self.statpoints > 0 else WARNING)
        surface.blit(points_text, (151, 640))
        
        # Draw start button if no points left
        if self.statpoints == 0:
            self.start_button.draw(surface)
    
    def draw_game(self, surface):
        # Draw month and global infection
        month_text = header_font.render(f"MONTH: {self.month}", True, HIGHLIGHT)
        surface.blit(month_text, (50, 80))
        
        infection_percent = self.calculate_global_infection()
        infection_text = header_font.render(f"Global Infection: {infection_percent:.1f}%", True, 
                                          SUCCESS if infection_percent > 50 else WARNING)
        surface.blit(infection_text, (WIDTH - infection_text.get_width() - 50, 80))
        
        # Draw stats
        stats_text = [
            f"Volatility: {self.volatility}",
            f"Infectiousness: {self.infect}",
            f"Survivability: {self.death}",
            f"Distinguisability: {self.dist}",
            f"Complexity: {self.complexity}"
        ]
        
        for i, text in enumerate(stats_text):
            rendered = small_font.render(text, True, TEXT_COLOR)
            surface.blit(rendered, (WIDTH - 200, 150 + i*30))
        
        # Draw cure/vaccine status
        if self.vaccine:
            vax_text = small_font.render(f"Vaccine was created {self.vcount} months ago", True, WARNING)
            surface.blit(vax_text, (WIDTH - 300, 30))
        
        if self.cure:
            cure_text = small_font.render(f"Cure was created {self.ccount} months ago", True, WARNING)
            surface.blit(cure_text, (WIDTH - 300, 50))
        
        # Draw continents
        for continent in self.continents.values():
            continent.draw(surface)
        
        # Draw action buttons
        for button in self.action_buttons:
            button.draw(surface)
        
        # Draw continent selection if needed
        if self.state == "CONTINENT_SELECT":
            select_text = header_font.render("SELECT CONTINENT", True, HIGHLIGHT)
            surface.blit(select_text, (WIDTH//2 - select_text.get_width()//2, 320))
            
            for button in self.continent_buttons:
                button.draw(surface)
        
        # Draw confirm button if needed
        if self.state == "ACTION_CONFIRM":
            action_text = normal_font.render(f"Action: {self.selected_action}", True, HIGHLIGHT)
            surface.blit(action_text, (50, 450))
            
            if self.selected_continent:
                continent_name = self.continents[self.selected_continent].name
                continent_text = normal_font.render(f"Continent: {continent_name}", True, CONTINENT_COLORS[self.selected_continent])
                surface.blit(continent_text, (50, 490))
            
            self.confirm_button.draw(surface)
        
        # Draw next month button
        if self.actions_taken >= self.max_actions:
            self.next_month_button.draw(surface)
        
        # Draw actions taken
        actions_text = header_font.render(f"Actions: {self.actions_taken}/{self.max_actions}", True, HIGHLIGHT)
        surface.blit(actions_text, (50, 30))
        
        # Draw message log
        pygame.draw.rect(surface, PANEL_BG, (50, 400, 900, 90), border_radius=10)
        pygame.draw.rect(surface, PANEL_BORDER, (50, 400, 900, 90), 2, border_radius=10)
        
        for i, message in enumerate(self.message_log[-2:]):
            msg_text = small_font.render(message, True, TEXT_COLOR)
            surface.blit(msg_text, (60, 410 + i*30))
    
    def draw_game_over(self, surface):
        if self.win:
            title = "VICTORY! WORLD DOMINATION ACHIEVED"
            color = SUCCESS
            message = f"You infected the entire planet in {self.month} months!"
        else:
            title = "DEFEAT! THE CURE PREVAILED"
            color = WARNING
            message = f"You were defeated after {self.month} months of infection."
        
        title_text = title_font.render(title, True, color)
        surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 150))
        
        message_text = header_font.render(message, True, TEXT_COLOR)
        surface.blit(message_text, (WIDTH//2 - message_text.get_width()//2, 250))
        
        # Draw final stats
        stats = [
            f"Months: {self.month}",
            f"Global Infection: {self.calculate_global_infection():.1f}%",
            f"Volatility: {self.volatility}",
            f"Infectiousness: {self.infect}",
            f"Survivability: {self.death}",
            f"Distinguisability: {self.dist}",
            f"Complexity: {self.complexity}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = normal_font.render(stat, True, TEXT_COLOR)
            surface.blit(stat_text, (WIDTH//2 - stat_text.get_width()//2, 350 + i*40))
        
        # Draw restart button
        
        self.restart_button.draw(surface)

        # Check for hover (optional, if your Button class uses it)
        #restart_button.check_hover(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
                # Get position RIGHT before checking click
                
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.state == "INTRO":
            self.start_button.check_hover(mouse_pos)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.start_button.rect.collidepoint(mouse_pos):
                    self.state = "STATS"
        elif self.state == "GAME_OVER":
            self.restart_button.check_hover(mouse_pos)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.restart_button.rect.collidepoint(mouse_pos):
                        self.__init__()  # Reset game
        elif self.state == "STATS":
            for button in self.stat_buttons:
                button.check_hover(mouse_pos)
                if self.statpoints > 0 and button.is_clicked(mouse_pos, event):
                    if button.text.startswith("Complexity"):
                        self.complexity += 1
                    elif button.text.startswith("Volatility"):
                        self.volatility += 1
                    elif button.text.startswith("Infectiousness"):
                        self.infect += 1
                    elif button.text.startswith("Survivability"):
                        self.death += 1
                    elif button.text.startswith("Distinguisability"):
                        self.dist += 1
                    self.statpoints -= 1
            
            if self.statpoints == 0:
                self.start_button.check_hover(mouse_pos)
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.start_button.rect.collidepoint(mouse_pos):
                        self.state = "ACTION_SELECT"
                        self.add_message("Game starting...")
                        self.add_message(f"You have {self.max_actions} actions per month")
                        self.add_message("Select an action to begin")
        
        elif self.state == "ACTION_SELECT" and self.actions_taken < self.max_actions:
            for i, button in enumerate(self.action_buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, event):
                    actions = ["IN", "IA", "SP", "SG", "MU", "EV", "CO"]
                    self.selected_action = actions[i]
                    
                    if self.selected_action in ["IN", "IA", "SP", "SG", "CO"]:
                        self.state = "CONTINENT_SELECT"
                    else:
                        self.state = "ACTION_CONFIRM"
        
        elif self.state == "CONTINENT_SELECT":
            for i, button in enumerate(self.continent_buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, event):
                    continents = ["AS", "AF", "EU", "NA", "SA", "OC"]
                    self.selected_continent = continents[i]
                    self.state = "ACTION_CONFIRM"
        
        elif self.state == "ACTION_CONFIRM":
            self.confirm_button.check_hover(mouse_pos)
            if self.confirm_button.is_clicked(mouse_pos, event):
                self.execute_action(self.selected_action, self.selected_continent)
                self.actions_taken += 1
                self.selected_action = None
                self.selected_continent = None
                self.state = "ACTION_SELECT"
                
                # Check if game over after action
                self.check_win_loss()
        
        if self.actions_taken >= self.max_actions:
            self.next_month_button.check_hover(mouse_pos)
            if self.next_month_button.is_clicked(mouse_pos, event):
                self.next_month()

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            game.handle_event(event)
        
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
