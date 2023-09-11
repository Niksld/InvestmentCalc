import requests
import dearpygui.dearpygui as dpg
from os import mkdir, path, getenv, rename
from datetime import datetime
import json

#DPG init
dpg.create_context()
viewport_title = "Investment calculator"
dpg.create_viewport(title=viewport_title, width=800, height=400)

#DPG Theme - WIP, mozna i light mode?
with dpg.theme() as default_theme:
    with dpg.theme_component(dpg.mvAll):
        #dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (14,10,12), category=dpg.mvThemeCat_Core)
        pass
    
dpg.bind_theme(default_theme)
    
#DPG Font - WIP
with dpg.font_registry():
    with dpg.font(path.relpath("fonts/OpenSans-Regular.ttf"), 16) as opensans_regular:
        dpg.add_font_range(0x0100, 0x25FF) # CZ Fix
    with dpg.font(path.relpath("fonts/OpenSans-Italic.ttf"), 16) as opensans_regular_i:
        dpg.add_font_range(0x0100, 0x25FF)
    with dpg.font(path.relpath("fonts/OpenSans-Light.ttf"), 16) as opensans_light:
        dpg.add_font_range(0x0100, 0x25FF)
    with dpg.font(path.relpath("fonts/OpenSans-LightItalic.ttf"), 16) as opensans_light_i:
        dpg.add_font_range(0x0100, 0x25FF)
        
#Vars
appdata_path = getenv('appdata')
savefile_path = f'{appdata_path}/InvestmentCalc/save.file'
savefile_exists = False

items_to_save = {}

czk_rate = 0
last_rate_update = None

# get exchange rates
def get_exchange_rate():
    url = 'https://v6.exchangerate-api.com/v6/372620cbf549ea6f6928b902/latest/USD'
    response = requests.get(url)
    return response.json()["conversion_rates"]["CZK"]

def update_exchange_rate():
    global czk_rate, last_rate_update
    czk_rate = get_exchange_rate()
    dpg.set_value("exchange_rate", czk_rate)
    last_rate_update = datetime.now()
    dpg.set_value("last_rate_update_text", last_rate_update.strftime('%H:%M:%S - %d.%m.%Y'))

# Save details
def save():
    global items_to_save, savefile_path
    
    items_with_values = items_to_save
    # create json file
    for key in items_with_values.keys():
        items_with_values[key] = dpg.get_value(items_with_values[key])
    json_file = json.dumps(items_with_values, indent=4)
    with open(savefile_path, mode='w', encoding='utf-8') as file:
        file.write(json_file)
    print("File saved!")
    #dpg.configure_viewport(label=f"{viewport_title} - Saved")
    
# Load saved details.
def load():
    global items_to_save, appdata_path, savefile_path
    
    loaded_json = None
    with open(savefile_path, mode='r', encoding='utf-8') as file:
        loaded_json = json.load(file)
    try:
        for key in items_to_save.keys():
            print(items_to_save[key], loaded_json[key])
            dpg.set_value(key, loaded_json[key])
    except KeyError:
        print("Loading failed! - Savefile out of date?")
        rename(savefile_path,f'{appdata_path}/InvestmentCalc/save.old')    
    print("File Loaded!")
    #dpg.configure_viewport(label=f"{viewport_title} - Last save")

def check_savefile():
    global savefile_exists, appdata_path, savefile_path
    
    if path.exists(savefile_path):
        load()
        savefile_exists = True
    else:
        if not path.exists(f'{appdata_path}/InvestmentCalc/'):
            mkdir(f'{appdata_path}/InvestmentCalc/')
        #dpg.configure_viewport("title", f"{dpg.get_viewport_title} - No save loaded")

def details_saved():
    global savefile_path, items_to_save
    
    loaded_json = None
    with open(savefile_path, mode='r', encoding='utf-8') as file:
        loaded_json = json.load(file)
    try:
        for key in items_to_save.keys():
            print(dpg.get_value(key), loaded_json[key])
            if dpg.get_value(key) != loaded_json[key]:
                return False
        return True
    except KeyError:
        print("Check failed! - is the file corrupt?")

def update_vars():
    dpg.set_value("share_price_czk", float(dpg.get_value("exchange_rate"))*float(dpg.get_value("share_price")))
    dpg.set_value("monthly_investment", float(dpg.get_value("annual_investment"))/12)
    dpg.set_value("shares_to_buy", float(dpg.get_value("monthly_investment"))/float(dpg.get_value("share_price_czk")))

def exit_program():
    if not details_saved():
        dpg.show_item("exit_popup")
    else:
        dpg.stop_dearpygui()
    
# Main window
with dpg.window(width=dpg.get_viewport_width(), height=dpg.get_viewport_height(), tag="main_window", no_resize=True, no_title_bar=True, no_move=True, pos=(0,0)):
    # create menubar
    with dpg.menu_bar(parent="main_window", tag="menubar"):
        # File
        dpg.add_menu(label="File", tag="file_menu")
        dpg.add_menu_item(label="Save", parent="file_menu", callback=save)
        dpg.add_menu_item(label="Load", parent="file_menu", callback=load)
        dpg.add_menu_item(label="Update exchange rate", parent="file_menu", callback=update_exchange_rate)
        dpg.add_menu_item(label="Exit", parent="file_menu", callback=exit_program)
        
        dpg.add_menu(label="About", tag="about_menu")
        dpg.add_menu_item(label="Copyright 2023, Matrysoft Inc.", parent="about_menu")
    
    # create window elements
    items_to_save.update({"annual_investment": dpg.add_input_text(decimal=True, tag='annual_investment', hint="Total annual", callback=update_vars, width=100, pos=(10,30), label="Total annual investment [ CZK ]")})
    items_to_save.update({"share_price": dpg.add_input_text(decimal=True, tag='share_price', hint="Share Price", pos=(10,60), label="Current share price [ USD ]", callback=update_vars)})
    dpg.add_input_text(decimal=True, tag='exchange_rate', readonly=True, hint="Current Exchange Rate", label="Current exchange rate [ 1 USD->CZK ]", pos=(10,90))
    dpg.add_input_text(decimal=True, tag='share_price_czk', readonly=True, hint="Share Price [CZK]", label="Share price [ CZK ]", pos=(10,120))
    dpg.add_input_text(decimal=True, tag='monthly_investment', readonly=True, hint="Monthly Investment", label="Monthly investment", pos=(10,150))
    dpg.add_input_text(decimal=True, tag='shares_to_buy', readonly=True, hint="Shares to buy", label="Shares to buy", pos=(10,180))
    with dpg.group(horizontal=True, pos=(10,240)):
        dpg.add_button(label="Save", callback=save)
        dpg.add_button(label="Load", callback=load)
    with dpg.group(pos=(550,300)):
        dpg.add_text("Last exchange rate update:\n")
        dpg.add_separator()
        dpg.add_text("", tag="last_rate_update_text")
        
    dpg.bind_font(opensans_regular)
    
# Exit popup window
with dpg.window(tag="exit_popup", no_title_bar=True, show=False, modal=True):
        dpg.add_text("Are you sure you want to exit?\nYou have unsaved changes.")
        dpg.add_separator()
        with dpg.group(horizontal=True, pos=(8,55)):
            dpg.add_button(label="Save and exit", callback=lambda: (save(), exit_program()))
            dpg.add_button(label="Exit without saving", callback=lambda: (dpg.stop_dearpygui()))
            dpg.add_button(label="Cancel", callback=lambda: (dpg.hide_item("exit_popup")))
        
        dpg.bind_font(opensans_regular)

# Start functions
check_savefile()
update_exchange_rate()
update_vars()

dpg.set_exit_callback(callback=exit_program)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

# # Initialize variables
# total_investment = 0
# share_price = 0

# # Input annual investment (one-time question)
# annual_investment = float(input("Enter the total annual investment amount in CZK : "))

# # Input share price (asked every time)
# share_price = float(input("Enter the current share price: "))
# share_price_czk = share_price * data["conversion_rates"]["CZK"]
# # Calculate monthly investment
# monthly_investment = annual_investment / 12

# # Calculate number of shares to buy
# shares_to_buy = monthly_investment / share_price_czk

# # Display the result
# print("-------------------------------------------")
# print(f"You should buy {shares_to_buy:.3f} shares this month.")
# print("-------------------------------------------")
# print("Price per share in CZK:",share_price_czk)
# print("Monthly investment:",monthly_investment)