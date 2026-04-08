## LED Controller Test Plan

1. Controller Type and Name
	- Set controller 1 to RGBW with the name "ABigName11"
	- Set controller 2 to RGB+1 with the name "ABigName12"
	- Set controller 3 to 4Chan with the name "ABigName13"
	- Set controller 4 to RGBW with the name "ABigName14"
	- Switch between all table to verify that type and name remain.
2. Setting LEDs
	- Cn controller 1, set the color wheel to blue and verify the correct light sets to blue.
	- On controller 2, click the toggle on the plus 1 channel and verify that the white LED 
	  comes on, then turn it back off.
	- On controller 2, set the color wheel to red and verify the correct light set to red.
	- On controller 3, toggle on and then off, each of the 4 channels in turn and verify 
	  the correct LED on the correct light comes on (channel 1 is red, channel 2 is green,
	  channel 3 is blue and channel 4 is white). Then, toggle on channels 2 and 4.
	- On controller 4, set the color wheel to purple and verify the correct light sets to purple.
	- Switch between tabs and ensure nothing changes.
3. Brightness
	- On controller 1, step through the brightness levels and verify the light changes brightness.
	- On controller 2, step through the brightness levels and verify the light changes brightness.
	- On controller 2, toggle the plus 1 channel on and step through the brightness levels
      and verify the white light changes brightness. Then toggle off the plus one channel.
	- On controller 3, toggle on each channel in turn and step through the brightness levels
	  and verify the channel changes brightness. Then return to the state with channels 1 and
	  3 are off and channels 2 and 4 are on.
	- On controller 4, step through the brightness levels and verify the light changes brightness.
4. Scene Saving
	- Give scene 1 the name BigScene11 and save it.
	- Make some random changes to the lights and give scene 2 the name BigScene12 and save it.
	- Make some random changes to the lights and give scene 3 the name BigScene13 and save it.
	- Make some random changes to the lights and give scene 4 the name BigScene14 and save it.
5. All off
	- Click the "All Off" button and verify that all lights are turned off.
6. Check Pico files
	- Stop the pico program and force stop the phone app. Check the file system on the Pico
	  to see that a config.json file, and a sceneX.json file was created for each scene.
	- Inspect the config.json file and verify that it looks complete.
	- Inspect each scene json file and verify that they look correctly formed and are different from each other.
	- Inspect the ID.txt file to see the pico's unique ID.
7. Configuration set on startup
	- Restart the pico program and the phone app. Verify that the scene names have been 
	  set as specified above, the controller types and controller names have been set.
8. Scene Selection
	- Select scene 1 and verify that the lights match what was set by the test plan.
	- Select each of the remaining scenes and verify that the lights change to match 
	  what was saved.
9. Read ID
	- Verify that the pico's unique ID  is displayed correctly.
	
