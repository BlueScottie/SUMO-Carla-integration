# SUMO-Carla-integration

The project is to integrate SUMO and Carla, because Carla's traffic is insufficiently sophisticated yet.
We use the traffic information from SUMO and parse them into Carla.

To achieve the integration, we have 4-step processings: (i) Map Conversion, (ii) Generating Origin/Destination Pairs in SUMO, (iii) Generating Trajectory Information in SUMO, and (iv) Parcing the Trajectories in Carla.

(1) Map Conversion
Carla uses OpenDRIVE and SUMO uses its own dedicated format (SUMO_map, xml style).
You basically use ./mapconverter to convert the road networks. (see SUMO_script directory)
-- it is based on "netconvert" command (https://sumo.dlr.de/docs/NETCONVERT.html)
  e.g.) netconvert --opendrive-files Town01.xodr

-- Town 01 and Town 02 are well-organized and well-tested
  Town 01 size:  410,68 x 344,26
  Town 02 size:  205,59 x 204,48
  Since the origin in Carla world and the one in SUMO are different, these values will be used

-- You can get .net.xml files as map databases (e.g. Town01.net.xml)


(2) Generating Origin/Destination Pairs in SUMO

-- You can simply type the following command:
  $SUMO_HOME/tools/randomTrips.py -n Town01.net.xml -e 50

-- Instruction is described in https://sumo.dlr.de/wiki/Tools/Trip

-- You can get trips.trips.xml file

(3) Generating Trajectory Information in SUMO

-- First, you should set up test.sumocfg file
  map file, routefile, and output file

-- Then, you can simply tyupe the following command:
  sumo -c test.sumocfg --fcd-output Town01_50.log

-- Town01_50.log is used to generate traffic in Carla world with Town01 map


(4) Parcing the Trajectories in Carla

-- Step1: Launch the Carla. Command is:
  ./Unreal/CarlaUE4/Saved/StagedBuilds/LinuxNoEditor/CarlaUE4.sh  -benchmark -fps=10

-- Step2: Generate & Store the data. Command is:
  python car_generator_forTown01.py -id $k

-- Note that Carla running with multiple sensors are very heavy processing. We may take the sensor data for each vehicle/module.
-- Please select small cars to run right now, in order to avoid vehicle collisions
-- You can use "script_forgettingdata" to get the data one by one.
  ./script_forgettingdata



# IEEE Intelligent Vehicles Symposium (IV), Cooperative Perception with Deep Reinforcement Learningfor Connected Vehicles (S. Aoki, T. Higuchi, O. Altintas),
# from National Institute of Informatics, Japan, Carnegie Mellon University, US, and Toyota InfoTech, US.
