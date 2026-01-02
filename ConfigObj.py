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

    controller1 = {"Name": "Ctrl1", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
    controller2 = {"Name": "Ctrl2", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
    controller3 = {"Name": "Ctrl3", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}
    controller4 = {"Name": "Ctrl4", "Type": "RGBW", "ChanNames": {"R": "", "G": "", "B": "", "W": ""}}

    scene_names = {
        "1": "scene1",
        "2": "scene2",
        "3": "scene3",
        "4": "scene4",
    }

    config_dict = {
        "1": controller1,
        "2": controller2,
        "3": controller3,
        "4": controller4,
        "Scenes": scene_names
    }

    def __init__(self):
        pass
#        print("Init Config Obj")


    def __post_init__(self):
        pass
#        if not isinstance(self.age, int) or self.age < 0:
#            raise ValueError("age must be a non-negative integer")

    #----------------------------------------------
    #--- set_scene_name
    #--- Both sceneNum and aName must be strings.
    #----------------------------------------------
    def set_scene_name(self, sceneNum, aName):
        self.scene_names[sceneNum] = aName
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
    #--- Read the names and config settings from the config file and
    #--- load into a json string that will get sent to the phone app.
    #---
    #----------------------------------------------------------------
    def read_config(self) -> str:

        config_file_path = "config.json"

        filePath = config_file_path
        try:
            with open(filePath, "r") as file:
                cfgData = json.load(file)
                self.config_dict = json.loads(cfgData)

        except OSError:
            #--- Failed to open file for read so no
            #--- config data has been saved. Create
            #--- default data to return.
    #        print("Failed to open config file for write")
            cfgData = json.dumps(self.config_dict)
        finally:
            if 'file' in locals():
                file.close()

        return cfgData


    #----------------------------------------------------------------
    #--- default_config_data
    #--- Build a structure of config data with default names.
    #---
    #----------------------------------------------------------------
    def default_config_data(self):

        cfgData = {}

        self.scene_names["1"] = "Scene1"
        self.scene_names["2"] = "Scene2"
        self.scene_names["3"] = "Scene3"
        self.scene_names["4"] = "Scene4"

        self.controller1["1"]["Name"] = "Ctrl1"         # Other attributes set by class
        self.controller2["1"]["Name"] = "Ctrl2"         # Other attributes set by class
        self.controller3["1"]["Name"] = "Ctrl3"         # Other attributes set by class
        self.controller4["1"]["Name"] = "Ctrl4"         # Other attributes set by class

 #       print("Default config data: ", self.config_dict)
        return json.dumps(self.config_dict)


    #----------------------------------------------
    #--- to_json
    #--- Dump the configuration dictionary to json
    #--- and return the json string.
    #----------------------------------------------
    def to_json(self) -> str:
        cfg = {
            "CFG": self.config_dict
        }
        return json.dumps(cfg)


    