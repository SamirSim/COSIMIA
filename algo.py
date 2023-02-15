import numpy as np
from abc import ABC, abstractmethod
from skopt import Optimizer
from skopt.learning.gaussian_process import kernels
from skopt.learning.gaussian_process.gpr import GaussianProcessRegressor

jitter = 1e-5

def listify(np2darray):
	return [list(l) for l in np2darray]

def topsis(y, mins, maxs):
	"""TOPSIS scalarization for the multi-objective problem.

	Assumptions:
			all objective values are normalized in [0, 1]
			larger is better

	Args:
			y (np.array): a vector of normalized (in [0, 1]) objective function values

	Returns:
			float: a single objective value, lower is better
	"""
	norm_mins = np.linalg.norm(y - mins)
	return norm_mins / (norm_mins + np.linalg.norm(maxs - y))

class BOOptimizer(ABC):
	"""Abstract BO Optimization class. Describe the interface for a BO algorithm.
	All BO classes *must* inherit this one.
	"""
	def __init__(self, in_dimensions, out_nd):
		"""Init the BO Optimizer attributes.

		Args:
				in_dimensions (list): List of tuples describing the dimensions of the
					input space with the format
					```[(x1_min, x1_max), ..., (xd_min, xd_max)]```.
				out_nd (int): Number of objective functions (i.e. dimension of the
					output space)
		"""
		self._in_nd = len(in_dimensions)
		self._in_dimensions = in_dimensions
		self._out_nd = out_nd

	@abstractmethod
	def ask(self):
		"""Compute the next query for the objective function to maximize.
		"""
		...

	@abstractmethod
	def tell(self, x, y):
		"""Update the BO algorithm with the observation of a new couple (x, y).

		Args:
				x (np.array): the query in the input space
				y (np.array): the associated objective value(s) in the output space
		"""
		...

	@abstractmethod
	def recommended(self):
		"""Return the recommended configuration among the previously observed ones

		Returns:
				tuple: metrics regarding the recommended configuration among
					the previously observed ones
		"""
		...
	
	@abstractmethod
	def save(self, path):
		"""Save the configurations and the objective values / scalarization into a
		tsv file.

		Args:
				path (str): filepath
		"""

class TOPSISOptimizer(BOOptimizer):
	"""Multi-objective optimizer maximizing a scalarization equivalent to the
	TOPSIS scalarization.
	"""
	def __init__(self, in_dimensions, first_observations, nu=3/2):
		"""Init the TOPSIS optimizer

		Args:
				in_dimensions (list): List of tuples describing the dimensions of the
					input space with the format
					```[(x1_min, x1_max), ..., (xd_min, xd_max)]```.
				first_observations (list): List of tuples describing first observations
					with the format ```[(x1, y1), ..., (xn, yn)]```. There must be at
					least 2 tuples in the list.
				nu (float, optional): Nu hyperparameter for the Matérn kernel. Defaults
					to 3/2.
		"""
		# Init the abstract parent class
		super().__init__(in_dimensions, first_observations[0][1].shape[0])

		self._nu = nu

		# Build the dataset attributes
		self._xx = np.array([x for x,_ in first_observations])
		self._yy = np.array([y for _,y in first_observations])

		self.normalize()
		self.scalarize()

	def normalize(self):
		"""L2 normalization of the objective values in the _yy attribute

		Returns:
				np.array: the objective values normalized
		"""
		normalization_weights = np.array([1.0 / np.linalg.norm(self._yy[:, i]) for i in range(self._yy.shape[1])])

		self._normalized_yy = np.multiply(self._yy, normalization_weights)

		return self._normalized_yy

	def scalarize(self):
		"""Scalarize the normalized objective values in the _yy_normalized
		attribute.

		Returns:
				np.array: the objective values scalarized with TOPSIS
		"""
		mins = np.min(self._normalized_yy, axis=0)
		maxs = np.max(self._normalized_yy, axis=0)
		self._scalarized_yy = np.array([topsis(y, mins, maxs) for y in self._normalized_yy])
		return self._scalarized_yy

	def ask(self):
		"""Learn a Gaussian Process and return a promising query.

		Returns:
				np.array: a vector of the input space
		"""
		# Init the model : Gaussian Process with local maximization algorithm, Matern kernel and white noise
		self._kernel = kernels.ConstantKernel() * kernels.Matern(nu=self._nu) + kernels.WhiteKernel()
		self._optimizer = Optimizer(self._in_dimensions, base_estimator=GaussianProcessRegressor(self._kernel, n_restarts_optimizer=15), acq_func="LCB", acq_optimizer="lbfgs", n_initial_points=2)
		
		self._optimizer.tell(listify(self._xx), list(-self._scalarized_yy))
		return np.array(self._optimizer.ask())

	def tell(self, x, y):
		"""Handle a new query.

		Args:
				x (np.array): the input query
				y (np.array): the observed objective values
		"""
		self._xx = np.append(self._xx, [x], axis=0)
		self._yy = np.append(self._yy, [y], axis=0)

		self.normalize()
		self.scalarize()

	def recommended(self):
		"""Return the best configuration among the previously collected ones

		Returns:
				tuple: metrics regarding the best configuration : its index, itself,
					its TOPSIS value, its objective values
		"""
		amax = np.argmax(self._scalarized_yy)
		return amax, self._xx[amax], self._scalarized_yy[amax], self._yy[amax]

	def save(self, filepath):
		"""Save the configurations and the objective values / scalarization into a
		tsv file.

		Args:
				path (str): filepath
		"""
		file = open(filepath, 'w+')
		file.write("x\ty\ttopsis\n")
		for i in range(len(self._xx)):
			file.write(f"{list(self._xx[i])}\t{list(self._yy[i])}\t{self._scalarized_yy[i]}\n")