import datetime
import json
from copy import deepcopy
import os
import glob # For listing save files
import calendar # For displaying the calendar

# --- ANSI Color Codes ---
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    # Text Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    # Bright Text Colors
    BRIGHT_BLACK = '\033[90m' # Often Gray
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    # Background Colors (Use sparingly for readability)
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Semantic Colors
    HEADER = BOLD + BRIGHT_MAGENTA
    SUBHEADER = BOLD + MAGENTA
    PROMPT = BRIGHT_BLUE
    INPUT_FIELD = BRIGHT_WHITE # Color for the text user will input against
    SUCCESS = BRIGHT_GREEN
    ERROR = BRIGHT_RED
    WARNING = BRIGHT_YELLOW
    INFO = BRIGHT_CYAN
    DATE_HIGHLIGHT = BOLD + YELLOW
    FIN_POSITIVE = GREEN
    FIN_NEGATIVE = RED
    OPTION = BRIGHT_WHITE # For menu option numbers/letters
    OPTION_TEXT = WHITE
    CALENDAR_DAY = WHITE
    CALENDAR_CURRENT_DAY = BOLD + BG_BLUE + BRIGHT_WHITE 
    CALENDAR_EVENT_S = BRIGHT_GREEN # Start
    CALENDAR_EVENT_P = GREEN # Payout
    CALENDAR_EVENT_L = BRIGHT_YELLOW # Last Payout
    CALENDAR_EVENT_C = BRIGHT_BLUE # Cost Return


# --- GLOBAL CONSTANTS ---
FORECAST_DEADLINE = datetime.date(2025, 10, 3)
SAVE_GAME_EXTENSION = ".json"
PROGRAM_CONFIG_FILENAME = "program_config.json" # Unified config file
DEFAULT_SAVES_DIR_NAME = "mining_tracker_saves" # Default relative save directory name
DAILY_CONTRACT_NAME = "Daily Contract" 
RECOMMENDATION_SCAN_DAYS = 14 
MAX_ROLLBACK_HISTORY_DAYS = 30 

class MiningContract:
    def __init__(self, name, cost, duration_days, total_net_profit, start_date=None, contract_id=None):
        self.name = name
        self.cost = float(cost)
        self.duration_days = int(duration_days)
        self.total_net_profit = float(total_net_profit)
        self.start_date = start_date 
        self.id = contract_id if contract_id else f"{name.replace(' ', '_')}_{datetime.datetime.now().timestamp()}"

    @property
    def daily_net_profit_payout(self):
        if self.duration_days == 0: return 0
        return self.total_net_profit / self.duration_days

    @property
    def contract_total_gross_return(self):
        return self.cost + self.total_net_profit

    def get_payout_on_date(self, current_date):
        if not self.start_date or self.duration_days <= 0:
            return 0.0
        days_since_start = (current_date - self.start_date).days
        if 1 <= days_since_start <= self.duration_days:
            return self.daily_net_profit_payout
        return 0.0

    def is_operationally_active_for_payout(self, current_date):
        if not self.start_date or self.duration_days <= 0:
            return False
        days_since_start = (current_date - self.start_date).days
        return 1 <= days_since_start <= self.duration_days

    def get_last_payout_day(self):
        if not self.start_date or self.duration_days <= 0: return None
        return self.start_date + datetime.timedelta(days=self.duration_days)

    def get_cost_return_day(self):
        if not self.start_date or self.duration_days <= 0: return None
        last_payout_day = self.get_last_payout_day()
        return last_payout_day + datetime.timedelta(days=1) if last_payout_day else None

    def to_dict(self):
        return {'name': self.name, 'cost': self.cost, 'duration_days': self.duration_days,
                'total_net_profit': self.total_net_profit,
                'start_date': self.start_date.isoformat() if self.start_date else None, 'id': self.id}

    @classmethod
    def from_dict(cls, data):
        start_date = datetime.date.fromisoformat(data['start_date']) if data['start_date'] else None
        return cls(name=data['name'], cost=data['cost'], duration_days=data['duration_days'],
                   total_net_profit=data['total_net_profit'], start_date=start_date, contract_id=data['id'])

    def __str__(self): 
        start_str = self.start_date.strftime('%Y-%m-%d') if self.start_date else "N/A"
        last_payout_str = self.get_last_payout_day().strftime('%Y-%m-%d') if self.get_last_payout_day() else "N/A"
        cost_return_str = self.get_cost_return_day().strftime('%Y-%m-%d') if self.get_cost_return_day() else "N/A"
        return (f"ID: {Colors.BRIGHT_BLACK}{self.id}{Colors.RESET}, Name: {Colors.BOLD}{self.name}{Colors.RESET}, Cost: {Colors.FIN_NEGATIVE}${self.cost:,.2f}{Colors.RESET}, Dur: {self.duration_days}d, "
                f"Net Profit: {Colors.FIN_POSITIVE}${self.total_net_profit:,.2f}{Colors.RESET}, Daily Net Payout: {Colors.FIN_POSITIVE}${self.daily_net_profit_payout:,.2f}{Colors.RESET}\n"
                f"  Starts: {Colors.DATE_HIGHLIGHT}{start_str}{Colors.RESET}, Last Payout Day: {Colors.DATE_HIGHLIGHT}{last_payout_str}{Colors.RESET}, Cost Returns: {Colors.DATE_HIGHLIGHT}{cost_return_str}{Colors.RESET}")

# --- HELPER & UTILITY FUNCTIONS ---
def get_validated_input(prompt, target_type=str, default=None, allow_empty_for_default=True):
    while True:
        try:
            user_input_str = input(f"{Colors.PROMPT}{prompt}{Colors.RESET}{Colors.INPUT_FIELD}").strip()
            print(Colors.RESET, end="") 
            if allow_empty_for_default and not user_input_str and default is not None:
                if target_type == datetime.date and isinstance(default, str):
                    return datetime.datetime.strptime(default, '%Y-%m-%d').date()
                return default
            if target_type == float: return float(user_input_str)
            if target_type == int: return int(user_input_str)
            if target_type == datetime.date: return datetime.datetime.strptime(user_input_str, '%Y-%m-%d').date()
            return user_input_str
        except ValueError:
            err_msg = f"Invalid input. Please enter a valid {target_type.__name__}"
            if target_type == datetime.date: err_msg += " (YYYY-MM-DD)"
            print(f"  {Colors.ERROR}❌ {err_msg}{Colors.RESET}")
        except Exception as e: print(f"  {Colors.ERROR}An unexpected error: {e}{Colors.RESET}")

def create_default_contract_templates_data(): 
    return [
        {'name': DAILY_CONTRACT_NAME, 'cost': 12, 'duration_days': 1, 'total_net_profit': 0.6},
        {'name': "$500 Contract", 'cost': 500, 'duration_days': 5, 'total_net_profit': 31.5},
        {'name': "$1200 Contract", 'cost': 1200, 'duration_days': 14, 'total_net_profit': 225.12},
        {'name': "$3200 Contract", 'cost': 3200, 'duration_days': 21, 'total_net_profit': 974.4},
        {'name': "$8200 Contract", 'cost': 8200, 'duration_days': 40, 'total_net_profit': 5379.2},
        {'name': "$10100 Contract", 'cost': 10100, 'duration_days': 45, 'total_net_profit': 7757.1},
    ]

def get_script_directory():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError: 
        return os.getcwd()

def get_all_known_contracts(current_game_settings, active_contracts_list, purchase_history_list):
    all_contracts_dict = {} 
    for c_obj in active_contracts_list: all_contracts_dict[c_obj.id] = c_obj
    if current_game_settings and 'held_contracts' in current_game_settings:
        for c_obj in current_game_settings['held_contracts']:
            if c_obj.id not in all_contracts_dict: all_contracts_dict[c_obj.id] = c_obj
    if current_game_settings and purchase_history_list:
        for item in purchase_history_list:
            if item['type'] == 'Purchased' and item['id'] not in all_contracts_dict:
                template_found = next((t for t in current_game_settings['contract_templates'] 
                                       if t.name == item['name'] and t.cost == item['cost']), None)
                if template_found:
                    hist_start_date = datetime.date.fromisoformat(item['date'])
                    reconstructed_c = MiningContract(name=template_found.name, cost=template_found.cost,
                                                     duration_days=template_found.duration_days,
                                                     total_net_profit=template_found.total_net_profit,
                                                     start_date=hist_start_date, contract_id=item['id'])
                    all_contracts_dict[reconstructed_c.id] = reconstructed_c
    return list(all_contracts_dict.values())

# --- PROGRAM CONFIGURATION ---
def load_program_config():
    script_dir = get_script_directory()
    config_filepath = os.path.join(script_dir, PROGRAM_CONFIG_FILENAME)
    
    default_relative_save_dir = DEFAULT_SAVES_DIR_NAME
    absolute_default_save_path = os.path.join(script_dir, default_relative_save_dir)

    default_game_setup_data = {
        "contract_templates_data": create_default_contract_templates_data(), 
        "initial_profit": 100.0,
        "start_date_str": datetime.date.today().isoformat(),
        "held_contracts_data": [], 
        "auto_purchase_forecast": False
    }
    
    prog_config = {
        'default_save_folder_path': default_relative_save_dir, 
        'default_game_setup': default_game_setup_data
    }

    if os.path.exists(config_filepath):
        try:
            with open(config_filepath, 'r') as f:
                loaded_prog_config = json.load(f)
            
            prog_config['default_save_folder_path'] = loaded_prog_config.get('default_save_folder_path', default_relative_save_dir)
            
            loaded_game_setup = loaded_prog_config.get('default_game_setup', {})
            for key, val in default_game_setup_data.items():
                prog_config['default_game_setup'][key] = loaded_game_setup.get(key, val)

        except (json.JSONDecodeError, IOError) as e:
            print(f"{Colors.WARNING}Warning: '{PROGRAM_CONFIG_FILENAME}' is corrupted or unreadable ({e}). Using defaults and attempting to recreate.{Colors.RESET}")
    else:
        print(f"{Colors.INFO}'{PROGRAM_CONFIG_FILENAME}' not found. Creating with default configuration.{Colors.RESET}")
    
    resolved_save_path_from_config = prog_config['default_save_folder_path']
    if not os.path.isabs(resolved_save_path_from_config):
        resolved_save_path_from_config = os.path.join(script_dir, resolved_save_path_from_config)
    
    if not os.path.isdir(resolved_save_path_from_config):
        print(f"{Colors.WARNING}Configured save path '{prog_config['default_save_folder_path']}' (resolved to '{resolved_save_path_from_config}') is invalid.{Colors.RESET}")
        potential_existing_default_dir = os.path.join(script_dir, DEFAULT_SAVES_DIR_NAME)
        if os.path.isdir(potential_existing_default_dir):
            print(f"{Colors.INFO}Found existing '{DEFAULT_SAVES_DIR_NAME}' folder. Setting as default save location.{Colors.RESET}")
            prog_config['default_save_folder_path'] = DEFAULT_SAVES_DIR_NAME 
            resolved_save_path_from_config = potential_existing_default_dir
        else:
            print(f"{Colors.INFO}Creating default save directory: '{absolute_default_save_path}'{Colors.RESET}")
            prog_config['default_save_folder_path'] = DEFAULT_SAVES_DIR_NAME 
            resolved_save_path_from_config = absolute_default_save_path
    
    try:
        os.makedirs(resolved_save_path_from_config, exist_ok=True)
        if os.path.normpath(resolved_save_path_from_config) == os.path.normpath(absolute_default_save_path):
            prog_config['default_save_folder_path'] = DEFAULT_SAVES_DIR_NAME
    except OSError as e:
        print(f"{Colors.ERROR}FATAL: Could not create or access save directory '{resolved_save_path_from_config}': {e}. Please check permissions or manually create it.{Colors.RESET}")
        
    save_program_config(prog_config) 
    return prog_config


def save_program_config(prog_config_dict):
    script_dir = get_script_directory()
    config_filepath = os.path.join(script_dir, PROGRAM_CONFIG_FILENAME)
    try:
        if 'default_game_setup' in prog_config_dict:
            dgs = prog_config_dict['default_game_setup']
            if 'start_date_str' in dgs and isinstance(dgs.get('start_date'), datetime.date): 
                 dgs['start_date_str'] = dgs['start_date'].isoformat()
            if 'contract_templates' in dgs and isinstance(dgs['contract_templates'], list) and \
               all(isinstance(item, MiningContract) for item in dgs['contract_templates']):
                dgs['contract_templates_data'] = [t.to_dict() for t in dgs['contract_templates']]
            if 'held_contracts' in dgs and isinstance(dgs['held_contracts'], list) and \
               all(isinstance(item, MiningContract) for item in dgs['held_contracts']):
                dgs['held_contracts_data'] = [hc.to_dict() for hc in dgs['held_contracts']]

        with open(config_filepath, 'w') as f:
            json.dump(prog_config_dict, f, indent=4)
        print(f"  {Colors.SUCCESS}Program configuration saved to '{config_filepath}'.{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.ERROR}❌ Error saving program configuration: {e}{Colors.RESET}")


def manage_program_overall_settings(prog_config):
    while True:
        print(f"\n{Colors.HEADER}--- Program Configuration ---{Colors.RESET}")
        print(f"{Colors.OPTION}[1]{Colors.OPTION_TEXT} Edit Default Game Setup Values (for New Games){Colors.RESET}")
        current_save_display_path = prog_config.get('default_save_folder_path', DEFAULT_SAVES_DIR_NAME)
        print(f"{Colors.OPTION}[2]{Colors.OPTION_TEXT} Edit Default Save Folder Path (Currently: {Colors.INFO}{current_save_display_path}{Colors.RESET}{Colors.OPTION_TEXT}){Colors.RESET}")
        print(f"{Colors.OPTION}[b]{Colors.OPTION_TEXT} Back to Main Menu{Colors.RESET}")
        choice = input(f"{Colors.PROMPT}Choice: {Colors.RESET}{Colors.INPUT_FIELD}").lower()
        print(Colors.RESET, end="")

        if choice == '1':
            print(f"\n{Colors.SUBHEADER}--- Editing Default Game Setup Values ---{Colors.RESET}")
            default_game_setup_obj = {
                "contract_templates": [MiningContract(**data) for data in prog_config['default_game_setup']['contract_templates_data']],
                "initial_profit": prog_config['default_game_setup']['initial_profit'],
                "start_date": datetime.date.fromisoformat(prog_config['default_game_setup']['start_date_str']),
                "held_contracts": [MiningContract(**data) for data in prog_config['default_game_setup']['held_contracts_data']],
                "auto_purchase_forecast": prog_config['default_game_setup']['auto_purchase_forecast']
            }
            updated_defaults_obj = manage_game_settings(default_game_setup_obj, is_initial_setup=True, context_info="Editing Program Defaults for New Games")
            if updated_defaults_obj: 
                prog_config['default_game_setup'] = {
                    "contract_templates_data": [t.to_dict() for t in updated_defaults_obj['contract_templates']],
                    "initial_profit": updated_defaults_obj['initial_profit'],
                    "start_date_str": updated_defaults_obj['start_date'].isoformat(),
                    "held_contracts_data": [hc.to_dict() for hc in updated_defaults_obj['held_contracts']],
                    "auto_purchase_forecast": updated_defaults_obj['auto_purchase_forecast']
                }
                save_program_config(prog_config) 
        elif choice == '2':
            current_path_display = prog_config.get('default_save_folder_path', DEFAULT_SAVES_DIR_NAME)
            new_path_input = get_validated_input(f"Enter new default save folder path (current: {current_path_display}): ", str, current_path_display)
            
            if os.path.isabs(new_path_input):
                resolved_new_path = os.path.normpath(new_path_input)
                path_to_store = resolved_new_path 
            else: 
                resolved_new_path = os.path.normpath(os.path.join(get_script_directory(), new_path_input))
                path_to_store = new_path_input 

            print(f"  {Colors.INFO}Path will be resolved to: {resolved_new_path}{Colors.RESET}")

            if os.path.isdir(resolved_new_path) or input(f"{Colors.WARNING}Path '{resolved_new_path}' doesn't exist or is not a directory. Create it? (y/n): {Colors.RESET}{Colors.INPUT_FIELD}").lower() == 'y':
                print(Colors.RESET, end="")
                try:
                    os.makedirs(resolved_new_path, exist_ok=True)
                    prog_config['default_save_folder_path'] = path_to_store 
                    save_program_config(prog_config)
                    print(f"  {Colors.SUCCESS}✅ Default save folder path updated to: '{path_to_store}' (resolves to '{resolved_new_path}'){Colors.RESET}")
                except Exception as e:
                    print(f"  {Colors.ERROR}❌ Error setting path: {e}{Colors.RESET}")
            else:
                print(f"  {Colors.INFO}Path not changed.{Colors.RESET}")
        elif choice == 'b':
            break
        else:
            print(f"  {Colors.ERROR}Invalid choice.{Colors.RESET}")

# --- GAME SETTINGS (For a specific simulation instance) ---
def manage_game_settings(current_game_settings_obj, is_initial_setup=True, context_info="Game Settings"):
    settings_copy = deepcopy(current_game_settings_obj) 

    while True:
        print("\n" + "="*60)
        title = context_info
        print(f"{Colors.HEADER}⚙️ {title} ⚙️{Colors.RESET}")
        print("="*60)
        
        print(f"{Colors.OPTION}[1]{Colors.OPTION_TEXT} Adjust Contract Template Values ({len(settings_copy['contract_templates'])} types){Colors.RESET}")
        if is_initial_setup: 
            print(f"{Colors.OPTION}[2]{Colors.OPTION_TEXT} Set Initial Available Profit (Currently: {Colors.FIN_POSITIVE}${settings_copy['initial_profit']:,.2f}{Colors.RESET}{Colors.OPTION_TEXT}){Colors.RESET}")
            print(f"{Colors.OPTION}[3]{Colors.OPTION_TEXT} Set Simulation Start Date (Currently: {Colors.DATE_HIGHLIGHT}{settings_copy['start_date'].strftime('%Y-%m-%d')}{Colors.RESET}{Colors.OPTION_TEXT}){Colors.RESET}")
            print(f"{Colors.OPTION}[4]{Colors.OPTION_TEXT} Add/View/Remove Pre-existing Held Contracts ({len(settings_copy['held_contracts'])} held){Colors.RESET}")
        print(f"{Colors.OPTION}[5]{Colors.OPTION_TEXT} Toggle Auto-Purchase Forecast (Currently: {Colors.INFO}{'ON' if settings_copy['auto_purchase_forecast'] else 'OFF'}{Colors.RESET}{Colors.OPTION_TEXT}){Colors.RESET}")
        if is_initial_setup:
             print(f"{Colors.OPTION}[v]{Colors.OPTION_TEXT} View Current Configuration Summary{Colors.RESET}")
        print(f"\n{Colors.OPTION}[s]{Colors.OPTION_TEXT} SAVE and APPLY settings and return{Colors.RESET}")
        print(f"{Colors.OPTION}[c]{Colors.OPTION_TEXT} CANCEL changes and return{Colors.RESET}")
        print("="*60)
        choice = input(f"{Colors.PROMPT}Enter your choice: {Colors.RESET}{Colors.INPUT_FIELD}").lower().strip()
        print(Colors.RESET, end="")


        if choice == '1':
            print(f"\n{Colors.SUBHEADER}--- Adjust Contract Templates ---{Colors.RESET}")
            for i, t in enumerate(settings_copy['contract_templates']):
                print(f"{Colors.OPTION}[{i+1}]{Colors.OPTION_TEXT} {t.name} (Cost: {Colors.FIN_NEGATIVE}${t.cost:,.2f}{Colors.RESET}{Colors.OPTION_TEXT}, Dur: {t.duration_days}d, Net Profit: {Colors.FIN_POSITIVE}${t.total_net_profit:,.2f}{Colors.RESET}{Colors.OPTION_TEXT}){Colors.RESET}")
            try:
                idx_choice = get_validated_input("Template to adjust (0 to skip): ", int, 0)
                if idx_choice == 0: continue
                idx = idx_choice - 1
                if 0 <= idx < len(settings_copy['contract_templates']):
                    template = settings_copy['contract_templates'][idx]
                    print(f"\n{Colors.SUBHEADER}--- Editing: {template.name} ---{Colors.RESET}")
                    template.cost = get_validated_input(f"  New Cost (${template.cost:,.2f}): $", float, template.cost)
                    template.duration_days = get_validated_input(f"  New Duration ({template.duration_days}d): ", int, template.duration_days)
                    template.total_net_profit = get_validated_input(f"  New Net Profit (${template.total_net_profit:,.2f}): $", float, template.total_net_profit)
                    print(f"  {Colors.SUCCESS}✅ Template updated.{Colors.RESET}")
            except: print(f"  {Colors.ERROR}Invalid selection.{Colors.RESET}")
        elif is_initial_setup and choice == '2':
            settings_copy['initial_profit'] = get_validated_input(f"New initial profit ($): ", float, settings_copy['initial_profit'])
        elif is_initial_setup and choice == '3':
            settings_copy['start_date'] = get_validated_input(f"New start date (YYYY-MM-DD): ", datetime.date, settings_copy['start_date'].strftime('%Y-%m-%d'))
        elif is_initial_setup and choice == '4':
            print(f"\n{Colors.SUBHEADER}--- Pre-existing Held Contracts ---{Colors.RESET}")
            if settings_copy['held_contracts']:
                for i, hc in enumerate(settings_copy['held_contracts']): print(f"{Colors.OPTION}[{i+1}]{Colors.OPTION_TEXT} {hc.name} (ID: {hc.id}, Starts: {hc.start_date.strftime('%Y-%m-%d')}){Colors.RESET}")
            else: print(f"  {Colors.INFO}No pre-existing contracts.{Colors.RESET}")
            action = input(f"{Colors.PROMPT}Add (a), Remove (r), Back (b)?: {Colors.RESET}{Colors.INPUT_FIELD}").lower()
            print(Colors.RESET, end="")
            if action == 'a':
                print(f"\n{Colors.SUBHEADER}Templates to add as held:{Colors.RESET}"); [print(f"{Colors.OPTION}[{i+1}]{Colors.OPTION_TEXT} {t.name}{Colors.RESET}") for i,t in enumerate(settings_copy['contract_templates'])]
                try:
                    t_idx = get_validated_input("Select type: ", int)-1
                    if 0 <= t_idx < len(settings_copy['contract_templates']):
                        tpl=settings_copy['contract_templates'][t_idx]
                        s_date=get_validated_input("Start date (YYYY-MM-DD): ",datetime.date)
                        held_c=MiningContract(tpl.name,tpl.cost,tpl.duration_days,tpl.total_net_profit,s_date,f"HELD_{tpl.name.replace(' ','_')}_{len(settings_copy['held_contracts'])+1}")
                        settings_copy['held_contracts'].append(held_c); print(f"  {Colors.SUCCESS}Added: {held_c.name}{Colors.RESET}")
                except: print(f"  {Colors.ERROR}Invalid input.{Colors.RESET}")
            elif action == 'r' and settings_copy['held_contracts']:
                try: r_idx=get_validated_input("Num to remove: ",int)-1; removed=settings_copy['held_contracts'].pop(r_idx); print(f"  {Colors.SUCCESS}Removed: {removed.name}{Colors.RESET}")
                except: print(f"  {Colors.ERROR}Invalid input.{Colors.RESET}")
        elif choice == '5':
            settings_copy['auto_purchase_forecast'] = not settings_copy['auto_purchase_forecast']
            print(f"  {Colors.INFO}Auto-Purchase Forecast: {'ON' if settings_copy['auto_purchase_forecast'] else 'OFF'}.{Colors.RESET}")
        elif is_initial_setup and choice == 'v':
            print(f"\n{Colors.SUBHEADER}--- Current Configuration Summary ---{Colors.RESET}")
            print(f"Initial Profit: {Colors.FIN_POSITIVE}${settings_copy['initial_profit']:,.2f}{Colors.RESET}")
            print(f"Start Date: {Colors.DATE_HIGHLIGHT}{settings_copy['start_date'].strftime('%Y-%m-%d')}{Colors.RESET}")
            print(f"Auto-Purchase Forecast: {Colors.INFO}{'ON' if settings_copy['auto_purchase_forecast'] else 'OFF'}{Colors.RESET}")
            print(f"{Colors.SUBHEADER}Contract Templates:{Colors.RESET}")
            for t in settings_copy['contract_templates']: print(f"  - {t.name}, Cost: {Colors.FIN_NEGATIVE}${t.cost:,.2f}{Colors.RESET}, Dur: {t.duration_days}d, Net Profit: {Colors.FIN_POSITIVE}${t.total_net_profit:,.2f}{Colors.RESET}")
            print(f"{Colors.SUBHEADER}Held Contracts:{Colors.RESET}")
            if settings_copy['held_contracts']: [print(f"  - {hc.name}, Starts: {Colors.DATE_HIGHLIGHT}{hc.start_date.strftime('%Y-%m-%d')}{Colors.RESET}") for hc in settings_copy['held_contracts']]
            else: print(f"  {Colors.INFO}None{Colors.RESET}")
            input(f"{Colors.PROMPT}Press Enter to continue...{Colors.RESET}")
        elif choice == 's': print(f"  {Colors.SUCCESS}✅ Settings applied.{Colors.RESET}"); return settings_copy
        elif choice == 'c': print(f"  {Colors.INFO}Changes cancelled.{Colors.RESET}"); return current_game_settings_obj 
        else: print(f"  {Colors.ERROR}Invalid choice.{Colors.RESET}")

# --- CALENDAR DISPLAY ---
def display_calendar_view(year, month, current_simulation_date, all_known_contracts_list):
    month_calendar = calendar.monthcalendar(year, month)
    month_name = datetime.date(year, month, 1).strftime("%B %Y")

    header_line = "=" * ((8 * 7) + 6)
    print(f"\n{Colors.INFO}{header_line}{Colors.RESET}") 
    print(f"{Colors.INFO}🗓️  {month_name.center((8*7)-4)} 🗓️{Colors.RESET}")
    print(f"{Colors.INFO}{header_line}{Colors.RESET}")
    print(f"{Colors.BOLD} MoSPLC  TuSPLC  WeSPLC  ThSPLC  FrSPLC  SaSPLC  SuSPLC {Colors.RESET}") 

    contracts_for_month_view = []
    first_day_of_month = datetime.date(year, month, 1)
    last_day_of_month = datetime.date(year, month, calendar.monthrange(year, month)[1])

    for contract in all_known_contracts_list:
        if not contract.start_date: continue
        contract_end_day = contract.get_cost_return_day() 
        if contract_end_day is None: 
            contract_end_day = contract.get_last_payout_day() 
            if contract_end_day is None: continue 

        if not (contract_end_day < first_day_of_month or contract.start_date > last_day_of_month):
            contracts_for_month_view.append(contract)

    for week in month_calendar:
        week_str = ""
        for day_num in week:
            if day_num == 0:
                week_str += " " * 8 
            else:
                cell_date = datetime.date(year, month, day_num)
                s_ind, p_ind, l_ind, c_ind = '-', '-', '-', '-'
                
                for contract in contracts_for_month_view: 
                    if contract.start_date == cell_date: s_ind = Colors.CALENDAR_EVENT_S + 'S' + Colors.RESET
                    if contract.get_payout_on_date(cell_date) > 0: p_ind = Colors.CALENDAR_EVENT_P + '$' + Colors.RESET
                    last_payout_day = contract.get_last_payout_day()
                    if last_payout_day and last_payout_day == cell_date: l_ind = Colors.CALENDAR_EVENT_L + 'L' + Colors.RESET
                    cost_return_day = contract.get_cost_return_day()
                    if cost_return_day and cost_return_day == cell_date: c_ind = Colors.CALENDAR_EVENT_C + 'C' + Colors.RESET
                
                event_indicators = f"{s_ind}{p_ind}{l_ind}{c_ind}" 
                
                day_str = str(day_num).rjust(2)
                if cell_date == current_simulation_date:
                    week_str += f"{Colors.CALENDAR_CURRENT_DAY}[{day_str}]{Colors.RESET}{event_indicators} " 
                else:
                    week_str += f" {Colors.CALENDAR_DAY}{day_str}{Colors.RESET} {event_indicators} " 
        print(week_str)
    print(f"{Colors.INFO}-{Colors.RESET}" * ((8 * 7) + 6))
    print(f"Legend: [{Colors.CALENDAR_CURRENT_DAY}DD{Colors.RESET}]=Curr Day, {Colors.CALENDAR_EVENT_S}S{Colors.RESET}=Start, {Colors.CALENDAR_EVENT_P}${Colors.RESET}=Payout, {Colors.CALENDAR_EVENT_L}L{Colors.RESET}=Last Payout, {Colors.CALENDAR_EVENT_C}C{Colors.RESET}=Cost Return")
    print(f"{Colors.INFO}{header_line}{Colors.RESET}")


# --- SAVE/LOAD GAME STATE ---
def save_game_state(game_state_dict, filepath):
    try:
        serializable_game_settings = {
            'contract_templates_data': [t.to_dict() for t in game_state_dict['game_settings']['contract_templates']],
            'initial_profit': game_state_dict['game_settings']['initial_profit'],
            'start_date_str': game_state_dict['game_settings']['start_date'].isoformat(),
            'held_contracts_data': [hc.to_dict() for hc in game_state_dict['game_settings']['held_contracts']],
            'auto_purchase_forecast': game_state_dict['game_settings']['auto_purchase_forecast']
        }
        serializable_state = {
            'current_date_str': game_state_dict['current_date'].isoformat(),
            'current_profit': game_state_dict['current_profit'],
            'active_contracts_data': [c.to_dict() for c in game_state_dict['active_contracts']],
            'purchase_history': game_state_dict['purchase_history'],
            'deposits_history': game_state_dict['deposits_history'],
            'game_settings_data': serializable_game_settings 
        }
        with open(filepath, 'w') as f: json.dump(serializable_state, f, indent=4)
        print(f"  {Colors.SUCCESS}✅ Game state saved to '{filepath}'.{Colors.RESET}")
    except Exception as e: print(f"  {Colors.ERROR}❌ Error saving game state: {e}{Colors.RESET}")

def load_game_state(filepath):
    try:
        if not os.path.exists(filepath): print(f"  {Colors.ERROR}❌ Save file '{filepath}' not found.{Colors.RESET}"); return None
        with open(filepath, 'r') as f: loaded_data = json.load(f)
        
        gs_data = loaded_data['game_settings_data'] 
        game_settings_obj = {
            'contract_templates': [MiningContract.from_dict(t_data) for t_data in gs_data['contract_templates_data']],
            'initial_profit': gs_data['initial_profit'],
            'start_date': datetime.date.fromisoformat(gs_data['start_date_str']),
            'held_contracts': [MiningContract.from_dict(hc_data) for hc_data in gs_data.get('held_contracts_data', [])],
            'auto_purchase_forecast': gs_data['auto_purchase_forecast']
        }
        state = {
            'current_date': datetime.date.fromisoformat(loaded_data['current_date_str']),
            'current_profit': loaded_data['current_profit'],
            'active_contracts': [MiningContract.from_dict(c_data) for c_data in loaded_data['active_contracts_data']],
            'purchase_history': loaded_data['purchase_history'],
            'deposits_history': loaded_data.get('deposits_history', []),
            'game_settings': game_settings_obj 
        }
        print(f"  {Colors.SUCCESS}✅ Game state loaded from '{filepath}'.{Colors.RESET}")
        return state
    except Exception as e: print(f"  {Colors.ERROR}❌ Error loading game state: {e}{Colors.RESET}"); return None

def list_and_select_save_file(save_folder_path):
    print(f"\n{Colors.SUBHEADER}--- Load Game from '{save_folder_path}' ---{Colors.RESET}")
    os.makedirs(save_folder_path, exist_ok=True) 
    save_files = glob.glob(os.path.join(save_folder_path, f"*{SAVE_GAME_EXTENSION}"))
    if not save_files: print(f"{Colors.INFO}No save files found.{Colors.RESET}"); return None
    print(f"{Colors.INFO}Available save files:{Colors.RESET}"); [print(f"{Colors.OPTION}[{i+1}]{Colors.OPTION_TEXT} {os.path.basename(f_path)}{Colors.RESET}") for i, f_path in enumerate(save_files)]
    try:
        choice = get_validated_input("Enter number of save file to load (0 to cancel): ", int, 0)
        if choice == 0: return None
        return save_files[choice - 1]
    except: print(f"  {Colors.ERROR}Invalid selection.{Colors.RESET}"); return None

# --- DAILY RECOMMENDATIONS ---
def generate_and_display_daily_recommendations(game_settings, current_date, current_profit, 
                                             all_known_contracts_for_events, 
                                             contract_types_already_purchased_today): 
    print(f"\n{Colors.SUBHEADER}--- Daily Briefing & Recommendations ---{Colors.RESET}")
    
    # Calculate Total Daily Earning Rate from contracts paying out today
    current_daily_earning_rate = sum(c.get_payout_on_date(current_date) for c in all_known_contracts_for_events)
    print(f"{Colors.INFO}Current Total Daily Earning Rate (Net Profit from active contracts today): {Colors.FIN_POSITIVE}${current_daily_earning_rate:,.2f}{Colors.RESET}")

    recommendations = []
    upcoming_events = {} 

    sorted_templates = sorted(game_settings['contract_templates'], key=lambda t: t.cost, reverse=True)
    viable_purchases_today = []
    
    for tpl in sorted_templates:
        cost_return_day_if_bought_today = current_date + datetime.timedelta(days=tpl.duration_days + 1)
        can_afford = current_profit >= tpl.cost 
        meets_deadline = cost_return_day_if_bought_today <= FORECAST_DEADLINE
        
        if tpl.name in contract_types_already_purchased_today: 
            continue 

        if can_afford and meets_deadline:
            viable_purchases_today.append(f"- Consider purchasing '{Colors.BOLD}{tpl.name}{Colors.RESET}' (Cost: {Colors.FIN_NEGATIVE}${tpl.cost:,.2f}{Colors.RESET}, Net Profit: {Colors.FIN_POSITIVE}${tpl.total_net_profit:,.2f}{Colors.RESET})")
    
    if viable_purchases_today:
        recommendations.append(f"{Colors.INFO}Recommended Purchases for Today (based on start-of-day balance):{Colors.RESET}")
        recommendations.extend(viable_purchases_today)
    elif DAILY_CONTRACT_NAME not in contract_types_already_purchased_today: 
        daily_tpl_obj = next((t for t in game_settings['contract_templates'] if t.name == DAILY_CONTRACT_NAME), None)
        if daily_tpl_obj and current_profit >= daily_tpl_obj.cost:
            if (current_date + datetime.timedelta(days=daily_tpl_obj.duration_days + 1)) <= FORECAST_DEADLINE:
                 recommendations.append(f"- Consider purchasing '{Colors.BOLD}{DAILY_CONTRACT_NAME}{Colors.RESET}' (Cost: {Colors.FIN_NEGATIVE}${daily_tpl_obj.cost:,.2f}{Colors.RESET}) if not already done.")
    
    if not recommendations and not viable_purchases_today : # Adjusted condition
        recommendations.append(f"{Colors.INFO}No immediate contract purchases recommended with current balance, purchase limits, and deadline.{Colors.RESET}")

    for i in range(1, RECOMMENDATION_SCAN_DAYS + 1):
        scan_date = current_date + datetime.timedelta(days=i)
        if scan_date > FORECAST_DEADLINE + datetime.timedelta(days=1) : 
            break 
        
        daily_events = []
        for contract in all_known_contracts_for_events: 
            if not contract.start_date : continue
            last_payout = contract.get_last_payout_day()
            cost_return = contract.get_cost_return_day()
            if last_payout == scan_date:
                daily_events.append(f"'{Colors.BOLD}{contract.name}{Colors.RESET}' (ID: ...{contract.id[-6:]}) {Colors.CALENDAR_EVENT_L}final payout{Colors.RESET}.")
            if cost_return == scan_date:
                daily_events.append(f"'{Colors.BOLD}{contract.name}{Colors.RESET}' (ID: ...{contract.id[-6:]}) cost ({Colors.FIN_POSITIVE}${contract.cost:,.2f}{Colors.RESET}) {Colors.CALENDAR_EVENT_C}settles{Colors.RESET}.")
        
        if daily_events:
            upcoming_events.setdefault(scan_date, []).extend(daily_events)

    if upcoming_events:
        recommendations.append(f"\n{Colors.INFO}Upcoming Events:{Colors.RESET}")
        for event_date in sorted(upcoming_events.keys()):
            day_label = "Tomorrow" if event_date == current_date + datetime.timedelta(days=1) else event_date.strftime('%a, %b %d')
            recommendations.append(f"  {Colors.DATE_HIGHLIGHT}{day_label}{Colors.RESET}:")
            for event_str in upcoming_events[event_date]:
                recommendations.append(f"    - {event_str}")
    
    # Print recommendations only if there are any beyond the default "no recs"
    # or if there are upcoming events
    if recommendations and (len(recommendations) > 1 or (len(recommendations) == 1 and not recommendations[0].startswith("No immediate")) or upcoming_events) :
        for rec_line in recommendations:
            print(rec_line)
    elif not upcoming_events: # Only print this if truly nothing to show (no recs, no events)
         print(f"{Colors.INFO}No specific recommendations or major upcoming events in the near future.{Colors.RESET}")
    print(f"{Colors.SUBHEADER}--- End of Daily Briefing ---{Colors.RESET}")


# --- FORECASTING LOGIC ---
def run_forecast_menu(current_game_settings_obj, current_sim_date, current_sim_profit, current_active_contracts_list):
    days_to_forecast = get_validated_input("Days to forecast (default 90): ", int, 90)
    if days_to_forecast <= 0: print(f"  {Colors.ERROR}Duration must be positive.{Colors.RESET}"); return

    fc_settings = deepcopy(current_game_settings_obj) 
    fc_contracts = deepcopy(current_active_contracts_list)

    if fc_settings['auto_purchase_forecast']:
        run_auto_purchase_forecast(fc_settings, current_sim_date, current_sim_profit, fc_contracts, days_to_forecast)
    else:
        run_simple_forecast(current_sim_date, current_sim_profit, fc_contracts, days_to_forecast)

def run_simple_forecast(current_date, current_profit, active_contracts, num_days):
    print(f"\n{Colors.SUBHEADER}--- {num_days}-Day Simple Forecast ---{Colors.RESET}")
    fc_profit = current_profit
    for day_offset in range(num_days):
        fc_date = current_date + datetime.timedelta(days=day_offset + 1)
        daily_net_profit = sum(c.get_payout_on_date(fc_date) for c in active_contracts)
        fc_profit += daily_net_profit
        
        active_contracts_for_forecast_next_day = []
        for c in active_contracts:
            cost_return_day = c.get_cost_return_day()
            if cost_return_day and fc_date < cost_return_day:
                 active_contracts_for_forecast_next_day.append(c)
        active_contracts = active_contracts_for_forecast_next_day
        print(f"Day {day_offset+1} ({Colors.DATE_HIGHLIGHT}{fc_date.strftime('%Y-%m-%d')}{Colors.RESET}): Net Profit {Colors.FIN_POSITIVE}+${daily_net_profit:,.2f}{Colors.RESET} | EOD Profit: {Colors.FIN_POSITIVE}${fc_profit:,.2f}{Colors.RESET}")

def run_auto_purchase_forecast(game_settings_obj, current_date, current_profit, active_contracts_list, num_days):
    print(f"\n{Colors.SUBHEADER}--- {num_days}-Day AUTO-PURCHASE Forecast (Deadline: {FORECAST_DEADLINE.strftime('%Y-%m-%d')}) ---{Colors.RESET}")
    sim_profit = current_profit
    sim_contracts = active_contracts_list 
    purchasable_templates = sorted(game_settings_obj['contract_templates'], key=lambda t: t.cost, reverse=True)

    for day_offset in range(num_days):
        sim_fc_date = current_date + datetime.timedelta(days=day_offset + 1)
        
        cost_return_day_of_potential_contract = lambda tpl: sim_fc_date + datetime.timedelta(days=tpl.duration_days + 1)

        if sim_fc_date > FORECAST_DEADLINE: 
            print(f"{Colors.WARNING}Day {day_offset+1}: Forecast stopped. Current forecast day {sim_fc_date.strftime('%Y-%m-%d')} is past deadline {FORECAST_DEADLINE.strftime('%Y-%m-%d')}.{Colors.RESET}")
            break 
        
        shortest_contract_possible = min(purchasable_templates, key=lambda t: t.duration_days + 1, default=None)
        if shortest_contract_possible and cost_return_day_of_potential_contract(shortest_contract_possible) > FORECAST_DEADLINE:
            pass 

        daily_net_profit = sum(c.get_payout_on_date(sim_fc_date) for c in sim_contracts)
        sim_profit += daily_net_profit
        
        returned_investment_fc = 0
        temp_sim_contracts_after_settlement = []
        for c_fc in sim_contracts:
            cost_return_day_fc = c_fc.get_cost_return_day()
            if cost_return_day_fc and sim_fc_date == cost_return_day_fc:
                sim_profit += c_fc.cost
                returned_investment_fc += c_fc.cost
            elif cost_return_day_fc and sim_fc_date < cost_return_day_fc:
                temp_sim_contracts_after_settlement.append(c_fc)
            elif not cost_return_day_fc and c_fc.start_date: 
                temp_sim_contracts_after_settlement.append(c_fc)
        sim_contracts = temp_sim_contracts_after_settlement
        
        log = [f"Day {day_offset+1} ({Colors.DATE_HIGHLIGHT}{sim_fc_date.strftime('%Y-%m-%d')}{Colors.RESET})", f"Net Profit In: {Colors.FIN_POSITIVE}+${daily_net_profit:,.2f}{Colors.RESET}"]
        if returned_investment_fc > 0:
            log.append(f"Investments Returned: {Colors.FIN_POSITIVE}+${returned_investment_fc:,.2f}{Colors.RESET}")

        purchased_today = True
        while purchased_today:
            purchased_today = False
            for tpl_obj in purchasable_templates: 
                if sim_profit >= tpl_obj.cost and cost_return_day_of_potential_contract(tpl_obj) <= FORECAST_DEADLINE:
                    sim_profit -= tpl_obj.cost
                    new_c = MiningContract(tpl_obj.name, tpl_obj.cost, tpl_obj.duration_days, tpl_obj.total_net_profit, 
                                           sim_fc_date, f"FCST_{tpl_obj.name.replace(' ','_')}_{len(sim_contracts)+1}")
                    sim_contracts.append(new_c)
                    log.append(f"{Colors.SUCCESS}BOUGHT {tpl_obj.name}{Colors.RESET} ({Colors.FIN_NEGATIVE}-${new_c.cost:,.2f}{Colors.RESET})")
                    purchased_today = True; break
        log.append(f"EOD Profit: {Colors.FIN_POSITIVE}${sim_profit:,.2f}{Colors.RESET}")
        print(" | ".join(log))
        
        sim_contracts_next_day_fc = []
        for c in sim_contracts:
            cost_return_day = c.get_cost_return_day()
            if cost_return_day and sim_fc_date < cost_return_day: 
                sim_contracts_next_day_fc.append(c)
        sim_contracts = sim_contracts_next_day_fc


# --- MAIN SIMULATION LOOP ---
def run_simulation_loop(game_state, current_save_filepath, prog_config): 
    current_date = game_state['current_date']
    current_profit = game_state['current_profit']
    active_contracts = game_state['active_contracts'] 
    purchase_history = game_state['purchase_history']
    deposits_history = game_state['deposits_history']
    current_game_settings = deepcopy(game_state['game_settings']) 
    
    daily_state_history = [] 
    _last_processed_date_for_daily_flags = None 
    contract_types_purchased_today = set() 

    print(f"\n{Colors.HEADER}--- Simulation Started/Resumed ---{Colors.RESET}")
    if not current_save_filepath: print(f"{Colors.WARNING}Warning: Session not tied to a save file. Use '[save]' to create one.{Colors.RESET}")
    else: print(f"{Colors.INFO}Current session linked to: {current_save_filepath}{Colors.RESET}")

    # Outer loop: Iterates per day
    while True: 
        # --- Start of Day Processing ---
        if not daily_state_history or daily_state_history[-1]['date'] != current_date:
            snapshot = {
                'date': current_date,
                'profit': current_profit, 
                'active_contracts_data': [c.to_dict() for c in active_contracts], 
                'purchase_history_snapshot': deepcopy(purchase_history),
                'deposits_history_snapshot': deepcopy(deposits_history),
                'contract_types_purchased_today_snapshot': deepcopy(contract_types_purchased_today) 
            }
            daily_state_history.append(snapshot)
            if len(daily_state_history) > MAX_ROLLBACK_HISTORY_DAYS:
                daily_state_history.pop(0) 
        
        if _last_processed_date_for_daily_flags != current_date:
            contract_types_purchased_today = set() 
            _last_processed_date_for_daily_flags = current_date
        
        all_contracts_for_day_view = get_all_known_contracts(current_game_settings, active_contracts, purchase_history)
        
        calendar_display_contracts = [
            c for c in all_contracts_for_day_view 
            if c.start_date and (
                (c.start_date.year == current_date.year and c.start_date.month == current_date.month) or
                (c.get_cost_return_day() and c.get_cost_return_day().year == current_date.year and c.get_cost_return_day().month == current_date.month) or
                (c.start_date <= datetime.date(current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]) and \
                 (c.get_cost_return_day() is None or c.get_cost_return_day() >= datetime.date(current_date.year, current_date.month, 1)))
            )
        ]
        display_calendar_view(current_date.year, current_date.month, current_date, calendar_display_contracts)
        
        generate_and_display_daily_recommendations(current_game_settings, current_date, current_profit, 
                                                 all_contracts_for_day_view, 
                                                 contract_types_purchased_today) 

        balance_at_start_of_day = current_profit 

        for c in active_contracts:
            if c.start_date and c.duration_days > 0:
                last_payout_day = c.get_last_payout_day()
                if last_payout_day and current_date == last_payout_day:
                    print(f"{Colors.INFO}INFO: Contract '{c.name}' (ID: {c.id}) makes its final net profit payout today. Cost settles tomorrow.{Colors.RESET}")

        todays_net_profit_payout = sum(c.get_payout_on_date(current_date) for c in active_contracts)
        current_profit += todays_net_profit_payout

        returned_investment_today = 0
        contracts_still_in_play_after_settlements = [] 
        for c in active_contracts:
            cost_return_day = c.get_cost_return_day()
            if cost_return_day and current_date == cost_return_day:
                current_profit += c.cost
                returned_investment_today += c.cost
                print(f"{Colors.INFO}INFO: Contract '{c.name}' (ID: {c.id}) settled. Initial investment of {Colors.FIN_POSITIVE}${c.cost:,.2f}{Colors.RESET} returned.{Colors.RESET}")
            elif cost_return_day and current_date < cost_return_day : 
                contracts_still_in_play_after_settlements.append(c)
            elif not cost_return_day and c.start_date : 
                 contracts_still_in_play_after_settlements.append(c) 
        active_contracts = contracts_still_in_play_after_settlements 

        print("\n" + "="*70)
        print(f"🗓️  Date: {Colors.DATE_HIGHLIGHT}{current_date.strftime('%A, %B %d, %Y')}{Colors.RESET}")
        print(f"💰 Balance at Start of Day: {Colors.FIN_POSITIVE}${balance_at_start_of_day:,.2f}{Colors.RESET}")
        print(f"✅ Today's Net Profit Payout: {Colors.FIN_POSITIVE}${todays_net_profit_payout:,.2f}{Colors.RESET}")
        if returned_investment_today > 0:
            print(f"💰 Today's Returned Investments: {Colors.FIN_POSITIVE}${returned_investment_today:,.2f}{Colors.RESET}")
        print(f"{Colors.BOLD}💰 EOD Available Profit (Current Balance): {Colors.FIN_POSITIVE}${current_profit:,.2f}{Colors.RESET}")
        print(f"{Colors.INFO}Contracts in Play (Paying or Awaiting Settlement): {len(active_contracts)}{Colors.RESET}")
        print("="*70)
        
        # --- Inner Loop for User Actions on the CURRENT DAY ---
        while True: 
            print(f"\n{Colors.PROMPT}Choose an action for {Colors.DATE_HIGHLIGHT}{current_date.strftime('%A, %B %d, %Y')}{Colors.RESET}{Colors.PROMPT}:{Colors.RESET}")
            print(f"  {Colors.OPTION}[p]{Colors.OPTION_TEXT} Purchase contract  {Colors.OPTION}[d]{Colors.OPTION_TEXT} Record deposit   {Colors.OPTION}[v]{Colors.OPTION_TEXT} View contracts{Colors.RESET}")
            print(f"  {Colors.OPTION}[h]{Colors.OPTION_TEXT} History            {Colors.OPTION}[f]{Colors.OPTION_TEXT} Forecast         {Colors.OPTION}[g]{Colors.OPTION_TEXT} Current Game Settings{Colors.RESET}")
            print(f"  {Colors.OPTION}[r]{Colors.OPTION_TEXT} Rollback to Date")
            print(f"  {Colors.OPTION}[save]{Colors.OPTION_TEXT} Save Game      {Colors.OPTION}[load]{Colors.OPTION_TEXT} Load Game      {Colors.OPTION}[n/enter]{Colors.OPTION_TEXT} Next Day{Colors.RESET}")
            print(f"  {Colors.OPTION}[m]{Colors.OPTION_TEXT} Main Menu (lose unsaved progress)       {Colors.OPTION}[q]{Colors.OPTION_TEXT} Quit Program{Colors.RESET}")
            choice = input(f"{Colors.PROMPT}Your choice: {Colors.RESET}{Colors.INPUT_FIELD}").lower().strip()
            print(Colors.RESET, end="")


            if choice == 'p':
                print(f"\n{Colors.SUBHEADER}--- Purchase New Contract ---{Colors.RESET}"); [print(f"{Colors.OPTION}[{i+1}]{Colors.OPTION_TEXT} {t.name} Cost:{Colors.FIN_NEGATIVE}${t.cost:,.2f}{Colors.RESET}") for i,t in enumerate(current_game_settings['contract_templates'])]
                try:
                    tpl_idx = get_validated_input("Select (0 to cancel):",int,0)-1
                    if tpl_idx != -1 and 0 <= tpl_idx < len(current_game_settings['contract_templates']):
                        tpl=current_game_settings['contract_templates'][tpl_idx]
                        
                        if tpl.name in contract_types_purchased_today: 
                            print(f"{Colors.INFO}INFO: Contract type '{tpl.name}' can only be purchased once per day.{Colors.RESET}")
                        elif current_profit >= tpl.cost:
                            current_profit -= tpl.cost
                            new_c=MiningContract(tpl.name,tpl.cost,tpl.duration_days,tpl.total_net_profit,current_date,f"BOUGHT_{tpl.name.replace(' ','_')}_{len(purchase_history)+1}")
                            active_contracts.append(new_c) 
                            purchase_history.append({"date":current_date.strftime('%Y-%m-%d'),"name":new_c.name,"cost":new_c.cost,"id":new_c.id,"type":"Purchased"})
                            print(f"{Colors.SUCCESS}Purchased: {new_c.name}. Profit after cost: {Colors.FIN_POSITIVE}${current_profit:,.2f}{Colors.RESET}. First payout will be tomorrow.{Colors.RESET}")
                            contract_types_purchased_today.add(tpl.name) 
                        else: print(f"{Colors.ERROR}Insufficient funds. Need ${tpl.cost:,.2f}{Colors.RESET}")
                except: print(f"{Colors.ERROR}Invalid selection.{Colors.RESET}")
            elif choice == 'd':
                amt=get_validated_input("Deposit amount: $",float);
                if amt>0:
                    dep_date_str=get_validated_input(f"Date (YYYY-MM-DD, def {current_date.strftime('%Y-%m-%d')}):",str,current_date.strftime('%Y-%m-%d'))
                    try: 
                        dep_date=datetime.datetime.strptime(dep_date_str,'%Y-%m-%d').date()
                        current_profit+=amt
                        deposits_history.append({"date":dep_date.strftime('%Y-%m-%d'),"amount":amt,"type":"Deposit"})
                        print(f"{Colors.SUCCESS}Deposited ${amt:,.2f}. New current balance: {Colors.FIN_POSITIVE}${current_profit:,.2f}{Colors.RESET}")
                    except: print(f"{Colors.ERROR}Invalid date.{Colors.RESET}")
                else: print(f"{Colors.WARNING}Amount must be positive.{Colors.RESET}")
            elif choice == 'v':
                master_contract_list_for_view = get_all_known_contracts(current_game_settings, active_contracts, purchase_history)
                view_type_choice = get_validated_input("View [s]implified (current & pending) or [d]etailed (all history)? ", str, 's').lower()
                
                display_list_for_view = []
                if view_type_choice == 's':
                    print(f"\n{Colors.SUBHEADER}--- Simplified View: Current & Pending Contracts ---{Colors.RESET}")
                    for c_instance in master_contract_list_for_view:
                        if not c_instance.start_date: continue 
                        cost_return_day = c_instance.get_cost_return_day()
                        is_pending_future = c_instance.start_date > current_date
                        is_relevant_active_or_settling = (
                            c_instance.start_date <= current_date and
                            (not cost_return_day or current_date <= cost_return_day) 
                        )
                        if is_pending_future or is_relevant_active_or_settling:
                            display_list_for_view.append(c_instance)
                else: 
                    print(f"\n{Colors.SUBHEADER}--- Detailed View: All Contracts ---{Colors.RESET}")
                    display_list_for_view = master_contract_list
                
                if not display_list_for_view:
                    print(f"{Colors.INFO}No contracts to display for this view.{Colors.RESET}")
                else:
                    for c_instance in sorted(display_list_for_view, key=lambda x: (x.start_date or datetime.date.min, x.name)):
                        status = "Unknown"
                        last_payout_day = c_instance.get_last_payout_day()
                        cost_return_day = c_instance.get_cost_return_day()

                        if c_instance.start_date:
                            if current_date < c_instance.start_date: 
                                status = f"{Colors.INFO}Pending (Starts {c_instance.start_date.strftime('%Y-%m-%d')}){Colors.RESET}"
                            elif current_date == c_instance.start_date:
                                status = f"{Colors.BRIGHT_GREEN}Active (Starts Today - First Payout Tomorrow){Colors.RESET}"
                            elif c_instance.get_payout_on_date(current_date) > 0: 
                                status = f"{Colors.GREEN}Active (Paying Today){Colors.RESET}"
                            elif last_payout_day and current_date == last_payout_day: 
                                status = f"{Colors.BRIGHT_YELLOW}Active (Final Payout Today - Cost Settles Tomorrow){Colors.RESET}"
                            elif cost_return_day and current_date < cost_return_day and (last_payout_day and current_date > last_payout_day): 
                                status = f"{Colors.CYAN}Active (Awaiting Cost Settlement - Due {cost_return_day.strftime('%Y-%m-%d')}){Colors.RESET}"
                            elif cost_return_day and current_date == cost_return_day: 
                                status = f"{Colors.BRIGHT_BLUE}Concluded (Cost Settled Today){Colors.RESET}" 
                            elif cost_return_day and current_date > cost_return_day: 
                                status = f"{Colors.BRIGHT_BLACK}Concluded (Expired after {cost_return_day.strftime('%Y-%m-%d')}){Colors.RESET}"
                            elif not last_payout_day : 
                                status = f"{Colors.WARNING}No Payout Period (Check Duration){Colors.RESET}"
                            else: 
                                if last_payout_day and c_instance.start_date < current_date < last_payout_day and not c_instance.get_payout_on_date(current_date) > 0 :
                                     status = f"{Colors.INFO}Active (Operational - Not Paying Today){Colors.RESET}" 
                                elif last_payout_day and current_date > last_payout_day and cost_return_day and current_date < cost_return_day: 
                                     status = f"{Colors.CYAN}Awaiting Cost Settlement (Due {cost_return_day.strftime('%Y-%m-%d')}){Colors.RESET}"
                                else: 
                                     status = f"{Colors.WARNING}Operational (Review Dates){Colors.RESET}" if c_instance.start_date <= current_date else f"{Colors.WARNING}Status Undetermined{Colors.RESET}"
                        print(f"  {c_instance} (Status: {status})")

            elif choice == 'h':
                print(f"\n{Colors.SUBHEADER}--- Transaction History ---{Colors.RESET}"); full_hist=sorted(purchase_history+deposits_history,key=lambda x:x['date'])
                if not full_hist: print(f"{Colors.INFO}No transactions.{Colors.RESET}");
                else: [print(f"- {Colors.DATE_HIGHLIGHT}{item['date']}{Colors.RESET}: {item['type']} '{Colors.BOLD}{item.get('name','N/A')}{Colors.RESET}' " + (f"Cost:{Colors.FIN_NEGATIVE}${item['cost']:,.2f}{Colors.RESET}" if 'cost' in item else f"Amount:{Colors.FIN_POSITIVE}${item['amount']:,.2f}{Colors.RESET}")) for item in full_hist]
            elif choice == 'f':
                run_forecast_menu(current_game_settings, current_date, current_profit, active_contracts)
            elif choice == 'g':
                updated_game_settings = manage_game_settings(current_game_settings, is_initial_setup=False, context_info="Current Game Session Settings")
                if updated_game_settings: current_game_settings = updated_game_settings
            elif choice == 'r': 
                print(f"\n{Colors.SUBHEADER}--- Rollback to a Previous Date (max {MAX_ROLLBACK_HISTORY_DAYS} days in this session) ---{Colors.RESET}")
                if not daily_state_history:
                    print(f"{Colors.INFO}No history available for rollback in this session.{Colors.RESET}")
                    continue
                
                print(f"{Colors.INFO}Available dates for rollback (from most recent):{Colors.RESET}")
                for i, snap in enumerate(reversed(daily_state_history)):
                    print(f"  {Colors.OPTION}[{i+1}]{Colors.OPTION_TEXT} {snap['date'].strftime('%Y-%m-%d')}{Colors.RESET}")
                
                try:
                    rb_choice_idx = get_validated_input(f"Enter number of date to rollback to (0 to cancel, 1 is yesterday if available): ", int, 0)
                    if rb_choice_idx == 0:
                        print(f"{Colors.INFO}Rollback cancelled.{Colors.RESET}"); continue
                    
                    actual_idx = len(daily_state_history) - rb_choice_idx 
                    
                    if 0 <= actual_idx < len(daily_state_history):
                        snapshot_to_restore = daily_state_history[actual_idx]
                        
                        if input(f"{Colors.WARNING}Rollback to start of {snapshot_to_restore['date'].strftime('%Y-%m-%d')}? This cannot be undone in-session. (y/n): {Colors.RESET}{Colors.INPUT_FIELD}").lower() != 'y':
                            print(Colors.RESET, end="")
                            print(f"{Colors.INFO}Rollback cancelled.{Colors.RESET}"); continue
                        print(Colors.RESET, end="")

                        current_date = snapshot_to_restore['date']
                        current_profit = snapshot_to_restore['profit']
                        active_contracts = [MiningContract.from_dict(data) for data in snapshot_to_restore['active_contracts_data']]
                        purchase_history = deepcopy(snapshot_to_restore['purchase_history_snapshot'])
                        deposits_history = deepcopy(snapshot_to_restore['deposits_history_snapshot'])
                        contract_types_purchased_today = deepcopy(snapshot_to_restore['contract_types_purchased_today_snapshot'])
                        
                        daily_state_history = daily_state_history[:actual_idx] 

                        print(f"  {Colors.SUCCESS}✅ Rolled back to the beginning of {current_date.strftime('%Y-%m-%d')}.{Colors.RESET}")
                        _last_processed_date_for_daily_flags = None 
                        break 
                    else:
                        print(f"  {Colors.ERROR}Invalid selection for rollback.{Colors.RESET}")
                except (ValueError, IndexError):
                    print(f"  {Colors.ERROR}Invalid input for rollback selection.{Colors.RESET}")

            elif choice == 'save':
                save_path_to_use = current_save_filepath 
                if not save_path_to_use: 
                    new_s_name = get_validated_input("Enter filename for this new save (e.g., my_sim_autosave): ", str)
                    if new_s_name: save_path_to_use = os.path.join(prog_config['default_save_folder_path'], new_s_name + SAVE_GAME_EXTENSION)
                    else: print(f"{Colors.INFO}Save cancelled (no filename).{Colors.RESET}"); continue 
                
                current_state_snapshot = {
                    'current_date': current_date, 'current_profit': current_profit,
                    'active_contracts': active_contracts, 'purchase_history': purchase_history,
                    'deposits_history': deposits_history, 'game_settings': current_game_settings
                }
                save_game_state(current_state_snapshot, save_path_to_use)
                if not current_save_filepath : current_save_filepath = save_path_to_use 
            elif choice == 'load':
                if input(f"{Colors.WARNING}Loading will discard unsaved progress. Continue? (y/n): {Colors.RESET}{Colors.INPUT_FIELD}").lower()=='y':
                    print(Colors.RESET, end="")
                    selected_fpath = list_and_select_save_file(prog_config['default_save_folder_path'])
                    if selected_fpath:
                        loaded_s = load_game_state(selected_fpath)
                        if loaded_s: return loaded_s, selected_fpath 
                else: print(f"{Colors.INFO}Load cancelled.{Colors.RESET}")
            elif choice == 'm': 
                if input(f"{Colors.WARNING}Return to Main Menu? Unsaved progress will be lost. (y/n): {Colors.RESET}{Colors.INPUT_FIELD}").lower()=='y':
                    print(Colors.RESET, end="")
                    return 'main_menu', None 
            elif choice == 'q': 
                if input(f"{Colors.WARNING}Quit program? Unsaved progress will be lost. (y/n): {Colors.RESET}{Colors.INPUT_FIELD}").lower()=='y':
                    print(Colors.RESET, end="")
                    return None, None 
            elif choice in ('n', ''): 
                current_date += datetime.timedelta(days=1)
                break 
            else: 
                print(f"  {Colors.ERROR}Invalid choice.{Colors.RESET}")
        # End of inner action loop
    # End of outer per-day loop 
    
    return {'current_date': current_date, 'current_profit': current_profit,
            'active_contracts': active_contracts, 'purchase_history': purchase_history,
            'deposits_history': deposits_history, 'game_settings': current_game_settings}, current_save_filepath

# --- PROGRAM ENTRY POINT ---
if __name__ == '__main__':
    program_config = load_program_config() 
    active_game_session_state = None
    current_session_save_filepath = None 

    while True: 
        if active_game_session_state is None: 
            print(f"\n{Colors.HEADER}" + "="*30 + " MAIN MENU " + "="*30 + f"{Colors.RESET}")
            print(f"{Colors.OPTION}[1]{Colors.OPTION_TEXT} New Game{Colors.RESET}")
            print(f"{Colors.OPTION}[2]{Colors.OPTION_TEXT} Load Game{Colors.RESET}")
            print(f"{Colors.OPTION}[3]{Colors.OPTION_TEXT} Program Configuration (Defaults & Save Path){Colors.RESET}")
            print(f"{Colors.OPTION}[4]{Colors.OPTION_TEXT} Quit Program{Colors.RESET}")
            menu_choice = input(f"{Colors.PROMPT}Choice: {Colors.RESET}{Colors.INPUT_FIELD}").lower().strip()
            print(Colors.RESET, end="")


            if menu_choice == '1':
                print(f"\n{Colors.SUBHEADER}--- Starting New Game Setup ---{Colors.RESET}")
                default_gs_data = program_config['default_game_setup']
                initial_game_settings_obj = {
                    "contract_templates": [MiningContract(**data) for data in default_gs_data['contract_templates_data']],
                    "initial_profit": default_gs_data['initial_profit'],
                    "start_date": datetime.date.fromisoformat(default_gs_data['start_date_str']),
                    "held_contracts": [MiningContract(**data) for data in default_gs_data['held_contracts_data']],
                    "auto_purchase_forecast": default_gs_data['auto_purchase_forecast']
                }
                customized_game_settings = manage_game_settings(initial_game_settings_obj, is_initial_setup=True, context_info="New Game Configuration")
                
                if customized_game_settings: 
                    new_game_filename_base = get_validated_input("Enter a name for your new game save file (e.g., my_first_sim): ", str)
                    if new_game_filename_base:
                        current_session_save_filepath = os.path.join(program_config['default_save_folder_path'], new_game_filename_base + SAVE_GAME_EXTENSION)
                        active_game_session_state = {
                            'current_date': customized_game_settings['start_date'],
                            'current_profit': customized_game_settings['initial_profit'],
                            'active_contracts': deepcopy(customized_game_settings['held_contracts']), 
                            'purchase_history': [], 'deposits_history': [],
                            'game_settings': customized_game_settings 
                        }
                        for hc in active_game_session_state['active_contracts']:
                             active_game_session_state['purchase_history'].append({
                                "date": hc.start_date.strftime('%Y-%m-%d') if hc.start_date else "N/A",
                                "name": hc.name, "cost": hc.cost, "id": hc.id, "type": "Pre-held"
                            })
                        save_game_state(active_game_session_state, current_session_save_filepath) 
                    else: print(f"{Colors.INFO}New game cancelled (no filename).{Colors.RESET}")
                else: print(f"{Colors.INFO}New game setup cancelled.{Colors.RESET}")
            
            elif menu_choice == '2':
                selected_filepath = list_and_select_save_file(program_config['default_save_folder_path'])
                if selected_filepath:
                    loaded_state = load_game_state(selected_filepath)
                    if loaded_state:
                        active_game_session_state = loaded_state
                        current_session_save_filepath = selected_filepath 
            
            elif menu_choice == '3':
                manage_program_overall_settings(program_config) 
            
            elif menu_choice == '4':
                print(f"{Colors.INFO}Exiting program.{Colors.RESET}"); break 
            else:
                print(f"  {Colors.ERROR}Invalid menu choice.{Colors.RESET}")
        
        if active_game_session_state:
            sim_result_tuple = run_simulation_loop(active_game_session_state, current_session_save_filepath, program_config)
            
            sim_result_state = sim_result_tuple[0]
            new_save_path_from_sim = sim_result_tuple[1]

            if sim_result_state is None: break 
            elif sim_result_state == 'main_menu': 
                active_game_session_state = None 
                current_session_save_filepath = None
            else: 
                active_game_session_state = sim_result_state
                current_session_save_filepath = new_save_path_from_sim 

    save_program_config(program_config) 
    print(f"{Colors.INFO}Program terminated.{Colors.RESET}")
