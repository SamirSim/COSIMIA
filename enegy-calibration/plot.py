from scipy.integrate import simpson
import numpy as np
from numpy import trapz
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
#sns.set_style("whitegrid")

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
	area = simpson(y, dx=0.065788) # Sampling period = 65.788 ms
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

def generate_energy_samples_expe(period, file): # period in seconds
	with open("oml-plot-tools/"+file) as fp:
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
			area = area + simpson(y, dx=0.065788) # Sampling period = 65.788 ms
			# Changed it, was area = simpson... to get samples. Here the sum is calculated for plots
			energy_samples.append(area)
			#print(y)
		return energy_samples

def generate_times_simu(period): # period in seconds
	with open("energy-states-parsed.txt") as fp:
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

print(get_total_energy_expe("m3_73-40.oml"))

#print(get_total_energy_simu())

#times = generate_times_simu(1)
#print(len(times))

period = 1
max = 50

energy_samples_expe = generate_energy_samples_expe(period, "m3_73-40.oml")
#print(energy_samples_expe)

energy_samples_simu = generate_energy_simu(period, "log-parsed-40-calibrated.txt")
#print(energy_samples_simu)

energy_samples_simu_def = generate_energy_simu(period, "log-parsed-40-default.txt")
#print(len(energy_samples_simu_def))

x = np.arange(1, max+1, period)
limit = max//period

plt.scatter(x, energy_samples_expe[:limit], marker = 'x', linewidth = 5)
plt.scatter(x, energy_samples_simu[:limit], marker = 'o', linewidth = 0.03)
plt.scatter(x, energy_samples_simu_def[:limit], linewidth = 0.03)

plt.legend(["Real measures" , "After calibration", "Default"])
#plt.legend(["Real measures" , "After calibration"])

plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")

ax = plt.gca()
ax.set_axisbelow(True)
ax.yaxis.grid(color='gray', linestyle='dashed')
#ax.set_yscale("log")

plt.show()

"""
c = 2

l = np.arange(1, np.log(max)//c)
print(len(l))
exp = np.exp(l)

plt.scatter(exp, energy_samples_expe[:max], marker = 'x', linewidth = 5)
plt.scatter(exp, energy_samples_simu[:max], marker = 'o', linewidth = 0.3)
plt.scatter(exp, energy_samples_simu_def[:max], linewidth = 0.3)

plt.legend(["Real measures" , "After calibration", "Default"])
#plt.legend(["Real measures" , "After calibration"])

plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")

ax = plt.gca()
ax.set_xscale("log")

plt.show()
"""