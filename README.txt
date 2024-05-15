Hello!
This file gives a description of the scripts found within this folder.
The exact file names may not match the file names found on various diagrams found within papers or presentations,
but the intent of the files will be given here with correspondence to the actual file name.


Model Generation:
These are python scripts meant to be run directly within Abaqus.
It then allows use of the GenerateGeometry function which is what creates the MXene model and sets up the simulation settings.
	+Generate_Geometry_Final.py
		Is the primary script used for most of the simulations. Has an example use of the function and how to loop the function to create multiple models in one run. 
	+Broken_Connections.py
		Is another script which modifies one aspect of the Generate_Geometry_Final.py script which makes some of the flake-flake or flake-matrix connections "broken"
		(really just extremely weak to not need to modify the code as much) to better match the empirical manufacturing process.
		Defaults to having 0% of the connections being broken which should give the exact same result as the Generate_Geometry_Final.py script.

FAIR WARNING: These scripts were made by someone inexperienced with Python and Abaqus (aka Jason Hasse). 
There are certain bugs that pop up which dont allow certain configurations to work properly within abaqus, causing simulations to fail or not start at all.
It works pretty well, but isnt perfect. Make sure the code is doing what you expect it to, check the geometries by hand!


PostProcessing:
These are also python scripts that are meant to be run after the model is generated and the simulation is performed.
Many of the directories will have to be tweaked as I put them in a string literals from my personal system. I recommend this practice as well, but is obviously not required.
	+PostProcessing-CSVs.py
		Should be used within Abaqus directly. It will convert the .odb file (the large output file) into a .csv file with the information that we are concerned.
		The .csv files are much much smaller in size and can be stored on personal machines much easier and doesnt require the use of an abaqus license to still use the data from the simulation.
	+PostProcessing-SystemPlots2.py
		Can be performed without interfacing with Abaqus. Will use the .csv file made and calculate some summary information about each of the .csv files.
		Also has the option to generate some basic plots regarding the stress strain curves as well as the internal/kinectic energy relations.
		Obvious indications are made these plots when the simulation should not be trusted. However, these plots are not meant to be shown in papers, merely to help the user understand the simulations.



Visualization:
These are scripts made in R (my preferred language) which are meant to create more visually appealing plots. If the user is comfortable with Python, feel free to recreate them in Python instead of working with R.
They are also made with base R plotting functions which tend to be more user friendly in my opinion compared to ggplot. 