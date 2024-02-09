from math import dist
import os
import subprocess
import sys
import csv

output_file = "5g-experience.csv"

battery_capacity = 2300
battery_voltage = 3

alternatives = [[50, 0.02, 5000, 10, "rural"],
                [5, 0.02, 5000, 50, "rural"],
                [5, 0.002, 5000, 50, "rural",],
                [50, 0.002, 100, 50, "rural"],
                [5, 0.02, 100, 10, "rural"],
                [50, 0.002, 5000, 10, "rural"],
                [50, 0.02, 100, 50, "rural"],
                [5, 0.002, 100, 10, "rural"], 
                [50, 0.02, 5000, 10, "urban"],
                [5, 0.02, 5000, 50, "urban"],
                [5, 0.002, 5000, 50, "urban",],
                [50, 0.002, 100, 50, "urban"],
                [5, 0.02, 100, 10, "urban"],
                [50, 0.002, 5000, 10, "urban"],
                [50, 0.02, 100, 50, "urban"],
                [5, 0.002, 100, 10, "urban"]
                ]


numerology = 3
nGW = 1
trafficDirection = "upstream"

for nED, period, size, distance, environment in alternatives:
    simulation_time = period * 10

    os.environ['NUMEROLOGY'] = str(numerology)

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

    output = subprocess.check_output('cd NS3-5G; ./waf --run "scratch/5g-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --numEnb=$NGW --numerology=$NUMEROLOGY --simulationTime=$SIMULATION_TIME --numSta=$NBDEVICES --trafficDirection=$TRAFFICDIR --interPacketInterval=$PERIOD --payloadSize=$PACKETSIZE --batteryCap=$BATTERY_CAPACITY --voltage=$BATTERY_VOLTAGE" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
    latency_ = subprocess.check_output('cd NS3-5G; cat $LOGFILE | grep -e "client sent 100 bytes" -e "server received 100 bytes from" > $LOGFILEPARSED; python3 wifi-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
    #subprocess.check_output('cd NS3-5G; rm $LOGFILE"; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

    lines = output.splitlines()
    line = lines[0]
    print(lines)
    i = 0
    while "Total" not in line:
        i = i + 1
        line = lines[i]
    energy = float(lines[i].split()[-1])
    success_rate = float(lines[i+3].split()[-1])
    latency = float(latency_) * 1000

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
        writer.writerow([nED, period, size, distance, nGW, environment_id, numerology, success_rate, energy, latency])

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