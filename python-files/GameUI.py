# ---------------------------------------------------------------------------
# imports all exterior files and libarys that will be used within the program 
# ---------------------------------------------------------------------------

import customtkinter
import tkinter 
import os
import re 
import keyword 

# -----------------------------------------------------------------------------
# perminently sets the apperance of the custom tkinter window to the dark state
# -----------------------------------------------------------------------------

customtkinter.set_appearance_mode("Dark")

# -------------------------------------------------------
# creates the class in which all the functions will occur
# -------------------------------------------------------

class GraphicsInterface(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # ---------------------------------------------------------------
        # sets up varilbes to store the different fonts that will be used
        # ---------------------------------------------------------------

        self.Font30 = customtkinter.CTkFont("arial", 30)
        self.Font40 = customtkinter.CTkFont("arial", 40)
        
        # ----------------------------------
        # stores all other required varibles
        # ----------------------------------

        self._state_before_windows_set_titlebar_color = 'zoomed'
        self.overrideredirect(1)
        
        # -----------------------------
        # calls the loadscreen function
        # -----------------------------

        self.LoadLoadscreen()

# -----------------------------------------------
# subprograms used within the back of the program
# -----------------------------------------------

    def clearScreen(self, ScreenType):
        # ------------------------------------------------------------------------------------
        # is used to clear all previous widgets of the screen so that the screen can be reused
        # ------------------------------------------------------------------------------------
    
        # -------------------------------------------------------------------------------------
        # checks to see whether the previous window is one of the windows with different layout
        # -------------------------------------------------------------------------------------

        if ScreenType == "LoadLoadscreen":
            # ---------------------------------------
            # deletes all widgets form the loadscreen
            # ---------------------------------------

            self.HackLab.destroy()
            self.GameRun.destroy()

        else:
            # --------------------------------------------
            # removes the widgets from the reusable frames
            # --------------------------------------------

            for widget in self.InformationFrame.winfo_children():

                widget.destroy()

            for widget in self.SelectorFrame.winfo_children():

                widget.destroy()

    def LoadDescriptions(self, Game):
        # --------------------------------------------------------------------------------------
        # loads the game descriptions so that the players can understand what each game involves
        # --------------------------------------------------------------------------------------

        DescriptionFile = Game
        
        # ----------------------------------------------------------------------------------------
        # checks to make sure that the inputed file name has the correct file type attatched to it 
        # ----------------------------------------------------------------------------------------

        if not DescriptionFile.endswith('.txt'):
            DescriptionFile = DescriptionFile + '.txt'
        
        # -----------------------------------------------------------
        # creates the complete path allowing for better file mangment 
        # -----------------------------------------------------------

        fullPath = os.path.join("C:\\Users\\cakeb\\OneDrive\\Documents\\coursework GUI\\Descriptions" , DescriptionFile)      

        if os.path.exists(fullPath):
            
            # ---------------------------------------------------------------------------------
            # uses encoding "UTF-8" as it allows for the use of characters such as appostrapies
            # ---------------------------------------------------------------------------------

           with open(fullPath, 'r', encoding = 'utf-8') as file:

            self.textbox.tag_config("font1", cnf = {"font": self.Font40})
            self.textbox.configure(state = 'normal')

            self.textbox.delete("0.0", "end")
            self.textbox.insert("5.0", file.read(), 'font1')
            
            # ---------------------------------------------------------------------------------------------------------------
            # the state is set to disabled so that the descriptions cannot be edited, creating a more proffessional apperance
            # ---------------------------------------------------------------------------------------------------------------

            self.textbox.configure(state = 'disabled')

    def LoadExsampleCodes(self, Question):
         
        ExsampleFile = Question

        if not ExsampleFile.endswith('.txt'):
            ExsampleFile = ExsampleFile + '.txt'
        
        fullPath = os.path.join("C:\\Users\\cakeb\\OneDrive\\Documents\\coursework GUI\\CodeExsamples" , ExsampleFile)      

        if os.path.exists(fullPath):
           
           # ------------------------------------------------------------------------------
           # uses encoding "UTF-8" as it allows the use of special characters like hasstags
           # ------------------------------------------------------------------------------
           
           with open(fullPath, 'r', encoding= 'utf-8') as file:

            self.textbox.tag_config("font1", cnf = {"font": self.Font40})
            
            # ---------------------------------------------------------------------------------------
            # state is left as normal so that the code can be edited and used like normal code editor
            # ---------------------------------------------------------------------------------------

            self.textbox.configure(state = 'normal')

            self.textbox.delete("0.0", "end")
            self.textbox.insert("5.0", file.read(), 'font1')

    def Return(self, clearScreenfunc):
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        # this function uses a simple call to the main menu as a return button due to the fact that you cannot get more than one screen away from the main menu 
        # -----------------------------------------------------------------------------------------------------------------------------------------------------

        self.Loadmainscreen(clearScreenfunc)

    def CodeHighlighter(self): #need to add functionality
        pass

    def Play(self):
        self.clearScreen("LoadMainscreen")

        self.SelectorFrame.configure(width = 500)
        
        self.textbox = customtkinter.CTkTextbox(self.SelectorFrame, width = 480, height = 580)
        self.textbox.grid(row = 1, column = 1, padx = 5, pady = 5)
        self.textbox.configure(wrap = 'word')
       
# ----------------------------------------------------------------
# subprograms used to create the front for the graphical interface 
# ----------------------------------------------------------------

    def LoadLoadscreen(self):
        # ------------------------------------------------------------   
        # creates the loadscreen by adding a game tile and play button
        # ------------------------------------------------------------
        
        self.HackLab = customtkinter.CTkLabel(self, text = "HACKLAB", font = ("roman", 250, "bold"), text_color = "#0072FC" )
        self.HackLab.place(relx = 0.5, rely = 0.4, anchor = tkinter.CENTER)
        
        # -----------------------------------------------------------------------
        # tkinter is used to anchor (fix) the widgets to the centre of the screen
        # -----------------------------------------------------------------------

        self.GameRun = customtkinter.CTkButton( self, text = "PLAY", font = ("arial", 30, "bold"), text_color = '#FFFFFF', command = lambda : (self.Loadmainscreen("LoadLoadscreen")))
        self.GameRun.place(relx = 0.5, rely = 0.65, anchor = tkinter.CENTER)

    def Loadmainscreen(self, clearScreenFunc):
        # --------------------------------------------------------------------------------------------
        # uses the pre-defined function clearScreen to remove the priovius widgets from the loadscreen 
        # --------------------------------------------------------------------------------------------

        self.clearScreen(clearScreenFunc)

        # ----------------------------------------------------------------------------------
        # configures the frmae by setting conditions for different parts of the frame itself
        # ----------------------------------------------------------------------------------

        self.grid_columnconfigure((1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # ------------------------------------------------------------------------------------------------------------------------------------
        # creates the new frames into which the needed information can be added [these frames will be repeated throught all the other screens]
        # ------------------------------------------------------------------------------------------------------------------------------------

        self.InformationFrame = customtkinter.CTkFrame(self, width = 900, height = 600)
        self.InformationFrame.grid(row = 0 , column = 1, padx = 10, pady =10, sticky = "nsew")

        self.SelectorFrame = customtkinter.CTkFrame(self, width = 200, height = 600)
        self.SelectorFrame.grid(row = 0 , column = 0, padx = 10, pady =10, sticky = "nsew")

        self.SelectorFrame.grid_rowconfigure(4, weight=1)

        self.textbox = customtkinter.CTkTextbox(self.InformationFrame, width=850, height=500)
        self.textbox.grid(row = 0, column = 4, padx = 20, pady = 10)
        self.textbox.configure(wrap = 'word', state = 'disabled')

        self.playButton = customtkinter.CTkButton(self.textbox, text="PLAY", command = lambda: self.Play())
        self.playButton.grid(row = 2, column = 0, padx =10, pady = 10)
        
        # ------------------------------------------------------------------------------------------------------------------
        # itterates through creating the game buttons, using lists meaning that new games can be added and therefore created 
        # ------------------------------------------------------------------------------------------------------------------

        games = ["TETRIS", "SURVIVAL_ISLAND_II", "ALIEN", "FLAPPY_BIRD_II"]
        optionButtons = ["SETTINGS", "DEVELOPMENT MODE"]

        for G in range(len(games)):
            name = games[G]

            self.Gamebutton = customtkinter.CTkButton(self.SelectorFrame, text = name, command = lambda name = name : self.LoadDescriptions(name))
            self.Gamebutton.grid(row = G, column = 0, padx = 10, pady = 10)
        
        # ----------------------------------------------------------------------------------
        # creates the other buttons that are unable to be created due to there command calls
        # ----------------------------------------------------------------------------------

        self.SettingsSelector = customtkinter.CTkButton(self.SelectorFrame, text = optionButtons[0],  command = lambda: self.loadSettings()) 
        self.SettingsSelector.grid(row = 10, column = 0, padx = 10, pady = 10)

        self.DevModeSelector = customtkinter.CTkButton(self.SelectorFrame, text = optionButtons[1], command = lambda: self.LoadDevelopmentMode()) 
        self.DevModeSelector.grid(row = 9, column = 0, padx = 10, pady = 10)

    def LoadDevelopmentMode(self):
        # -------------------------------------------------------------------------------------------------
        # uses the pre-defined function clearScreen to remove the priovius widgets from the called location 
        # -------------------------------------------------------------------------------------------------
        self.clearScreen("LoadDevelopmentMode")

        self.textbox = customtkinter.CTkTextbox(self.InformationFrame, width = 850, height = 550)
        self.textbox.grid(row = 0, column = 0, padx = 10, pady = 10)
        self.textbox.configure(state = "normal", wrap = "word")
        
        self.SelectorFrame.grid_rowconfigure(4, weight=1)
        
        # ------------------------------------------------------------------------------------------------------------------
        # itterates through creating the code buttons, using lists meaning that new codes can be added and therefore created 
        # ------------------------------------------------------------------------------------------------------------------

        Exsamples = ["QUESTION_1", "QUESTION_3", "QUESTION_5", "CHALLENGE_QUESTION"]
        ROW = [0, 1, 2, 3]
  
        for E in range(len(Exsamples)):
            self.button = customtkinter.CTkButton(self.SelectorFrame, text = Exsamples[E], command=lambda E = E: self.LoadExsampleCodes(Exsamples[E]))
            self.button.grid(row = ROW[E], column = 0, padx = 10, pady = 10)
        
         # ----------------------------------------------------------------------------------
        # creates the other buttons that are unable to be created due to there command calls
        # ----------------------------------------------------------------------------------

        self.ReturnButton = customtkinter.CTkButton(self.SelectorFrame, text="RETURN", command = lambda: self.Return("LoadDevelopmentMode"))
        self.ReturnButton.grid(row = 10, column = 0, padx = 10, pady = 10)

        self.Savebutton = customtkinter.CTkButton(self.SelectorFrame, text = "SAVE", command = lambda : self.Save())
        self.Savebutton.grid(row = 9, column = 0, padx = 10, pady = 10)

    def loadSettings(self):
        self.settingWindow = SettingsWindow()

class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("settings")
        self.geometry("540x400")

        self.attributes("-topmost", True)
        self.Font25 = customtkinter.CTkFont("arial", 25)
        
        self.LoadSettings()
        
    def clearScreen(self):
        # ---------------------------------------------------
        # removes the widgets from the settings window screen 
        # ---------------------------------------------------

        for widget in self.leftframe.winfo_children():
            
            widget.destroy()

    def LoadSettings(self): ### need to look at how the buttons are created 
        self.grid_columnconfigure((1,3), weight = 1)
        self.grid_rowconfigure((1,5), weight = 1)

        self.leftframe = customtkinter.CTkFrame(self, width = 520, height = 380)
        self.leftframe.grid(row = 0, column = 0, padx = 10, pady = 10)
        self.leftframe.grid_propagate(False)

        #Settingbuttons = ["MUTE", "HOW TO PLAY", "LOAD GAME", "SAVE"]
        #ROW = [1,2,3,10]
        #COLUMN = [4,4,4,1]

        #for S in range(len(Settingbuttons)):
            #name = Settingbuttons[S]

            #SettingNames[S] = customtkinter.CTkButton(self.leftframe, text = name, command = commands[S])
            #SettingNames[S].grid(row = ROW[S], column = COLUMN[S], padx = 5, pady = 5)
        self.mute = customtkinter.CTkButton(self.leftframe, text = "MUTE", command = lambda : self.Mute())
        self.mute.grid(row = 1, column = 4, padx = 5, pady = 5)

        self.save = customtkinter.CTkButton(self.leftframe, text = "SAVE", command = lambda : self.Save())
        self.save.grid(row = 10, column = 1, padx = 5, pady = 5)

        self.addNewGame = customtkinter.CTkButton(self.leftframe, text = "LOAD GAME", command = lambda : self.AddNewGame())
        self.addNewGame.grid(row = 2, column = 4, padx = 5, pady = 5)

        self.howToPlay = customtkinter.CTkButton(self.leftframe, text = "HOW TO PLAY", command = lambda : self.HowToPlay())
        self.howToPlay.grid(row = 3, column = 4, padx = 5, pady = 5)


        self.volumeSlider = customtkinter.CTkSlider(self.leftframe, width = 340, from_=0, to = 100)
        self.volumeSlider.grid(row = 1, columnspan = 3, column = 1, padx = 10, pady = 10)

        Music = ["50 Over The Speed Limit", "Back In The 80's", "Caught In The Middle", "Day Dream", "Dear Mr Super Computer", "Horizon", "Volcano", "Walk Around"]
        MUSICROW = [2,3,4,5,6,7,8,9]
        
        for M in range(len(Music)):
            name = Music[M]

            self.MusicBox = customtkinter.CTkCheckBox(self.leftframe, text = name)
            self.MusicBox.grid(row = MUSICROW[M], column = 1 , columnspan = 2, sticky = "w", padx = 10, pady = 5)

    def AddNewGame(self): ### need to add titles for each entry / prevnet widget collapese / potentaly all for selection of files from outside the direct folder area 
        # -----------------------------------------
        # clears the screen of all previous widgets 
        # -----------------------------------------

        self.clearScreen()
        
        #
        #
        #

        self.NameTitle = customtkinter.CTkLabel(self.leftframe, text = "ADD GAME NAME")
        self.NameTitle.grid(row = 1, column = 1, columnspan = 3, padx = 60, pady = 10, sticky = 'nsew')

        self.NameBox = customtkinter.CTkEntry(self.leftframe, placeholder_text = "GAME NAME")
        self.NameBox.grid(row = 2, column = 1, columnspan = 3, padx = 60, pady = 10, sticky = "nsew" )
        
        self.DescriptionsTitle = customtkinter.CTkLabel(self.leftframe, text = "ADD GAME DESCRIPTION LOCATION")
        self.DescriptionsTitle.grid(row = 3, column = 1, columnspan = 3, padx = 60, pady = 10, sticky = 'nsew')

        self.DescriptionBox = customtkinter.CTkEntry(self.leftframe, placeholder_text = "DESCRIPTION FILE ADDRESS")
        self.DescriptionBox.grid(row = 4, column = 1, columnspan = 3, padx = 60, pady = 10, sticky = "nsew")
        
        self.CodeTitle = customtkinter.CTkLabel(self.leftframe, text = "ADD GAME CODE LOCATION")
        self.CodeTitle.grid(row = 5, column = 1, columnspan = 3, padx = 60, pady = 10, sticky = 'nsew')

        self.CodeBox = customtkinter.CTkEntry(self.leftframe, placeholder_text = "CODE FILE ADDRESS")
        self.CodeBox.grid(row = 6, column = 1, columnspan = 3, padx = 60, pady = 10, sticky = "nsew")
        
        self.save = customtkinter.CTkButton(self.leftframe, text = "SAVE")
        self.save.grid(row = 7, column = 1, columnspan = 3, padx = 60, pady = 10)
        
        row = [6,4]

        for i in range(2):
            self.browse = customtkinter.CTkButton(self.leftframe, text = "BROWSE")
            self.browse.grid(row = row[i] , column = 4, padx = 0, pady = 10)

    def HowToPlay(self):
        # -------------------------------------
        # clears the screen of previous widgets
        # -------------------------------------

        self.clearScreen()

        # -----------------------------------
        # creates the textbox and back button
        # -----------------------------------

        self.textbox = customtkinter.CTkTextbox(self, width = 520, height = 380)
        self.textbox.grid(row = 0, column = 0, padx = 10, pady = 10)

        self.Return = customtkinter.CTkButton(self, command = lambda: self.AddNewGame())
        self.Return.grid(row = 1, column = 0, padx = 10 , pady = 10  )
        

        Location = "C:\\Users\\cakeb\\OneDrive\\Documents\\coursework GUI\\HowToPlay.txt"      

        if os.path.exists(Location):
            
            # ---------------------------------------------------------------------------------
            # uses encoding "UTF-8" as it allows for the use of characters such as appostrapies
            # ---------------------------------------------------------------------------------

           with open(Location, 'r', encoding = 'utf-8') as file:

            self.textbox.tag_config("font1", cnf = {"font": self.Font25})
            self.textbox.configure(state = 'normal', wrap = 'word')

            self.textbox.delete("0.0", "end")
            self.textbox.insert("5.0", file.read(), 'font1')
            
            # ---------------------------------------------------------------------------------------------------------------
            # the state is set to disabled so that the Textbox cannot be edited, creating a more proffessional apperance
            # ---------------------------------------------------------------------------------------------------------------

            self.textbox.configure(state = 'disabled')

    def Mute(self): ### add functnality 
        pass

    def Save(self): # add functionality 
        pass

# --------------------------------------------------------------------------------
# creates an instance of the application using custotkinter and then runs the code 
# --------------------------------------------------------------------------------

if __name__ == '__main__':
    app = GraphicsInterface()
    app.mainloop()   



