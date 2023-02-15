import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import viridis

from algo import TOPSISOptimizer

def dummy_objective_function(x):
	return np.array([np.linalg.norm(x - 0.5) ** 2, np.cos(np.linalg.norm(x))])

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

if __name__ == "__main__":
	# TODO: replace by the true domains
	in_dimensions = [
		(0.0, 1.0),
		(-1.0, 1.0)
	]

	# TODO: replace by the true objective function
	objective = dummy_objective_function

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
	optimizer = TOPSISOptimizer(in_dimensions, obs)

	# Optimization loop
	budget = 60
	for i in range(n_initial_obs + 1, budget + 1):
		query = optimizer.ask()
		label = objective(query)

		optimizer.tell(query, label)

		print(f"== STEP {i} ==")
		print(f"Queried: {query}")
		print(f"Objective values: {label}")
		print(f"TOPSIS reward: {optimizer._scalarized_yy[-1]}\n")

	# Let's plot some metrics
	alpha = 2.0 / (budget / 4.0 + 1.0)
	_, axes = plt.subplots(ncols=3)

	axes[0].scatter(optimizer._yy[:, 0], optimizer._yy[:, 1], c=viridis(np.arange(1, budget + 1) / budget))
	axes[0].set_xlabel("First objective")
	axes[0].set_ylabel("Second objective")
	axes[0].set_title("Optimization in output space")

	axes[1].scatter(range(1, budget+1), optimizer._scalarized_yy, c=viridis(np.arange(1, budget + 1) / budget))
	axes[1].plot(range(1, budget+1), exponential_moving_average(optimizer._scalarized_yy, alpha), alpha=0.3)
	axes[1].set_xlabel("Optimization step")
	axes[1].set_ylabel("TOPSIS objective")
	axes[1].set_title("TOPSIS objective w.r.t optimization step")

	queries = optimizer._xx
	distances = [np.linalg.norm(x1 - x2) for x1, x2 in zip(queries[1:], queries)]
	axes[2].scatter(range(2, budget+1), distances, c=viridis(np.arange(2, budget + 1) / budget))
	axes[2].plot(range(2, budget+1), exponential_moving_average(distances, alpha), alpha=0.3)
	axes[2].set_xlabel("Optimization step")
	axes[2].set_ylabel("Convergence $||x_{t+1} - x_{t}||_2$")
	axes[2].set_title("Convergence w.r.t optimization step")
	
	plt.show()