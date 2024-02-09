import numpy as np
import pandas as pd
import os
import subprocess
import time
import warnings
import csv

warnings.filterwarnings("ignore")

output_file_complete = "data-wifi/use-case-complete-reconfiguration.csv"
output_file_sampling = "data-wifi/use-case-sampling-reconfiguration.csv"

#nED, period, size, distance, environment = 50, 0.01, 1000, 200, "suburban"

size, distance, environment = 1000, 200, "suburban"

battery_capacity = 2300
battery_voltage = 3
PRICE_GW = 100

def complete_research():
    mcs_list = [i for i in range(0,10)]
    spatial_stream_list = [1, 2, 3]
    agregation_list = [0, 1]
    sgi_list = [0, 1]
    period_list = [0.005, 0.004, 0.003, 0.002]
    nED_list = [30, 40, 50]
    
    
    for nED in nED_list:
        nGW_list = [i for i in range(1,(nED//5)+1)]
        for period in period_list:
            for nGW in nGW_list:
                for mcs in mcs_list:
                    for agregation in agregation_list:
                        for spatial_streams in spatial_stream_list:
                            for sgi in sgi_list:
                                simulation_time = 1 # Second

                                os.environ['MCS'] = str(mcs)
                                os.environ['SGI'] = str(sgi)
                                os.environ['SPATIALSTREAMS'] = str(spatial_streams)
                                os.environ['AGREGATION'] = str(agregation)

                                os.environ['NGW'] = str(nGW)
                                os.environ['NBDEVICES'] = str(nED)
                                os.environ['DISTANCE'] = str(distance)
                                os.environ['PACKETSIZE'] = str(size)
                                os.environ['PERIOD'] = str(period)
                                os.environ['RADIOENVIRONMENT'] = str(environment)

                                os.environ['SIMULATION_TIME'] = str(simulation_time)
                                os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
                                os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

                                os.environ['LOGFILE'] = "log-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+"-complete"+".txt"
                                os.environ['LOGFILEPARSED'] = "log-parsed"+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+"-complete"+".txt"

                                output = subprocess.check_output('cd NS3-6LoWPAN; ./waf --run "scratch/wifi-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGW=$NGW --agregation=$AGREGATION --sgi=$SGI --spatialStreams=$SPATIALSTREAMS --simulationTime=$SIMULATION_TIME --nWifi=$NBDEVICES --period=$PERIOD --payloadSize=$PACKETSIZE --batteryCap=$BATTERY_CAPACITY --voltage=$BATTERY_VOLTAGE" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                                try:
                                    latency = subprocess.check_output('cd NS3-6LoWPAN; cat $LOGFILE | grep -e "UdpEchoClientApplication" -e "UdpEchoServerApplication" > $LOGFILEPARSED; python3 wifi-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                                except:
                                    latency = 100
                                subprocess.check_output('cd NS3-6LoWPAN; rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                                
                                lines = output.splitlines()
                                line = lines[0]
                                #print(lines)
                                i = 0
                                while "Total" not in line:
                                    i = i + 1
                                    line = lines[i]
                                energy = float(lines[i].split()[-1]) / simulation_time # Watts
                                success_rate = float(lines[i+3].split()[-1])
                                latency = float(latency) * 1000
                                price = PRICE_GW * nGW

                                #result = success_rate/100 - energy/0.002964 - latency/3809.28 - price/10000

                                with open(output_file_complete, 'a', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow([nED,period,nGW,mcs,agregation,spatial_streams,sgi,success_rate,energy,latency,price])

    return

def sampling_research():
    mcs_list = [0, 5, 9]
    spatial_stream_list = [1, 3]
    agregation_list = [0, 1]
    sgi_list = [0, 1]
    
    period_list = [0.005, 0.004, 0.003, 0.002]
    nED_list = [30, 40, 50]
    
    
    for nED in nED_list:
        nGW_list = [i for i in range(1,(nED//5)+1)]
        for period in period_list:
            for nGW in nGW_list:
                for mcs in mcs_list:
                    for agregation in agregation_list:
                        for spatial_streams in spatial_stream_list:
                            for sgi in sgi_list:
                                simulation_time = 1

                                os.environ['MCS'] = str(mcs)
                                os.environ['SGI'] = str(sgi)
                                os.environ['SPATIALSTREAMS'] = str(spatial_streams)
                                os.environ['AGREGATION'] = str(agregation)

                                os.environ['NGW'] = str(nGW)
                                os.environ['NBDEVICES'] = str(nED)
                                os.environ['DISTANCE'] = str(distance)
                                os.environ['PACKETSIZE'] = str(size)
                                os.environ['PERIOD'] = str(period)
                                os.environ['RADIOENVIRONMENT'] = str(environment)

                                os.environ['SIMULATION_TIME'] = str(simulation_time)
                                os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
                                os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

                                os.environ['LOGFILE'] = "log-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+"-sampling"+".txt"
                                os.environ['LOGFILEPARSED'] = "log-parsed"+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+"-sampling"+".txt"

                                output = subprocess.check_output('cd NS3-6LoWPAN; ./waf --run "scratch/wifi-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGW=$NGW --agregation=$AGREGATION --sgi=$SGI --spatialStreams=$SPATIALSTREAMS --simulationTime=$SIMULATION_TIME --nWifi=$NBDEVICES --period=$PERIOD --payloadSize=$PACKETSIZE --batteryCap=$BATTERY_CAPACITY --voltage=$BATTERY_VOLTAGE" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                                
                                try:
                                    latency = subprocess.check_output('cd NS3-6LoWPAN; cat $LOGFILE | grep -e "UdpEchoClientApplication" -e "UdpEchoServerApplication" > $LOGFILEPARSED; python3 wifi-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                                except:
                                    latency = 100
                                
                                subprocess.check_output('cd NS3-6LoWPAN; rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                                
                                lines = output.splitlines()
                                line = lines[0]
                                #print(lines)
                                i = 0
                                while "Total" not in line:
                                    i = i + 1
                                    line = lines[i]
                                energy = float(lines[i].split()[-1]) / simulation_time # Watts
                                success_rate = float(lines[i+3].split()[-1])
                                latency = float(latency) * 1000
                                price = PRICE_GW * nGW

                                #result = success_rate/100 - energy/0.002964 - latency/3809.28 - price/10000

                                with open(output_file_sampling, 'a', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow([nED,period,nGW,mcs,agregation,spatial_streams,sgi,success_rate,energy,latency,price])

    return

#print("Use case: ", nED, period, size, distance, environment)
#start = time.time()
#complete_research()
#print("Complete research time: ", time.time()-start)

start = time.time()
sampling_research()
print("Sampling research time: ", time.time()-start)