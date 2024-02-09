import numpy as np
import pandas as pd
import os
import subprocess
import time
import warnings
import csv

warnings.filterwarnings("ignore")

output_file_complete = "data/use-case-complete-3.csv"
output_file_sampling = "data/use-case-sampling-3.csv"

nED, period, size, distance, environment = 200, 600, 50, 8000, "suburban"

battery_capacity = 2300
battery_voltage = 3
PRICE_GW = 1000

def complete_research():
    coding_rate_list = [1, 2, 3, 4]
    nGW_list = [i for i in range(1,(nED//5)+1)]
    crc_list = [0, 1]
    sf_list = [7, 8, 9, 10, 11, 12]
    traffic_type_list = ["Unconfirmed", "Confirmed"]

    for coding_rate in coding_rate_list:
        for nGW in nGW_list:
            for crc in crc_list:
                for sf in sf_list:
                    for traffic_type in traffic_type_list:
                        simulation_time = period * 10

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

                        output = subprocess.check_output('cd NS3-6LoWPAN; ./waf --run "scratch/lora-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGateways=$NGW --trafficType=$TRAFFIC --SF=$SF --codingRate=$CODINGRATE --crc=$CRC --distance=$DISTANCE --simulationTime=$SIMULATION_TIME --nSta=$NBDEVICES --payloadSize=$PACKETSIZE --period=$PERIOD" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                        output = output + "Energy consumption: " + subprocess.check_output("cd NS3-6LoWPAN; cat $LOGFILE | grep -e 'LoraRadioEnergyModel:Total energy consumption' | tail -1 | awk 'NF>1{print $NF}' | sed 's/J//g'", shell=True, text=True,stderr=subprocess.DEVNULL)
                        latency_ = subprocess.check_output('cd NS3-6LoWPAN; cat $LOGFILE | grep -e "Total time" > $LOGFILEPARSED; python3 lora-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

                        subprocess.check_output('cd NS3-6LoWPAN; rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                            
                        lines = output.splitlines()
                        line = lines[0]
                        i = 0
                        while "Success" not in line:
                            i = i + 1
                            line = lines[i]
                        success_rate = round(float(lines[i].split()[-1]), 2)
                        energy = float(lines[i+2].split()[-1]) / simulation_time # Watts
                        latency = float(latency_) * 1000
                        price = nGW * PRICE_GW

                        #result = success_rate/100 - energy/0.002964 - latency/3809.28 - price/10000

                        if traffic_type == "Unconfirmed":
                            traffic_type_text = 0
                        else:
                            traffic_type_text = 1

                        with open(output_file_complete, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([nGW,sf,traffic_type_text,coding_rate,crc,success_rate,energy,latency,price])

    return

def sampling_research():
    coding_rate_list = [1, 4]
    nGW_list = [i for i in range(1,(nED//5)+1,2)]
    crc_list = [0, 1]
    sf_list = [7, 9, 12]
    traffic_type_list = ["Unconfirmed", "Confirmed"]

    for coding_rate in coding_rate_list:
        for nGW in nGW_list:
            for crc in crc_list:
                for sf in sf_list:
                    for traffic_type in traffic_type_list:
                        simulation_time = period * 10

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

                        output = subprocess.check_output('cd NS3-6LoWPAN; ./waf --run "scratch/lora-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGateways=$NGW --trafficType=$TRAFFIC --SF=$SF --codingRate=$CODINGRATE --crc=$CRC --distance=$DISTANCE --simulationTime=$SIMULATION_TIME --nSta=$NBDEVICES --payloadSize=$PACKETSIZE --period=$PERIOD" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                        output = output + "Energy consumption: " + subprocess.check_output("cd NS3-6LoWPAN; cat $LOGFILE | grep -e 'LoraRadioEnergyModel:Total energy consumption' | tail -1 | awk 'NF>1{print $NF}' | sed 's/J//g'", shell=True, text=True,stderr=subprocess.DEVNULL)
                        latency_ = subprocess.check_output('cd NS3-6LoWPAN; cat $LOGFILE | grep -e "Total time" > $LOGFILEPARSED; python3 lora-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

                        subprocess.check_output('cd NS3-6LoWPAN; rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                            
                        lines = output.splitlines()
                        line = lines[0]
                        i = 0
                        while "Success" not in line:
                            i = i + 1
                            line = lines[i]
                        success_rate = round(float(lines[i].split()[-1]), 2)
                        energy = float(lines[i+2].split()[-1]) / simulation_time # Watts
                        latency = float(latency_) * 1000
                        price = nGW * PRICE_GW

                        #result = success_rate/100 - energy/0.002964 - latency/3809.28 - price/10000

                        if traffic_type == "Unconfirmed":
                            traffic_type_text = 0
                        else:
                            traffic_type_text = 1

                        with open(output_file_sampling, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([nGW,sf,traffic_type_text,coding_rate,crc,success_rate,energy,latency,price])

    return

print("Use case: ", nED, period, size, distance, environment)
start = time.time()
complete_research()
print("Complete research time: ", time.time()-start)

start = time.time()
sampling_research()
print("Sampling research time: ", time.time()-start)