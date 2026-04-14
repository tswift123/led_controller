#---------------------------------------------------
#--- ConfigObj
#--- This class implements an object to hold the 
#--- configuration of the LED controller.  It will be
#--- updated whenever the user make a change to an 
#--- attribute of the controlller like the name or
#--- type of a controller.  When a phone app first connects
#--- to the LED controller box, it will call for this
#--- configuration so that it can be updated if a different
#--- phone app made a change to the configuration.  This
#--- object will package the attributes into a json string
#--- and return it to the caller.
#---------------------------------------------------
import ujson as json


class ConfigObj:

    controller1: dict = {"Name": "Ctrl1", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
    controller2: dict = {"Name": "Ctrl2", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
    controller3: dict = {"Name": "Ctrl3", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
    controller4: dict = {"Name": "Ctrl4", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}

    
    scene1: dict = {"Name": "Scene1", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }
    
    scene2: dict = {"Name": "Scene2", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }
    
    scene3: dict = {"Name": "Scene3", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }
    
    scene4: dict = {"Name": "Scene4", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }
    
    scene5: dict = {"Name": "Scene5", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }
    
    scene6: dict = {"Name": "Scene6", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }
    
    scene7: dict = {"Name": "Scene7", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }
    
    scene8: dict = {"Name": "Scene8", 
              "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
              "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
            }

    #--- Only 4 scenes for now until the UI is adapted to handle more than 4 scenes.  The config file will
    allScenes: dict = {
        "1": scene1,
        "2": scene2,
        "3": scene3,
        "4": scene4,
#        "5": scene5,
#        "6": scene6,
#        "7": scene7,
#        "8": scene8
    }

    config_dict: dict = {
        "1": controller1,
        "2": controller2,
        "3": controller3,
        "4": controller4,
        "Scenes": allScenes
    }


    def __init__(self):
        self.read_config()
#        print("Init Config Obj")


    def __post_init__(self):
        pass
#        if not isinstance(self.age, int) or self.age < 0:
#            raise ValueError("age must be a non-negative integer")

    #----------------------------------------------
    #--- set_rgbw_values_and_brightness
    #--- Copy the RGBW values for a scene into the 
    #--- local config dict and write to file.
    #--- Both sceneNum and aName must be strings.
    #----------------------------------------------
    def set_rgbw_values_and_brightness(self, sceneID, sceneName, valueDict, brightnessDict):
        self.allScenes[sceneID]["Name"] = sceneName
        self.allScenes[sceneID]["RGBWValues"] = valueDict.copy()
        self.allScenes[sceneID]["Brightness"] = brightnessDict.copy()

        # self.cfg_rgbw_values["1R"] = valueDict["1R"]
        # self.cfg_rgbw_values["1G"] = valueDict["1G"]
        # self.cfg_rgbw_values["1B"] = valueDict["1B"]
        # self.cfg_rgbw_values["1W"] = valueDict["1W"]
        # self.cfg_rgbw_values["2R"] = valueDict["2R"]
        # self.cfg_rgbw_values["2G"] = valueDict["2G"]
        # self.cfg_rgbw_values["2B"] = valueDict["2B"]
        # self.cfg_rgbw_values["2W"] = valueDict["2W"]
        # self.cfg_rgbw_values["3R"] = valueDict["3R"]
        # self.cfg_rgbw_values["3G"] = valueDict["3G"]
        # self.cfg_rgbw_values["3B"] = valueDict["3B"]
        # self.cfg_rgbw_values["3W"] = valueDict["3W"]
        # self.cfg_rgbw_values["4R"] = valueDict["4R"]
        # self.cfg_rgbw_values["4G"] = valueDict["4G"]
        # self.cfg_rgbw_values["4B"] = valueDict["4B"]
        # self.cfg_rgbw_values["4W"] = valueDict["4W"]

        # self.cfg_brightness["1R"] = brightnessDict["1R"]
        # self.cfg_brightness["1G"] = brightnessDict["1G"]
        # self.cfg_brightness["1B"] = brightnessDict["1B"]
        # self.cfg_brightness["1W"] = brightnessDict["1W"]
        # self.cfg_brightness["2R"] = brightnessDict["2R"]
        # self.cfg_brightness["2G"] = brightnessDict["2G"]
        # self.cfg_brightness["2B"] = brightnessDict["2B"]
        # self.cfg_brightness["2W"] = brightnessDict["2W"]
        # self.cfg_brightness["3R"] = brightnessDict["3R"]
        # self.cfg_brightness["3G"] = brightnessDict["3G"]
        # self.cfg_brightness["3B"] = brightnessDict["3B"]
        # self.cfg_brightness["3W"] = brightnessDict["3W"]
        # self.cfg_brightness["4R"] = brightnessDict["4R"]
        # self.cfg_brightness["4G"] = brightnessDict["4G"]
        # self.cfg_brightness["4B"] = brightnessDict["4B"]
        # self.cfg_brightness["4W"] = brightnessDict["4W"]

        self.write_to_file()


    #----------------------------------------------
    #--- set_scene_name
    #--- Both sceneNum and aName must be strings.
    #----------------------------------------------
    def set_scene_name(self, sceneNum, aName):
        self.allScenes[sceneNum]["Name"] = aName
        self.write_to_file()


    #----------------------------------------------
    #--- set_ctrl_name
    #--- Both ctrlNum and aName must be strings.
    #----------------------------------------------
    def set_ctrl_name(self, ctrlNum, aName):
        self.config_dict[ctrlNum]["Name"] = aName
        self.write_to_file()


    #----------------------------------------------
    #--- set_ctrl_type
    #--- Both ctrlNum and aType must be strings.
    #----------------------------------------------
    def set_ctrl_type(self, ctrlNum, aType):
        self.config_dict[ctrlNum]["Type"] = aType
#        print("Setting Ctrl Type: ", aType)
        self.write_to_file()


    #----------------------------------------------
    #--- set_channel_name
    #--- All of ctrlNum, chanNum and aName must be 
    #--- strings. chanNUm must be one of "R", "G",
    #--- "B", or "W".
    #----------------------------------------------
    def set_channel_name(self, ctrlNum, chanNum, aName):
        self.config_dict[ctrlNum]["ChanNames"][chanNum] = aName
        self.write_to_file()


    #----------------------------------------------
    #--- get_ctrl_type
    #--- Both ctrlNum and aType must be strings.
    #--- ctrlNum must be a value from 1 to 4
    #----------------------------------------------
    def get_ctrl_type(self, ctrlNum) -> str:
        return self.config_dict[ctrlNum]["Type"]

    
    #----------------------------------------------
    #--- write_to_file
    #--- Both ctrlNum and aType must be strings.
    #----------------------------------------------
    def write_to_file(self):

        config_file_path = "config.json"
        jsonStr = self.to_json()

        try:
            with open(config_file_path, "w") as file:
                json.dump(self.config_dict, file)

        except OSError:
            #--- Failed to open file for write
            print("Failed to open config file for write")
        finally:
            if 'file' in locals():
                file.close()


    #----------------------------------------------------------------
    #--- read_config
    #--- Read the names and config settings from the config file (if
    #--- it exists) and load them into the main config dictionary of
    #--- this object. If the file doesn't exist, load the dictionary 
    #--- with default data.
    #---
    #----------------------------------------------------------------
    def read_config(self):

        config_file_path = "config.json"

        filePath = config_file_path
        try:
            with open(filePath, "r") as file:
                self.config_dict = json.load(file)

        except OSError:
            #--- Failed to open file for read so no
            #--- config data has been saved. Create
            #--- default data to return.
    #        print("Failed to open config file for write")
            self.default_config_data()
        finally:
            if 'file' in locals():
                file.close()

    

    #----------------------------------------------------------------
    #--- default_config_data
    #--- Set default values into the main config structure
    #--- of this object.
    #---
    #----------------------------------------------------------------
    def default_config_data(self):

        self.controller1 = {"Name": "Ctrl1", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
        self.controller2 = {"Name": "Ctrl2", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
        self.controller3 = {"Name": "Ctrl3", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
        self.controller4 = {"Name": "Ctrl4", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
        self.controller1["Name"] = "Ctrl1"        
        self.controller2["Name"] = "Ctrl2"        
        self.controller3["Name"] = "Ctrl3"        
        self.controller4["Name"] = "Ctrl4"        
        self.controller1["Type"] = "RGBW"         
        self.controller2["Type"] = "RGBW"         
        self.controller3["Type"] = "RGBW"         
        self.controller4["Type"] = "RGBW"
        self.controller1["ChanNames"]["R"] = "R"
        self.controller1["ChanNames"]["G"] = "G"
        self.controller1["ChanNames"]["B"] = "B"
        self.controller1["ChanNames"]["W"] = "W"
        self.controller2["ChanNames"]["R"] = "R"
        self.controller2["ChanNames"]["G"] = "G"
        self.controller2["ChanNames"]["B"] = "B"
        self.controller2["ChanNames"]["W"] = "W"
        self.controller3["ChanNames"]["R"] = "R"
        self.controller3["ChanNames"]["G"] = "G"
        self.controller3["ChanNames"]["B"] = "B"
        self.controller3["ChanNames"]["W"] = "W"
        self.controller4["ChanNames"]["R"] = "R"
        self.controller4["ChanNames"]["G"] = "G"
        self.controller4["ChanNames"]["B"] = "B"
        self.controller4["ChanNames"]["W"] = "W"

        self.scene1 = {"Name": "Scene1", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }
        
        self.scene2 = {"Name": "Scene2", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }
        
        self.scene3 = {"Name": "Scene3", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }
        
        self.scene4 = {"Name": "Scene4", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }
        
        self.scene5 = {"Name": "Scene5", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }
        
        self.scene6 = {"Name": "Scene6", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }
        
        self.scene7 = {"Name": "Scene7", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }
        
        self.scene8 = {"Name": "Scene8", 
                "RGBWValues": {"1R": 0, "1G": 0, "1B": 0, "1W": 0, "2R": 0, "2G": 0, "2B": 0, "2W": 0, "3R": 0, "3G": 0, "3B": 0, "3W": 0, "4R": 0, "4G": 0, "4B": 0, "4W": 0},
                "Brightness": {"1R": 100, "1G": 100, "1B": 100, "1W": 100, "2R": 100, "2G": 100, "2B": 100, "2W": 100, "3R": 100, "3G": 100, "3B": 100, "3W": 100, "4R": 100, "4G": 100, "4B": 100, "4W": 100}
                }

 #       print("Default config data: ", self.config_dict)


    #----------------------------------------------
    #--- to_json
    #--- Dump the configuration dictionary to json
    #--- and return the json string.
    #----------------------------------------------
    def to_json(self) -> str:
        return json.dumps(self.config_dict)


    