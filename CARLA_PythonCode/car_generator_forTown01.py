#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Spawn NPCs into the simulation"""

import glob
import os
import sys
import math
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
from carla import ColorConverter

import argparse
import logging
import random
import xml.etree.ElementTree as ET 

#FILE_NAME = 'Town01_Car50.log'
FILE_NAME = 'Town01_Car50_2.log'
OUTPUT_PATH = 'Car50_2/data/'
BSM_ORIGINALPATH = '/home/usrp/carla/PythonAPI/shunsuke_workplace/Car50_2/'


#BSM_Vehicle = 1
#SensingVehicleID = 1
#BSM_Vehicle = list(range(49))
#BSM_path = '/home/usrp/carla/PythonAPI/shunsuke_workplace/_shunsuke/VehicleData_BSM/BSM_'+str(BSM_Vehicle)+'.txt'
#BSM_path = []
#for k in range(0,len(BSM_Vehicle)):
#    new_path = '/home/usrp/carla/PythonAPI/shunsuke_workplace/_shunsuke/VehicleData_BSM/BSM_'+str(BSM_Vehicle[k])+'.txt'
#    BSM_path.append(new_path)
#BSM_mode = True #when True, take all BSM

def BSMWriter(file_path, carID_list, timestamp, actor_list, ID_table, BSM_vehicleID):
#   BSM contains (time, location.x, location.y, heading)
    targetID = -1 #initialization
    for k in range(0, len(ID_table)):
        if(int(ID_table[k]['sumo_ID']) == BSM_vehicleID):
            targetID = int(ID_table[k]['Carla_ID'])

    for actor in actor_list:
        if actor.parent != None:
            continue
        if actor.id == targetID:
            transform = actor.get_transform()
            location = transform.location.x
            location = transform.location.x
            file_path.write(str(timestamp)+'\t'+str(transform.location.x)+'\t'+str(transform.location.y)+'\t'+str(transform.rotation.yaw)+'\n')




def MaxVehicleID(xmlfile): 
    tree = ET.parse(xmlfile) 
    root = tree.getroot() 
    VehicleNumber = 0
    for item in root.findall('timestep'): 
        for edge in item.findall('vehicle'):
            collectedID = int(edge.attrib['id'])
            if collectedID > VehicleNumber:
                VehicleNumber = collectedID

    return VehicleNumber+1  #from MaximumID to VehicleNumber


def parseXML_forAllVehicles(xmlfile,VehicleNumber): 
  
    # create element tree object 
    tree = ET.parse(xmlfile) 
    # get root element 
    root = tree.getroot() 
  
    # create empty list for parsing to Carla world
    vehicleID =[]
    vehicleInfo=[]
    for item in root.findall('timestep'): 
        #newsitems.append(item.attrib['time'])
        collectedtime = float(item.attrib['time'])
        for edge in item.findall('vehicle'):
            collectedID = int(edge.attrib['id'])
            if collectedID == 46:
                continue
            if collectedID == 48:
                continue
#            if collectedID <41 or collectedID > 42:
#            if collectedID !=42:
#                continue
#            print(collectedID, 'yeah')
            for vehicleID_ite in range(0, VehicleNumber):
                if collectedID == vehicleID_ite:
                    collectedangle = float(edge.attrib['angle'])
                    collectedangle = collectedangle - 90
                    if collectedangle < 0:
                        collectedangle = collectedangle + 360

#                    collectedx = float(edge.attrib['x'])
#                    collectedy = float(edge.attrib['y'])
                    collectedx = float(edge.attrib['x']) + 0.7* math.cos(collectedangle)
                    collectedy = float(edge.attrib['y']) - 0.7* math.sin(collectedangle)
                    collectedspeed = float(edge.attrib['speed'])
                    new_vehicleInfo={'time': collectedtime, 'id': collectedID, 'x': collectedx, 'y': collectedy, 'angle': collectedangle, 'speed': collectedspeed}
                    vehicleInfo.append(new_vehicleInfo)

    return vehicleInfo

def Generate_New_Vehicles(SumoVehicleInfo_ForAll, Elapsedtime, actor_list, blueprints, world, active_carID_list, killed_list, ID_table,vehicleID4Sensing):
    new_transform_list=[]
    new_id_list=[]

    for i in range(0, len(SumoVehicleInfo_ForAll)):
        collectedtime=SumoVehicleInfo_ForAll[i]['time']
        if (float(int(Elapsedtime)) == collectedtime and (not SumoVehicleInfo_ForAll[i]['id'] in active_carID_list) and (not SumoVehicleInfo_ForAll[i]['id'] in killed_list)):
            #transform = carla.Transform(carla.Location(x=float(SumoVehicleInfo_ForAll[i]['x']), y=344.26-float(SumoVehicleInfo_ForAll[i]['y'])-16, z=1.8431), carla.Rotation(pitch=0, yaw=float(SumoVehicleInfo_ForAll[i]['angle']), roll=0))
            transform = carla.Transform(carla.Location(x=float(SumoVehicleInfo_ForAll[i]['x']), y=344.26-float(SumoVehicleInfo_ForAll[i]['y'])-16, z=0.2), carla.Rotation(pitch=0, yaw=float(SumoVehicleInfo_ForAll[i]['angle']), roll=0))
            print('Generated... VehicleID is ', SumoVehicleInfo_ForAll[i]['id'], ' time is ', SumoVehicleInfo_ForAll[i]['time'])
            new_transform_list.append(transform)
            new_id_list.append(SumoVehicleInfo_ForAll[i]['id'])
            active_carID_list.append(SumoVehicleInfo_ForAll[i]['id'])
#    print('new_transform_list is: ',len(new_transform_list))
    for n, transform in enumerate(new_transform_list):
    #     if n >= args.number_of_vehicles:
    #         break
        #blueprint = world.get_blueprint_library().filter('vehicle')
        blueprint_library = world.get_blueprint_library()
#        blueprint = random.choice(blueprint_library.filter('vehicle.toyota.*'))
        blueprint = random.choice(blueprint_library.filter('vehicle.toyota.prius')) # having 10 different colors
#        blueprint = random.choice(blueprint_library.filter('vehicle.seat.leon'))
#        blueprint = random.choice(blueprint_library.filter('vehicle.*'))
#        print(blueprint)
#        blueprint = random.choice(blueprint_library.filter('vehicle.mini.cooperst'))
        #vehicle.chevrolet.impala
        #vehicle.diamondback.century
        #vehicle.audi.tt,tags
        #vehicle.harley-davidson.low
        #vehicle.bmw.grandtourer,tags
        #vehicle.bmw.isetta,tags
        #vehicle.mercedes-benz.coupe
        #vehicle.nissan.patrol
        #vehicle.gazelle.omafiets
        #vehicle.nissan.micra
        #vehicle.nissan.patrol
        #vehicle.audi.etron
        #vehicle.yamaha.yzf
        #vehicle.audi.etron



        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
#            color = random.choice(blueprint.get_attribute('color'))
            blueprint.set_attribute('color', color)
#        blueprint = random.choice(blueprint_library.filter('vehicle.toyota.prius'))
        blueprint.set_attribute('role_name', 'autopilot')


        actor = world.spawn_actor(blueprint, transform)
        actor_list.append(actor)
        actor.set_autopilot(False)
        ID_relationship={'sumo_ID':new_id_list[n],'Carla_ID': actor.id}
        ID_table.append(ID_relationship)

        # sensorother_bp = blueprint_library.find('sensor.other.obstacle')
        # sensorother_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        # othersensor = world.spawn_actor(sensorother_bp, sensorother_transform, attach_to=actor)
        # othersensor.listen(lambda image: image.save_to_disk('leon_log/others_%s' ) % image.frame_number)
        # actor_list.append(othersensor)


        if new_id_list[n]==vehicleID4Sensing:


            #Front Camera
##                camera_transform = carla.Transform(carla.Location(x=1.0,z=1.3))
#                camera_transform = carla.Transform(carla.Location(x=0.4,z=2.0))
            #Rear Camera
#                camera_transform = carla.Transform(carla.Location(x=-0.8,z=2.0), carla.Rotation(yaw = 180))

            #Front camera
            c_height = 1.5
            x_diff_front = 0.4
            x_diff = 0.33
            x_diff_rear = 0.7
            y_diff = x_diff**(1/2.0)
#            try:
#                os.makedirs('_shunsuke/data')
#            except:
#                print('data folder cannot be generated')

            try:
                os.makedirs(OUTPUT_PATH+str(new_id_list[n]))
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/front')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/front_Right60')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/front_Left300')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/rear_Right120')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/rear180')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/rear_Left240')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/frontD')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/front_Right60D')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/front_Left300D')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/rear_Right120D')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/rear180D')
                os.makedirs(OUTPUT_PATH+str(new_id_list[n])+'/rear_Left240D')
            except:
                print('Cannot make new folder for data for ID %d',new_id_list[n])

            writing_path=OUTPUT_PATH+str(new_id_list[n])+'/camera.config'
            f = open(writing_path, "w")
            f.write('worldtime(camera)\ttimestamp\tcamera_height\tx_diff_front\tx_diff\tx_diff_rear\ty_diff\n')
            f.write(str(world.wait_for_tick().elapsed_seconds)+'\t'+str(Elapsedtime)+'\t'+str(c_height)+'\t'+str(x_diff_front)+'\t'+str(x_diff)+'\t'+str(x_diff_rear)+'\t'+str(y_diff))
            f.close()


            print('camera set...!!')
            camera_bp = blueprint_library.find('sensor.camera.rgb')
            camera_transform = carla.Transform(carla.Location(x=x_diff_front,z=c_height))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/front/rgb_%s.png' % (image.timestamp)))
            new_id_list[n]
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Front Right camera
            camera_bp = blueprint_library.find('sensor.camera.rgb')
            camera_transform = carla.Transform(carla.Location(x=x_diff,y = y_diff, z=c_height), carla.Rotation(yaw = 60))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/front_Right60/rgb_%s.png' % (image.timestamp)))
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Front Left camera
            camera_bp = blueprint_library.find('sensor.camera.rgb')
            camera_transform = carla.Transform(carla.Location(x=x_diff,y = -y_diff, z=c_height), carla.Rotation(yaw = 300))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/front_Left300/rgb_%s.png' % (image.timestamp)))
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Rear Right camera
            # camera_bp = blueprint_library.find('sensor.camera.rgb')
            # camera_transform = carla.Transform(carla.Location(x=-x_diff_rear,y = y_diff, z=c_height), carla.Rotation(yaw = 120))
            # camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            # camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/rear_Right120/rgb_%s.png' % (image.timestamp)))
            # transform = camera.get_transform()
            # transform = actor.get_transform()
            # actor_list.append(camera)

            #Rear camera
            camera_bp = blueprint_library.find('sensor.camera.rgb')
            camera_transform = carla.Transform(carla.Location(x=-x_diff_rear-0.2, z=c_height), carla.Rotation(yaw = 180))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/rear180/rgb_%s.png' % (image.timestamp)))
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Rear Left camera
            # camera_bp = blueprint_library.find('sensor.camera.rgb')
            # camera_transform = carla.Transform(carla.Location(x=-x_diff_rear, y=-y_diff,z=c_height), carla.Rotation(yaw = 240))
            # camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            # camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/rear_Left240/rgb_%s.png' % (image.timestamp)))
            # transform = camera.get_transform()
            # transform = actor.get_transform()
            # actor_list.append(camera)

            #Depth
            #Front camera
            camera_bp = blueprint_library.find('sensor.camera.depth')
            camera_transform = carla.Transform(carla.Location(x=x_diff_front,z=c_height))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/frontD/depth_%s.png' % (image.timestamp)))
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Depth: Front Right camera
            camera_bp = blueprint_library.find('sensor.camera.depth')
            camera_transform = carla.Transform(carla.Location(x=x_diff,y = y_diff, z=c_height), carla.Rotation(yaw = 60))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/front_Right60D/depth_%s.png' % (image.timestamp)))
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Depth: Front Left camera
            camera_bp = blueprint_library.find('sensor.camera.depth')
            camera_transform = carla.Transform(carla.Location(x=x_diff,y = -y_diff, z=c_height), carla.Rotation(yaw = 300))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/front_Left300D/depth_%s.png' % (image.timestamp)))
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Depth: Rear Right camera
            # camera_bp = blueprint_library.find('sensor.camera.depth')
            # camera_transform = carla.Transform(carla.Location(x=-x_diff_rear,y = y_diff, z=c_height), carla.Rotation(yaw = 120))
            # camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            # camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/rear_Right120D/depth_%s.png' % (image.timestamp)))
            # transform = camera.get_transform()
            # transform = actor.get_transform()
            # actor_list.append(camera)

            #Depth: Rear camera
            camera_bp = blueprint_library.find('sensor.camera.depth')
            camera_transform = carla.Transform(carla.Location(x=-x_diff_rear-0.2, z=c_height), carla.Rotation(yaw = 180))
            camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/rear180D/depth_%s.png' % (image.timestamp)))
            transform = camera.get_transform()
            transform = actor.get_transform()
            actor_list.append(camera)

            #Depth: Rear Left camera
            # camera_bp = blueprint_library.find('sensor.camera.depth')
            # camera_transform = carla.Transform(carla.Location(x=-x_diff_rear, y=-y_diff,z=c_height), carla.Rotation(yaw = 240))
            # camera = world.spawn_actor(camera_bp, camera_transform, attach_to=actor)
            # camera.listen(lambda image: image.save_to_disk(OUTPUT_PATH+str(new_id_list[n])+'/rear_Left240D/depth_%s.png' % (image.timestamp)))
            # transform = camera.get_transform()
            # transform = actor.get_transform()
            # actor_list.append(camera)



            # lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
            # lidar_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
            # lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=actor)
            # lidar.listen(lambda image: image.save_to_disk('_shunsuke/Lidar_%s' % image.frame_number))
            # actor_list.append(lidar)

            # semantic_segmentation_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
            # semantic_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
            # semanticcamera = world.spawn_actor(semantic_segmentation_bp, semantic_transform, attach_to=actor)
            # cc = carla.ColorConverter.CityScapesPalette
            # semanticcamera.listen(lambda image: image.save_to_disk('leon_log/semantic/semantic_%s_%s' % (image.frame_number, image.timestamp), cc))
            # actor_list.append(semanticcamera)

            # sensorother_bp = blueprint_library.find('sensor.other.obstacle')
            # sensorother_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
            # othersensor = world.spawn_actor(sensorother_bp, sensorother_transform, attach_to=actor)
            # othersensor.listen(lambda image: image.save_to_disk('leon_log/others_%s' ) % image.frame_number)
            # actor_list.append(othersensor)

#Raw
#CityScapesPalette
#            colored_sem_seg = image_converter.labels_to_cityscapes_palette(semanticcamera)
            #converted_semantic = ColorConverter.CityScapesPalette(semanticcamera)
#            converted_semantic.listen(lambda image: image.save_to_disk('_shunsuke/semantic/test_%s' % image.frame_number))

#############################
#############################


    return actor_list, active_carID_list, ID_table


def ChangeLocation4ExistingCars(SumoVehicleInfo_ForAll, Previous_Elapsedtime, Elapsedtime, actor_list, actor_carID_list, VehicleNumber, killed_list, ID_table):
    counter = 0
    erase_vehicle_list=[] #For next function
    Floor_time=math.floor(Elapsedtime)
    Ceil_time=math.ceil(Elapsedtime)
    # print('len(actor_list):', len(actor_list), actor_list[0].type_id, actor_list[0].parent)#, actor_list[0].semantic_tags)
    # print('len(ID_table):', len(ID_table))
    # print(type(actor_list[0].type_id))
    # for i in range(0, len(actor_list)):
    #     print('shunsuke:', actor_list[i].type_id, actor_list[i].parent, actor_list[i].id)
    #     if(actor_list[i].parent != None):
    #         print('nyan', actor_list[i].parent.id)

    for actor in actor_list:
        if actor.parent != None: # meaning "attached sensors to vehicles"
#            print('not None...', actor.parent)
            continue
        if actor.type_id == 'sensor.camera.rgb': # meaning "camera in Infrastructure (like in Road Intersection)"
#            print('Infra!')
            continue
#        print('test', len(actor_list), len(actor_carID_list), actor.parent, actor.type_id)
        targetID = actor_carID_list[counter]
        
        Updated_x = -1
        Updated_y = -1
        #print(len(SumoVehicleInfo_ForAll), targetID, counter)# jUST O,1,2,3 THIS IS WIERD!!//counter is not increased
        for i in range(0, len(SumoVehicleInfo_ForAll)):
            flag_ceil = False
            #print(len(SumoVehicleInfo_ForAll), targetID,)
#            print('counter', counter)
#            print('before if...',actor.id)
#            if(Floor_time == SumoVehicleInfo_ForAll[i]['time']):
#                print(len(SumoVehicleInfo_ForAll), targetID)
#            if(targetID == SumoVehicleInfo_ForAll[i]['id']):
#                print(len(SumoVehicleInfo_ForAll), targetID)
            #if(counter == 3):
                #print('targetID ', targetID,' Floor_time ', Floor_time, ' Elapsedtime ', Elapsedtime)

            if(targetID == SumoVehicleInfo_ForAll[i]['id'] and Floor_time == SumoVehicleInfo_ForAll[i]['time']):
#                print('after if...',actor.id)
                Floor_x = float(SumoVehicleInfo_ForAll[i]['x'])
                Floor_y = 344.26-16- float(SumoVehicleInfo_ForAll[i]['y'])
#                Floor_z = SumoVehicleInfo_ForAll[i]['z']
#                Floor_pitch = SumoVehicleInfo_ForAll[i]['pitch']
                Floor_yaw = float(SumoVehicleInfo_ForAll[i]['angle'])# - 90
#                print('test2:shunsuke')
                iterate_number = i + VehicleNumber*2
                if(len(SumoVehicleInfo_ForAll)<=iterate_number):
                    iterate_number=len(SumoVehicleInfo_ForAll);
                for j in range (i, iterate_number):
                    if(targetID == SumoVehicleInfo_ForAll[j]['id'] ) and Ceil_time == SumoVehicleInfo_ForAll[j]['time']:
                        Ceil_x = float(SumoVehicleInfo_ForAll[j]['x'])
                        Ceil_y = 344.26-16- float(SumoVehicleInfo_ForAll[j]['y'])
                        Ceil_yaw = float(SumoVehicleInfo_ForAll[j]['angle'])# - 90

                        flag_ceil = True
                        break
                if flag_ceil == False:
                    print('shunsuke: ', flag_ceil, counter, Elapsedtime,'\t killed...',killed_list)
                    print('shunsuke: ', iterate_number, ' and i is ',i, 'and,', Ceil_time, targetID, killed_list, Elapsedtime)
                    print(' ') 
                if(flag_ceil == True):
                    proceeded_portion = (Elapsedtime - Floor_time)
                    Updated_x = Floor_x + (Ceil_x - Floor_x) * proceeded_portion
                    Updated_y = Floor_y + (Ceil_y - Floor_y) * proceeded_portion
                    Updated_yaw = Floor_yaw + (Ceil_yaw - Floor_yaw) * proceeded_portion
#                    print('ID 42-before', Floor_yaw, Ceil_yaw)
                    if (Ceil_yaw - Floor_yaw) <= -180:
                        Ceil_yaw = Ceil_yaw + 360
                        Updated_yaw = Floor_yaw + (Ceil_yaw - Floor_yaw) * proceeded_portion
                    if (Ceil_yaw - Floor_yaw) >= 180:
                        Floor_yaw = Floor_yaw + 360
                        Updated_yaw = Floor_yaw + (Ceil_yaw - Floor_yaw) * proceeded_portion
#                    print('ID 42-after', Floor_yaw, Ceil_yaw, proceeded_portion, Updated_yaw)
#                    print('    before:', counter)
                    counter = counter + 1
#                    print('    after :', counter)

            if targetID in killed_list:
                counter = counter + 1
#                print('test5:shunsuke', len(killed_list))
                break


#        print('test3:shunsuke', counter)
        if (not Updated_x == -1 ) and (not Updated_y == -1):
            location=actor.get_location()
            location.x = Updated_x
            location.y = Updated_y
            transform = actor.get_transform()
            transform.location = location
            transform.rotation.yaw = Updated_yaw
            actor.set_transform(transform)
#            print('test4:shunsuke')

    return counter


def Kill_Finished_Vehicles(SumoVehicleInfo_ForAll, Elapsedtime, actor_list,killed_list, active_carID_list, ID_table):
#    print("kill_function is caled", len(actor_list))
    previous_car_set = []
    new_car_set = []
    targetID_Carla=[]
    for i in range(0, len(SumoVehicleInfo_ForAll)):
        if int(Elapsedtime) == SumoVehicleInfo_ForAll[i]['time']:
            previous_car_set.append(SumoVehicleInfo_ForAll[i]['id'])
        if int(Elapsedtime)+2 == SumoVehicleInfo_ForAll[i]['time']:
            new_car_set.append(SumoVehicleInfo_ForAll[i]['id'])

    killed_car_set =[]
    targetIDs_forSUMO=[]

    for i in range(0, len(previous_car_set)):
        if previous_car_set[i] not in new_car_set:
            killed_car_set.append(previous_car_set[i])
#            print('size is', len(killed_car_set), previous_car_set[i])


    for i in range(0, len(killed_car_set)):
        targetID_forSUMO = killed_car_set[i]
        targetIDs_forSUMO.append(targetID_forSUMO)
        for j in range(0, len(ID_table)):
            if( int(ID_table[j]['sumo_ID']) == targetID_forSUMO):
                targetID_Carla.append(int(ID_table[j]['Carla_ID']))

#    print(killed_car_set, targetID_Carla)
    pointer4erase =[]
    for n, actor in enumerate(actor_list):
        if actor.parent != None:
            continue
        for k in range(0, len(targetID_Carla)):
            if(actor.id == targetID_Carla[k]):
                #print('actor destroy ID:', actor.id, 'n', n)
                actor.destroy()
                pointer4erase.append(n)
                del actor_list[n]
                break

#    for i in reversed(range(0, len(pointer4erase))):
#        del actor_list pointer4erase[i]

#                del actor_list[n]
    temp_killed_list=[]
    for i in range(0, len(targetIDs_forSUMO)):
        for j in range(0, len(active_carID_list)):
            if(targetIDs_forSUMO[i]==active_carID_list[j]):
                print('Deleting...ID:', targetIDs_forSUMO[i])
                killed_list.append(active_carID_list[j])
                temp_killed_list.append(active_carID_list[j])
                del active_carID_list[j]
                break

    for k in range(0, len(pointer4erase)):
        if not (len(pointer4erase)==len(temp_killed_list)):
            for n, actor in enumerate(actor_list):
                if actor.parent != None:
                    continue
                for m in range(0, len(targetID_Carla)):
                    if(actor.id == targetID_Carla[m]):
                        print('actor destroy ID:', actor.id, 'n', n)
                        actor.destroy()
                        pointer4erase.append(n)
                        del actor_list[n]
                        break
    #Kill sensors
#    print('killed...ID is', targetID_Carla)
    kill_sensor_set = []
    kill_sensor_pointer = []
#    print('actor_list1: ',len(actor_list))

    for n, actor in enumerate(actor_list):
        if actor.parent != None:
#            print('sensor!', actor.id, 'targetID is', targetID_Carla)
            for k in range (0, len(targetID_Carla)):
#                print('parent id is ', actor.parent.id)
 #               print('targetID_Carla[k]', targetID_Carla[k])
                if(actor.parent.id == targetID_Carla[k]):
                    kill_sensor_set.append(actor)
                    kill_sensor_pointer.append(n)

                    #actor.destroy()
                    #del actor_list[n]
                    #print('delete!!')
                    #break
#    print('actor_list2: ',len(actor_list))

    for targetactor in kill_sensor_set:
        for n, actor in enumerate(actor_list):
            if (targetactor == actor):
                actor.destroy()
                del actor_list[n]
#                print('destroying!!')

#    print('actor_list3: ',len(actor_list))

#    while(len(kill_sensor_set)>=1):
#        kill_sensor_set[0].destroy()
#    temp_length = len(kill_sensor_pointer)
#    for k in range (0, len(kill_sensor_pointer)):
#        print('pointer', temp_length - 1 - k)
#        print('len', len(kill_sensor_pointer) )
#        del kill_sensor_pointer[temp_length - 1 - k]
#
#    print('actor_list4: ',len(actor_list))


#                    print('kill sensor...')

#    if not (len(pointer4erase)==len(temp_killed_list)):
#        for n, actor in enumerate(actor_list):
#            if actor.parent != None:
#                continue
#            for k in range(0, len(targetID_Carla)):
#                if(actor.id == targetID_Carla[k]):
#                    print('actor destroy ID:', actor.id, 'n', n)
#                    actor.destroy()
#                    pointer4erase.append(n)
#                    del actor_list[n]


    return actor_list,killed_list,active_carID_list


def main():
    #VehicleNumber = MaxVehicleID('sumo_log/Town01_Car50.log') 
    VehicleNumber = MaxVehicleID('sumo_log/'+FILE_NAME) 

#    VehicleNumber = 50
    active_carID_list = []
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=VehicleNumber,
        type=int,
        help='number of vehicles (default: 10)')
    argparser.add_argument(
        '-d', '--delay',
        metavar='D',
        default=2.0,
        type=float,
        help='delay in seconds between spawns (default: 2.0)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '-id', '--id',
        dest='vehicleID',
        default=10000,
        type = int,
        help='for sensor')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    actor_list = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(2.0)


    #SumoVehicleInfo_ForAll = parseXML_forAllVehicles('sumo_log/Town01_Car50.log',VehicleNumber) 
    SumoVehicleInfo_ForAll = parseXML_forAllVehicles('sumo_log/'+FILE_NAME,VehicleNumber) 
    #BSM_path = '/home/usrp/carla/PythonAPI/shunsuke_workplace/_shunsuke/VehicleData_BSM/BSM_'+str(args.vehicleID)+'.txt'
    try:
        os.makedirs(BSM_ORIGINALPATH+'VehicleData_BSM/')
    except:
        pass

    BSM_path = BSM_ORIGINALPATH+'VehicleData_BSM/BSM_'+str(args.vehicleID)+'.txt'
    bsm_f = open(BSM_path,"w")






    try:
        world = client.get_world()
        blueprints = world.get_blueprint_library().filter(args.filter)

        if args.safe:
            blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
            blueprints = [x for x in blueprints if not x.id.endswith('isetta')]
            blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]

        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points) 

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        batch = []
        killed_list =[]
        ID_table =[]



        init_timestamp = world.wait_for_tick()
        
        elapsedtime = 0.00
        elapsedtime_mill_sec = 0.00
       
        (actor_list, active_carID_list, ID_table) = Generate_New_Vehicles(SumoVehicleInfo_ForAll, elapsedtime, actor_list, blueprints, world, active_carID_list, killed_list,ID_table, args.vehicleID)

        print('before while', elapsedtime)
        initial_flag = True

        #After launching Carla
        while True:
            #print(args.vehicleID)
            previous_elapsedtime = elapsedtime
            previous_mill_sec = elapsedtime_mill_sec
            if initial_flag == True:
                initial_flag = False
                timestamp = init_timestamp
            else:
                timestamp = world.wait_for_tick()
            #print('initial flag ',initial_flag)
            timestamp_mill_sec = timestamp.elapsed_seconds % 1
            elapsedtime = timestamp.elapsed_seconds - init_timestamp.elapsed_seconds
            elapsedtime_mill_sec = elapsedtime % 1 
            #print('test2',previous_mill_sec, 'and', elapsedtime_mill_sec)
            #print('location changed...time:',elapsedtime, 'elapsedtime_mill_sec',elapsedtime_mill_sec, 'previous_mill_sec', previous_mill_sec)
#            for actor in actor_list:
#                if isinstance(actor, carla.libcarla.ServerSideSensor):
#                    print(actor.type_id)#, actor.id)

#            sensorother_bp = blueprint_library.find('sensor.other.obstacle')
#            sensorother_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
#            othersensor = world.spawn_actor(sensorother_bp, sensorother_transform, attach_to=actor)
#            othersensor.listen(lambda image: image.save_to_disk('leon_log/others_%s' ) % image.frame_number)
#            actor_list.append(othersensor)

            #1. ImageProcessing with TensorFlow
            ##  ...since vehicle movement is not changed for iteration, you can post-process the image processing and determine which info is transmitted
            #
            #2. Data transmission and Evaluation (whether the information is already known or not)
            #...Do all vehicles have to work for the notification? Is it like "information flooding"?
            # Reinforcement learning?
            #
            #
            #3 When do I have to join the cooperative perception?
            # Road intersections -- many buildings/blocking but also congested.
            #if camera is in Infrastructure side, it the cooperative perception really needed?
            #
            #3. Can we make a map (heat map) for utility of cooperative perception?
            #  --maybe it is not useful in rural straight road
            #  --maybe it is useful in road intersections, roundabout, T-intersection
            #


            if previous_mill_sec > elapsedtime_mill_sec:
                #print('killing and generating')
#                print('shunsuke:', actor_list[0].get_location().x, actor_list[0].get_location().y)
#                if not(len(actor_list) == Active_Car_Num):
#                    print('KILL! in Function')
                (actor_list, killed_list,active_carID_list) = Kill_Finished_Vehicles(SumoVehicleInfo_ForAll, elapsedtime, actor_list, killed_list, active_carID_list,ID_table)

                #Generate New Vehicle(s)
#                print('--time is', elapsedtime, 'vehicle number', len(actor_list), len(active_carID_list))
                (actor_list, active_carID_list, ID_table) = Generate_New_Vehicles(SumoVehicleInfo_ForAll, elapsedtime, actor_list, blueprints, world, active_carID_list,killed_list, ID_table, args.vehicleID)

                if(len(actor_list) == 0):
                    if elapsedtime > 10:
                        client.stop_recorder()
                        bsm_f.close()
                        quit()


                if elapsedtime >500:
                    ErrorPath = '/home/usrp/carla/PythonAPI/shunsuke_workplace/OUTPUT_PATH'+str(args.vehicleID)+'.txt'
                    ErrorPath = open(writing_path, "w")
                    ErrorPath.write('Error: I cannot finish this simulation...\n')
                    ErrorPath.close()
                    quit()

            Active_Car_Num = ChangeLocation4ExistingCars(SumoVehicleInfo_ForAll, previous_elapsedtime, elapsedtime, actor_list, active_carID_list, VehicleNumber, killed_list, ID_table)
            BSMWriter(bsm_f, active_carID_list,elapsedtime, actor_list, ID_table, args.vehicleID)


#                print('len(actor_list):', len(actor_list), actor_list[0].type_id, actor_list[0].parent)#, actor_list[0].semantic_tags)
#                print('len(ID_table):', len(ID_table))
#                print(type(actor_list[0].type_id))
#                for i in range(0, len(actor_list)):
#                    print('shunsuke:', actor_list[i].type_id, actor_list[i].parent, actor_list[i].id)
#                    if(actor_list[i].parent != None):
#                        print('nyan', actor_list[i].parent.id)


#                print('len(ID_table):', len(ID_table))
#                print(ID_table)
#                print(len(ID_table))

#                print('time is', elapsedtime, 'vehicle number', len(actor_list), len(active_carID_list))
#                if int(elapsedtime) >= 76:
#                    print('Aliving CarList', active_carID_list)
#                    for j in range (0, len(actor_list)):
#                        print('Carla:', actor_list[j].id)

#                    for i in range(0, len(active_carID_list)):
#                        print('when t is 80: ',active_carID_list[i])


    finally:
        print('\ndestroying %d actors' % len(actor_list))
        for actor in actor_list:
            print(actor.id, actor.parent)
            actor.destroy()
        client.stop_recorder()
        bsm_f.close()
if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
