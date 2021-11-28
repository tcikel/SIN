import os, sys, json
sys.path.append(os.path.join(os.environ.get("SUMO_HOME"), 'tools'))
import traci,paho.mqtt.client as mqtt
sumoBinary = "/usr/share/sumo/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "/home/tcikel/Sumo/2021-11-16-23-21-53/test/new.sumocfg"]



light = "GGGgrrrrGGGgrrrr"


#getTimeSinceDetection -- returns the time in seconds since last detection
#getTimeSinceDetection -- return the percentage of time the dectector was occupied by a vehicle
#TODO:: Vytvorit kontrolel
def on_message(client, userdata, msg):
    global light
    light = str(msg.payload)[2:-1]
    #print(light)

def collect_induction_loops_incoming_ids(x):
    loops=[]
    i = x
    while i < 6+x:
        if (i%2) == 1:
            loops.append(traci.inductionloop.getLastStepVehicleIDs("det_" + str(i)))
        i += 1
        #print (x + "  " + i)
    return json.dumps(loops)

def collect_induction_loops_outgoing_ids(x):
    loops=[]
    i = x
    while i < 6+x:
        if (i%2) == 0:
            loops.append(traci.inductionloop.getLastStepVehicleIDs("det_" + str(i)))
            #print("lol")
        i += 1
        #print (x + "  " + i)
    return json.dumps(loops)

def collect_induction_loops(x):
    loops=bytearray()
    i = x
    while i < 6+x:
        loops.append(traci.inductionloop.getLastStepVehicleNumber("det_" + str(i)))
        i += 1
        #print (x + "  " + i)
    
    
    return loops

def collect_timer(x):
    loops=bytearray()
    i = x
    while i < 6+x:
        tmp = int(traci.inductionloop.getTimeSinceDetection("det_" + str(i)))
        tmp = tmp if tmp<255 else 255
        print(tmp)
        loops.append(tmp)
        i += 1
    return loops


def collect_percentage(x):
    loops=bytearray()
    i = x
    while i < 6+x:
        loops.append(int(traci.inductionloop.getLastStepOccupancy("det_" + str(i))))
        i += 1
    
    return loops


client  = mqtt.Client("0")
client.connect("127.0.0.1")
client.on_message = on_message
client.subscribe("traffic_controller")
client.loop_start()
traci.start(sumoCmd)
step = 0
while step < 1000:
    traci.simulationStep()
    client.publish("Step",step)
    step += 1
    traci.trafficlight.setRedYellowGreenState("gneJ8",light)
    client.publish("induction_loops_e5",collect_induction_loops(0))
    client.publish("induction_loops_e3",collect_induction_loops(6))
    client.publish("induction_loops_e7",collect_induction_loops(12))
    client.publish("induction_loops_e1",collect_induction_loops(18))
    client.publish("induction_loops_e5_ids_incoming",collect_induction_loops_incoming_ids(0))
    client.publish("induction_loops_e5_ids_outgoing",collect_induction_loops_outgoing_ids(0))
    client.publish("induction_loops_e3_ids_incoming",collect_induction_loops_incoming_ids(6))
    client.publish("induction_loops_e3_ids_outgoing",collect_induction_loops_outgoing_ids(6))
    client.publish("induction_loops_e7_ids_incoming",collect_induction_loops_incoming_ids(12))
    client.publish("induction_loops_e7_ids_outgoing",collect_induction_loops_outgoing_ids(12))
    client.publish("induction_loops_e1_ids_incoming",collect_induction_loops_incoming_ids(18))
    client.publish("induction_loops_e1_ids_outgoing",collect_induction_loops_outgoing_ids(18))
    client.publish("induction_loops_timer_e5",collect_timer(0))
    client.publish("induction_loops_timer_e3",collect_timer(6))
    client.publish("induction_loops_timer_e7",collect_timer(12))
    client.publish("induction_loops_timer_e1",collect_timer(18))
    client.publish("induction_loops_percentage_e5",collect_percentage(0))
    client.publish("induction_loops_percentage_e3",collect_percentage(6))
    client.publish("induction_loops_percentage_e7",collect_percentage(12))
    client.publish("induction_loops_percentage_e1",collect_percentage(18))

    client.publish("traffic_light",traci.trafficlight.getRedYellowGreenState("gneJ8"))
   #print( traci.inductionloop.getLastStepVehicleNumber("det_1"))

traci.close(False)
