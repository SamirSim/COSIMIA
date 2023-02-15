import numpy as np
import pandas as pd
import os
import subprocess
import time
import warnings
import csv

warnings.filterwarnings("ignore")

#output_file_complete = "data-6lowpan/use-case-complete-1-seed-3.csv"
output_file_sampling = "data-6lowpan/use-case-sampling-1-seed-0.csv"

nED, period, size, distance, environment = 50, 1, 100, 200, "suburban"

battery_capacity = 2300
battery_voltage = 3
PRICE_GW = 100

def complete_research():
    frame_retries_list = [i for i in range(0,8)]
    csma_backoff_list = [i for i in range(0,6)]
    max_be_list = [i for i in range(3,9)]
    min_be_list = [i for i in range(0,8)]
    nGW_list = [i for i in range(1,(nED//5)+1)]

    for nGW in nGW_list:
        for frame_retries in frame_retries_list:
            for csma_backoff in csma_backoff_list:
                for max_be in max_be_list:
                    for min_be in min_be_list:
                        simulation_time = 10 # Second

                        os.environ['MAXFRAMERETRIES'] = str(frame_retries)
                        os.environ['CSMABACKOFF'] = str(csma_backoff)
                        os.environ['MAXBE'] = str(max_be)
                        os.environ['MINBE'] = str(min_be)

                        os.environ['NGW'] = str(nGW)
                        os.environ['NBDEVICES'] = str(nED)
                        os.environ['DISTANCE'] = str(distance)
                        os.environ['PACKETSIZE'] = str(size)
                        os.environ['PERIOD'] = str(period)
                        os.environ['RADIOENVIRONMENT'] = str(environment)

                        os.environ['SIMULATION_TIME'] = str(simulation_time)
                        os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
                        os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

                        os.environ['LOGFILE'] = "log-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"
                        os.environ['LOGFILEPARSED'] = "log-parsed"+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"
                        
                        output = subprocess.check_output('cd NS3-6LoWPAN; ./waf --run "scratch/6lowpan-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGW=$NGW --maxFrameRetries=$MAXFRAMERETRIES --max_BE=$MAXBE --min_BE=$MINBE --csma_backoffs=$CSMABACKOFF --distance=$DISTANCE --simulationTime=$SIMULATION_TIME --nSta=$NBDEVICES --packetSize=$PACKETSIZE --period=$PERIOD --capacity=$BATTERY_CAPACITY --voltage=$BATTERY_VOLTAGE" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                        
                        try:
                            latency_ = subprocess.check_output('cd NS3-6LoWPAN; cat $LOGFILE | grep -e "client sent 50 bytes" -e "server received 50 bytes from" > $LOGFILEPARSED; python3 wifi-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                        except:
                            latency_ = 1000
                        subprocess.check_output('cd NS3-6LoWPAN; rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

                        lines = output.splitlines()
                        line = lines[0]

                        #print(lines)
                        i = 0
                        while "Total" not in line:
                            i = i + 1
                            line = lines[i]
                        energy = float(lines[i].split()[-1])
                        success_rate = float(lines[i+3].split()[-1])
                        latency = float(latency_) * 1000
                        price = PRICE_GW * nGW

                        #result = success_rate/100 - energy/0.002964 - latency/3809.28 - price/10000

                        with open(output_file_complete, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([nGW,max_be, min_be, csma_backoff, frame_retries,success_rate,energy,latency,price])

    return

def sampling_research():
    frame_retries_list = [0, 8]
    csma_backoff_list = [0, 6]
    max_be_list = [3, 9]
    min_be_list = [0, 8]
    nGW_list = [i for i in range(1,(nED//5)+1,2)]

    for nGW in nGW_list:
        for frame_retries in frame_retries_list:
            for csma_backoff in csma_backoff_list:
                for max_be in max_be_list:
                    for min_be in min_be_list:
                        simulation_time = 10 # Second

                        os.environ['MAXFRAMERETRIES'] = str(frame_retries)
                        os.environ['CSMABACKOFF'] = str(csma_backoff)
                        os.environ['MAXBE'] = str(max_be)
                        os.environ['MINBE'] = str(min_be)

                        os.environ['NGW'] = str(nGW)
                        os.environ['NBDEVICES'] = str(nED)
                        os.environ['DISTANCE'] = str(distance)
                        os.environ['PACKETSIZE'] = str(size)
                        os.environ['PERIOD'] = str(period)
                        os.environ['RADIOENVIRONMENT'] = str(environment)

                        os.environ['SIMULATION_TIME'] = str(simulation_time)
                        os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
                        os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

                        os.environ['LOGFILE'] = "log-seed-3-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"
                        os.environ['LOGFILEPARSED'] = "log-parsedseed-3"+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"

                        output = subprocess.check_output('cd NS3-6LoWPAN; ./waf --run "scratch/6lowpan-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGW=$NGW --maxFrameRetries=$MAXFRAMERETRIES --max_BE=$MAXBE --min_BE=$MINBE --csma_backoffs=$CSMABACKOFF --distance=$DISTANCE --simulationTime=$SIMULATION_TIME --nSta=$NBDEVICES --packetSize=$PACKETSIZE --period=$PERIOD --capacity=$BATTERY_CAPACITY --voltage=$BATTERY_VOLTAGE" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                        
                        try:
                            latency_ = subprocess.check_output('cd NS3-6LoWPAN; cat $LOGFILE | grep -e "client sent 50 bytes" -e "server received 50 bytes from" > $LOGFILEPARSED; python3 wifi-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                        except:
                            latency_ = 1000
                        subprocess.check_output('cd NS3-6LoWPAN; rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

                        lines = output.splitlines()
                        line = lines[0]

                        #print(lines)
                        i = 0
                        while "Total" not in line:
                            i = i + 1
                            line = lines[i]
                        energy = float(lines[i].split()[-1])
                        success_rate = float(lines[i+3].split()[-1])
                        latency = float(latency_) * 1000
                        price = PRICE_GW * nGW

                        #result = success_rate/100 - energy/0.002964 - latency/3809.28 - price/10000

                        with open(output_file_sampling, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([nGW,max_be, min_be, csma_backoff, frame_retries,success_rate,energy,latency,price])

    return

print("Use case: ", nED, period, size, distance, environment)
#start = time.time()
#complete_research()
#print("Complete research time: ", time.time()-start)

start = time.time()
sampling_research()
print("Sampling research time (seed 0): ", time.time()-start)