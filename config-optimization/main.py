import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.cm import viridis
import os
import subprocess
import time
import csv

matplotlib.use('TkAgg',force=True)
from algo import TOPSISOptimizer, RandomConvexCombinationsOptimizer

# Global variables
nED, period, size, distance, environment = 50, 1, 100, 200, "suburban"
battery_capacity = 2300
battery_voltage = 3
PRICE_GW = 100
budget = 200
filepath = "BO_results_pareto.tsv"

def dummy_objective_function(x):
	return np.array([np.linalg.norm(x - 0.5) ** 2, np.cos(np.linalg.norm(x)), np.sin(np.linalg.norm(x))])

def simulation(x):
	"""
	x format: [NGW, frame_retries, csma_backoff, max_be, min_be]
	"""
	nGW = x[0]
	frame_retries = x[1]
	csma_backoff = x[2]
	max_be = x[3]
	min_be = x[4]
	simulation_time = 10 * period

	os.environ['NGW'] = str(nGW)
	os.environ['MAXFRAMERETRIES'] = str(frame_retries)
	os.environ['CSMABACKOFF'] = str(csma_backoff)
	os.environ['MAXBE'] = str(max_be)
	os.environ['MINBE'] = str(min_be)
   
	os.environ['NBDEVICES'] = str(nED)
	os.environ['DISTANCE'] = str(distance)
	os.environ['PACKETSIZE'] = str(size)
	os.environ['PERIOD'] = str(period)
	os.environ['RADIOENVIRONMENT'] = str(environment)

	os.environ['SIMULATION_TIME'] = str(simulation_time)
	os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
	os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

	os.environ['LOGFILE'] = "log-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"
	os.environ['LOGFILEPARSED'] = "log-parsed-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"

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
	
	return np.array([success_rate,-energy,-latency,-price]) # Negative value for criteria which need to be minimized


def exponential_moving_average(yy, alpha):
	# EMA
	weights = []
	ema = []
	for i,y in enumerate(yy):
		if weights != []:
			weights = list((1 - alpha) * np.array(weights))
		weights.append(1)
		ema.append(np.ma.average(yy[:i+1], weights=weights))

	return ema

def visualize(xx, yy, yy_scalarized=[], objective_indices=range(3)):
	# Let's plot some metrics
	alpha = 2.0 / (budget / 4.0 + 1.0)
	fig = plt.figure()
	show_yy_scalarized = len(yy_scalarized) > 0

	n_subplots = 2 + int(show_yy_scalarized)
	axes = [fig.add_subplot(1, n_subplots, 1, projection='3d'), fig.add_subplot(1, n_subplots, 2)]
	if show_yy_scalarized:
		axes.append(fig.add_subplot(1, n_subplots, 3))
	
	axes[0].scatter(yy[:, objective_indices[0]], yy[:, objective_indices[1]], yy[:, objective_indices[2]], c=viridis(np.arange(1, budget + 1) / budget))
	axes[0].set_xlabel("First objective")
	axes[0].set_ylabel("Second objective")
	axes[0].set_zlabel("Third objective")
	axes[0].set_title("Optimization in output space")

	distances = [np.linalg.norm(x1 - x2) for x1, x2 in zip(xx[1:], xx)]
	axes[1].scatter(range(2, budget+1), distances, c=viridis(np.arange(2, budget + 1) / budget))
	axes[1].plot(range(2, budget+1), exponential_moving_average(distances, alpha), alpha=0.3)
	axes[1].set_xlabel("Optimization step")
	axes[1].set_ylabel("Convergence $||x_{t+1} - x_{t}||_2$")
	axes[1].set_title("Convergence w.r.t optimization step")

	if show_yy_scalarized:
		axes[2].scatter(range(1, budget+1), yy_scalarized, c=viridis(np.arange(1, budget + 1) / budget))
		axes[2].plot(range(1, budget+1), exponential_moving_average(yy_scalarized, alpha), alpha=0.3)
		axes[2].set_xlabel("Optimization step")
		axes[2].set_ylabel("TOPSIS objective")
		axes[2].set_title("TOPSIS objective w.r.t optimization step")
	
	plt.show()

def read_datafile(filepath):
	xx, yy, yy_scalarized = [], [], []
	with open(filepath) as fd:
		rd = csv.reader(fd, delimiter="\t")
		first = True
		for row in rd:
			if first:
				first = False
				continue

			xx.append(eval(row[0]))
			yy.append(eval(row[1]))
			if len(row) > 2:
				yy_scalarized.append(eval(row[2]))

	return np.array(xx), np.array(yy), np.array(yy_scalarized)

if __name__ == "__main__":
	# TODO: replace by the true domains
	# in_dimensions = [
	# 	(0.0, 1.0),
	# 	(-1.0, 1.0),
	# 	(0.0, 1.0)
	# ]

	# Reading the previous datafile
	xx, yy, yy_scalarized = read_datafile(filepath)
	visualize(xx, yy, yy_scalarized, objective_indices=[0, 1, 3])

	rounding = True
	in_dimensions = [
		(1.0, nED//5),
		(0.0, 7.0),
		(0.0, 5.0),
		(3.0, 8.0),
		(0.0, 7.0)
	]

	# TODO: replace by the true objective function
	# objective = dummy_objective_function
	objective = simulation

	# Dummy collection of observations
	obs = []
	for _ in range(2):
		x = []
		for min_x,max_x in in_dimensions:
			x.append(np.random.uniform(min_x, max_x))
		y = objective(np.array(x))

		obs.append((np.array(x), np.array(y)))

	# Initialize the model
	n_initial_obs = len(obs)
	# optimizer = TOPSISOptimizer(in_dimensions, obs)
	coeffs_dimensions = [
	 	(0.7, 0.8),
		 (0.7, 0.8),
	 	(0.0, 0.0),
		 (0.2,0.3)
	 ]
	optimizer = RandomConvexCombinationsOptimizer(in_dimensions, coeffs_dimensions, obs)

	# Optimization loop
	start = time.time()
	for i in range(n_initial_obs + 1, budget + 1):
		query = optimizer.ask()

		# Round
		if rounding:
			for j,elem in enumerate(query):
				query[j] = round(elem)
		label = objective(query)

		optimizer.tell(query, label)

		print(f"== STEP {i} ==")
		print(f"Queried: {query}")
		print(f"Objective values: {label}")
		print(f"Scalarized reward: {optimizer._scalarized_yy[-1]}\n")

	print("== Saving the results... ==\n")
	optimizer.save(filepath)

	# Recommended configuration
	# idx, xbest, topsisbest, obj_best = optimizer.recommended()
	# print("== FINAL RESULTS ==")
	# print(f"Recommended configuration: {xbest}")
	# print(f"Objective values: {obj_best}")
	# print(f"TOPSIS reward: {topsisbest}")
	# print(f"Index: {idx}")
	# print(f"Execution time: {time.time()-start} seconds")

	visualize(optimizer._xx, optimizer._yy, optimizer._scalarized_yy, objective_indices=[0, 1, 3])