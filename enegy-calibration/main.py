from scipy.integrate import simpson
import numpy as np
from numpy import trapz
import pandas as pd
import matplotlib.pyplot as plt

VOLTAGE = 3

def get_total_energy_expe(file):
	with open("oml-plot-tools/"+file) as fp:
		for _ in range(10):
			line = fp.readline()
		times = []
		while line:
			times.append(float(line.split()[5]))
			line = fp.readline()
	#print (times)

	y = np.array(times)
	#area = simpson(y, dx=0.065788) # Sampling period = 65.788 ms
	area = simpson(y, dx=0.00112) # Sampling period = 1.12 ms
	return area

def get_total_energy_simu():
	with open("energy-states-parsed.txt") as fp:
		line = fp.readline()
		energy = 0
		while line:
			energy = energy + (float(line.split()[3]) * float(line.split()[4]) * float(line.split()[5]))
			#if float(line.split()[3]) == 0:
				#print(line.split()[-1])
			line = fp.readline()
		return energy

def generate_energy_samples_expe(period): # period in seconds
	with open("oml-plot-tools/m3_73.oml") as fp:
		for _ in range(10):
			line = fp.readline()
		energy_samples = []
		area = 0
		while line:
			current_time = float(line.split()[3]) + (float(line.split()[4])/1000000)
			#print(current_time)
			times = []
			#print(float(line.split()[3]+'.'+line.split()[4]), current_time + period)
			while line and (float(line.split()[3]) + (float(line.split()[4])/1000000) <= current_time + period):
				times.append(float(line.split()[5]))
				line = fp.readline()
			y = np.array(times)
			#print(current_time, y)
			area = simpson(y, dx=0.065788) # Sampling period = 65.788 ms
			energy_samples.append(area)
			#print(y)
		return energy_samples

def generate_times_simu(period): # period in seconds
	with open("log-states-40.txt") as fp:
		line = fp.readline()
		times = []
		while line: 
			#print(line)
			current_time = float(line.split()[0].lstrip("+").replace("s",""))
			tx_time, rx_time, busy_tx_time, busy_rx_time, trx_switch_time = 0, 0, 0, 0, 0
			while line and float(line.split()[0].lstrip("+").replace("s","")) < current_time + period:
				if line.split()[-1] == "Tx":
					tx_time = tx_time + float(line.split()[3])
					#if tx_time != 0:
						#print(tx_time, line)
				elif line.split()[-1] == "Rx":
					rx_time = rx_time + float(line.split()[3])
				elif line.split()[-1] == "Trx-switch":
					trx_switch_time = trx_switch_time + float(line.split()[3])
				elif line.split()[-1] == "Busy-Rx":
					busy_rx_time = busy_rx_time + float(line.split()[3])
				elif line.split()[-1] == "Busy-Tx":
					busy_tx_time = busy_tx_time + float(line.split()[3])
				line = fp.readline()
			#print(rx_time)
			times.append([tx_time, rx_time, busy_tx_time, busy_rx_time, trx_switch_time]) 
		return times
	
def generate_energy_samples_simu(period): # period in seconds
	with open("energy-states-parsed-total.txt") as fp:
		line = fp.readline()
		energy_samples = []
		energy, old, cur = 0, 0, 0
		while line: 
			#print(line)
			current_time = float(line.split()[0].lstrip("+").replace("s",""))
			while line and float(line.split()[0].lstrip("+").replace("s","")) < current_time + period:
				cur = float(line.split()[-1].replace("J", ""))
				line = fp.readline()
			energy = cur - old
			old = cur
			energy_samples.append(energy)
		return energy_samples
	
def generate_energy_simu(period, file): # period in seconds
	with open(file) as fp:
		line = fp.readline()
		energy_samples = []
		energy, old, cur = 0, 0, 0
		while line: 
			#print(line)
			current_time = float(line.split()[0].lstrip("+").replace("s",""))
			while line and float(line.split()[0].lstrip("+").replace("s","")) < current_time + period:
				cur = float(line.split()[-1].replace("J", ""))
				line = fp.readline()
			energy_samples.append(cur)
		return energy_samples
	
print("No transmission: ", get_total_energy_expe("m3_53-no-transmission.oml"))
print("1 packet/s: ", get_total_energy_expe("m3_53.oml"))
print("10 packets/s: ", get_total_energy_expe("m3_53-more-transmission.oml"))
print("100 packets/s: ", get_total_energy_expe("m3_53-ultra-transmission.oml"))

"""
print(get_total_energy_simu())

times = generate_times_simu(1)
#print(len(times))

energy_samples_expe = generate_energy_samples_expe(1)
print(len(energy_samples_expe))
#print(energy_samples_expe)

data = []
i = 0
for elem in times:
	try:
		elem.append(energy_samples_expe[i])
		#print(elem)
		data.append(elem)
		i = i + 1
	except:
		pass

#print(data)

df = pd.DataFrame(data, columns=["tx", "rx", "busy-tx", "busy-rx", "trx-switch", "energy"])
df = df.apply(lambda x : x * VOLTAGE if x.name in ["tx", "rx", "busy-tx", "busy-rx", "trx-switch"] else x)
df.to_csv('data-40.csv', index=False)
"""