from math import dist
import os
import subprocess
import sys
import csv

output_file = "halow-experience.csv"

battery_capacity = 2300
battery_voltage = 3

alternatives = [[500, 100, 1000, 10, "rural"],
                [10, 100, 1000, 1000, "rural"],
                [10, 1, 1000, 1000, "rural",],
                [500, 1, 15, 1000, "rural"],
                [10, 100, 15, 10, "rural"],
                [500, 1, 1000, 10, "rural"],
                [500, 100, 15, 1000, "rural"],
                [10, 1, 15, 10, "rural"], 
                [500, 100, 1000, 10, "urban"],
                [10, 100, 1000, 1000, "urban"],
                [10, 1, 1000, 1000, "urban",],
                [500, 1, 15, 1000, "urban"],
                [10, 100, 15, 10, "urban"],
                [500, 1, 1000, 10, "urban"],
                [500, 100, 15, 1000, "urban"],
                [10, 1, 15, 10, "urban"]
                ]


mcs = 0
sgi = 1
beacon_interval = 51200
nraw_groups = 1
nGW = 1
trafficDirection = "upstream"

for nED, period, size, distance, environment in alternatives:
    simulation_time = period * 10

    os.environ['MCS'] = str(mcs)
    os.environ['SGI'] = str(sgi)
    os.environ['BEACONINTERVAL'] = str(beacon_interval)
    os.environ['NRAWGROUPS'] = str(nraw_groups)

    os.environ['DISTANCE'] = str(distance)
    os.environ['PACKETSIZE'] = str(size)
    os.environ['PERIOD'] = str(period)
    os.environ['RADIOENVIRONMENT'] = str(environment)
    os.environ['NBDEVICES'] = str(nED)
    os.environ['NGW'] = str(nGW)
    os.environ['TRAFFICDIR'] = trafficDirection

    os.environ['SIMULATION_TIME'] = str(simulation_time)
    os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
    os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

    os.environ['LOGFILE'] = "log-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"
    os.environ['LOGFILEPARSED'] = "log-parsed"+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"

    output = subprocess.check_output('cd NS3-802.11ah; ./waf --run "rca --Nsta=$NBDEVICES --radioEnvironment=$RADIOENVIRONMENT --nGW=$NGW --mcs=$MCS --sgi=$SGI --BeaconInterval=$BEACONINTERVAL --NGroup=$NRAWGROUPS --rho=$DISTANCE --simulationTime=$SIMULATION_TIME --trafficInterval=$PERIOD --payloadSize=$PACKETSIZE --batteryCapacity=$BATTERY_CAPACITY --voltage=$BATTERY_VOLTAGE" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
    latency_ = subprocess.check_output('cd NS3-802.11ah; cat $LOGFILE | grep -e "UdpEchoClientApplication" -e "UdpEchoServerApplication" > $LOGFILEPARSED; python3 halow-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
    subprocess.check_output('cd NS3-802.11ah; rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

    lines = output.splitlines()
    line = lines[0]
    print(lines)
    i = 0
    while "Total" not in line:
        i = i + 1
        line = lines[i]
    energy = float(lines[i].split()[-1]) / simulation_time # Watts
    #battery_lifetime = float(lines[i+1].split()[-1])
    #throughput = float(lines[i+2].split()[-1])
    success_rate = float(lines[i+3].split()[-1])
    latency = float(latency) * 1000

    if environment == "rural":
        environment_id = 1
    elif environment == "urban":
        environment_id = 2
    elif environment == "suburban":
        environment_id = 3
    elif environment == "indoor":
        environment_id = 4

    with open(output_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nED, period, size, distance, nGW, environment_id, mcs, sgi, beacon_interval, nraw_groups, success_rate, energy, latency])

"""
for nED in nED_list:
    for period in period_list:
        for size in size_list:
            for distance in distance_list:
                for nGW in nGW_list:
                    for environment in environment_list:
                        for sf in SF_list:
                            for traffic_type in traffic_type_list:
                                for coding_rate in coding_rate_list:
                                    for bandwidth in bandwidth_list:
                                        for crc in CRC_list:
                                            simulation_time = 10 * period # 10 packets are sent                                       
                                            
                                            os.environ['SF'] = str(sf)
                                            os.environ['CODINGRATE'] = str(coding_rate)
                                            os.environ['CRC'] = str(crc)
                                            os.environ['TRAFFIC'] = str(traffic_type)
                                            os.environ['NGW'] = str(nGW)
                                            os.environ['NBDEVICES'] = str(nED)

                                            os.environ['DISTANCE'] = str(distance)
                                            os.environ['PACKETSIZE'] = str(size)
                                            os.environ['PERIOD'] = str(period)
                                            os.environ['RADIOENVIRONMENT'] = str(environment)

                                            os.environ['SIMULATION_TIME'] = str(simulation_time)
                                            os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
                                            os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

                                            os.environ['LOGFILE'] = "log-"+str(sf)+"-"+str(coding_rate)+"-"+str(traffic_type)+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"
                                            os.environ['LOGFILEPARSED'] = "log-parsed-"+str(sf)+"-"+str(coding_rate)+"-"+str(traffic_type)+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"

                                            output = subprocess.check_output('./waf --run "scratch/lora-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGateways=$NGW --trafficType=$TRAFFIC --SF=$SF --codingRate=$CODINGRATE --crc=$CRC --distance=$DISTANCE --simulationTime=$SIMULATION_TIME --nSta=$NBDEVICES --payloadSize=$PACKETSIZE --period=$PERIOD" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                                            output = output + "Energy consumption: " + subprocess.check_output("cat $LOGFILE | grep -e 'LoraRadioEnergyModel:Total energy consumption' | tail -1 | awk 'NF>1{print $NF}' | sed 's/J//g'", shell=True, text=True,stderr=subprocess.DEVNULL)
                                            latency_ = subprocess.check_output(' cat $LOGFILE | grep -e "Total time" > $LOGFILEPARSED; python3 lora-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

                                            subprocess.check_output('rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                                            
                                            lines = output.splitlines()
                                            line = lines[0]
                                            i = 0
                                            while "Success" not in line:
                                                i = i + 1
                                                line = lines[i]
                                            success_rate = round(float(lines[i].split()[-1]), 2)
                                            energy = float(lines[i+2].split()[-1]) / simulation_time # Watts

                                            if traffic_type == "Unconfirmed":
                                                traffic_type = 0
                                            else:
                                                traffic_type = 1

                                            if environment == "rural":
                                                environment_id = 1
                                            elif environment == "urban":
                                                environment_id = 2
                                            elif environment == "suburban":
                                                environment_id = 3
                                            elif environment == "indoor":
                                                environment_id = 4

                                            with open(output_file, 'a', newline='') as file:
                                                writer = csv.writer(file)
                                                writer.writerow([nED, period, size, distance, nGW, environment_id, sf, traffic_type, coding_rate, bandwidth, crc, success_rate, energy])
"""