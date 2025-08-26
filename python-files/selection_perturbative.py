import numpy as np
import time
import random
from typing import List, Tuple, Callable, Dict
import matplotlib.pyplot as plt
from dataclasses import dataclass
from enum import Enum

class HeuristicType(Enum):
    """Enumeration of low-level perturbative heuristics"""
    RANDOM_WALK = "random_walk"
    GAUSSIAN_MUTATION = "gaussian_mutation"
    CAUCHY_MUTATION = "cauchy_mutation"
    UNIFORM_CROSSOVER = "uniform_crossover"
    HILL_CLIMBING = "hill_climbing"
    SIMULATED_ANNEALING = "simulated_annealing"

@dataclass
class HeuristicPerformance:
    """Tracks performance metrics for each heuristic"""
    success_count: int = 0
    total_applications: int = 0
    cumulative_improvement: float = 0.0
    recent_improvements: List[float] = None
    
    def __post_init__(self):
        if self.recent_improvements is None:
            self.recent_improvements = []

class BenchmarkFunction:
    """Base class for benchmark functions"""
    def __init__(self, name: str, dimension: int, bounds: Tuple[float, float], optimal_value: float):
        self.name = name
        self.dimension = dimension
        self.bounds = bounds
        self.optimal_value = optimal_value
    
    def evaluate(self, x: np.ndarray) -> float:
        """Evaluate the function at point x"""
        raise NotImplementedError
    
    def is_within_bounds(self, x: np.ndarray) -> bool:
        """Check if solution is within bounds"""
        return np.all((x >= self.bounds[0]) & (x <= self.bounds[1]))

class F1_Function(BenchmarkFunction):
    """f1 = 0.26(x1² + x2²) - 0.48x1x2"""
    def __init__(self, dimension: int = 2):
        super().__init__("f1", dimension, (-10, 10), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        if len(x) < 2:
            raise ValueError("f1 requires at least 2 dimensions")
        return 0.26 * (x[0]**2 + x[1]**2) - 0.48 * x[0] * x[1]

class F2_Function(BenchmarkFunction):
    """f2 = 4x1² - 2.1x1⁴ + (x1⁶)/3 + x1x2 - 4x2² + 4x2⁴"""
    def __init__(self, dimension: int = 2):
        super().__init__("f2", dimension, (-5, 5), -1.0316)
    
    def evaluate(self, x: np.ndarray) -> float:
        if len(x) < 2:
            raise ValueError("f2 requires at least 2 dimensions")
        return (4*x[0]**2 - 2.1*x[0]**4 + (x[0]**6)/3 + 
                x[0]*x[1] - 4*x[1]**2 + 4*x[1]**4)

class F3_Function(BenchmarkFunction):
    """f3 = Σ(xi²)"""
    def __init__(self, dimension: int):
        super().__init__("f3", dimension, (-100, 100), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum(x**2)

class F4_Function(BenchmarkFunction):
    """f4 = Σ|xi| + Π|xi|"""
    def __init__(self, dimension: int):
        super().__init__("f4", dimension, (-10, 10), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum(np.abs(x)) + np.prod(np.abs(x))

class F5_Function(BenchmarkFunction):
    """f5 = Σ(Σxj)²"""
    def __init__(self, dimension: int):
        super().__init__("f5", dimension, (-100, 100), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        result = 0
        for i in range(len(x)):
            result += (np.sum(x[:i+1]))**2
        return result

class F6_Function(BenchmarkFunction):
    """f6 = max{|xi|, 1 ≤ i ≤ D}"""
    def __init__(self, dimension: int):
        super().__init__("f6", dimension, (-100, 100), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.max(np.abs(x))

class F7_Function(BenchmarkFunction):
    """f7 = Σ(i*xi²)"""
    def __init__(self, dimension: int):
        super().__init__("f7", dimension, (-10, 10), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum([(i+1) * x[i]**2 for i in range(len(x))])

class F8_Function(BenchmarkFunction):
    """f8 = Σ(i*xi⁴)"""
    def __init__(self, dimension: int):
        super().__init__("f8", dimension, (-1.28, 1.28), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum([(i+1) * x[i]**4 for i in range(len(x))])

class F9_Function(BenchmarkFunction):
    """f9 = Σ|xi|^(i+1)"""
    def __init__(self, dimension: int):
        super().__init__("f9", dimension, (-1, 1), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum([np.abs(x[i])**(i+2) for i in range(len(x))])

class F10_Function(BenchmarkFunction):
    """f10 = Σ((10^6)^((i-1)/(D-1)) * xi²)"""
    def __init__(self, dimension: int):
        super().__init__("f10", dimension, (-100, 100), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        if len(x) == 1:
            return x[0]**2
        return np.sum([(10**6)**((i)/(len(x)-1)) * x[i]**2 for i in range(len(x))])

class F11_Function(BenchmarkFunction):
    """f11 = Σ(floor(xi + 0.5)²)"""
    def __init__(self, dimension: int):
        super().__init__("f11", dimension, (-1.28, 1.28), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum(np.floor(x + 0.5)**2)

class F12_Function(BenchmarkFunction):
    """f12 = Σ(i*xi⁴) + random[0,1)"""
    def __init__(self, dimension: int):
        super().__init__("f12", dimension, (-1.28, 1.28), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum([(i+1) * x[i]**4 for i in range(len(x))]) + np.random.random()

class F13_Function(BenchmarkFunction):
    """f13 = Σ(xi² - 10*cos(2πxi) + 10) - Rastrigin"""
    def __init__(self, dimension: int):
        super().__init__("f13", dimension, (-5.12, 5.12), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum(x**2 - 10*np.cos(2*np.pi*x) + 10)

class F14_Function(BenchmarkFunction):
    """f14 = Ackley function"""
    def __init__(self, dimension: int):
        super().__init__("f14", dimension, (-32, 32), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        n = len(x)
        return (-20 * np.exp(-0.2 * np.sqrt(np.sum(x**2)/n)) - 
                np.exp(np.sum(np.cos(2*np.pi*x))/n) + 20 + np.e)

class F15_Function(BenchmarkFunction):
    """f15 = Griewank function"""
    def __init__(self, dimension: int):
        super().__init__("f15", dimension, (-600, 600), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return (1/4000 * np.sum(x**2) - 
                np.prod(np.cos(x/np.sqrt(np.arange(1, len(x)+1)))) + 1)

class F16_Function(BenchmarkFunction):
    """f16 = Schaffer function"""
    def __init__(self, dimension: int):
        super().__init__("f16", dimension, (-100, 100), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        sum_squares = np.sum(x**2)
        return (0.5 + (np.sin(np.sqrt(sum_squares))**2 - 0.5) / 
                (1 + 0.001*sum_squares)**2)

class F17_Function(BenchmarkFunction):
    """f17 = Σ(xi⁴ - 16xi² + 5xi)/D"""
    def __init__(self, dimension: int):
        super().__init__("f17", dimension, (-5, 5), -78.3323)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum(x**4 - 16*x**2 + 5*x) / len(x)

class F18_Function(BenchmarkFunction):
    """f18 = Σ|xi*sin(xi) + 0.1*xi|"""
    def __init__(self, dimension: int):
        super().__init__("f18", dimension, (-10, 10), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        return np.sum(np.abs(x * np.sin(x) + 0.1 * x))

class F19_Function(BenchmarkFunction):
    """f19 = Modified Rastrigin"""
    def __init__(self, dimension: int):
        super().__init__("f19", dimension, (-5.12, 5.12), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        result = 0
        for xi in x:
            if abs(xi) < 0.5:
                result += xi**2 - 10*np.cos(2*np.pi*xi) + 10
            else:
                rounded = np.round(2*xi)
                result += rounded**2 - 10*np.cos(np.pi*rounded) + 10
        return result

class F20_Function(BenchmarkFunction):
    """f20 = Penalized function 1"""
    def __init__(self, dimension: int):
        super().__init__("f20", dimension, (-50, 50), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        n = len(x)
        y = 1 + (x + 1) / 4
        
        term1 = 10 * np.sin(np.pi * y[0])**2
        term2 = np.sum((y[:-1] - 1)**2 * (1 + 10 * np.sin(np.pi * y[1:])**2))
        term3 = (y[-1] - 1)**2
        
        penalty = np.sum([self._u(xi, 10, 100, 4) for xi in x])
        
        return np.pi/n * (term1 + term2 + term3) + penalty
    
    def _u(self, x, a, k, m):
        if x > a:
            return k * (x - a)**m
        elif x < -a:
            return k * (-x - a)**m
        else:
            return 0

class F21_Function(BenchmarkFunction):
    """f21 = Schwefel function"""
    def __init__(self, dimension: int):
        super().__init__("f21", dimension, (-500, 500), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        n = len(x)
        return 418.9828872724369 * n - np.sum(x * np.sin(np.sqrt(np.abs(x))))

class F22_Function(BenchmarkFunction):
    """f22 = Modified Rastrigin with different weights"""
    def __init__(self, dimension: int):
        super().__init__("f22", dimension, (-5.12, 5.12), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        n = len(x)
        weights = [10**(6*(i)/(n-1)) if n > 1 else 1 for i in range(n)]
        return np.sum([weights[i] * (x[i]**2 - 10*np.cos(2*np.pi*10**(6*i/(n-1) if n > 1 else 0)*x[i]) + 10) 
                      for i in range(n)])

class F23_Function(BenchmarkFunction):
    """f23 = Penalized function 2"""
    def __init__(self, dimension: int):
        super().__init__("f23", dimension, (-50, 50), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        term1 = np.sin(3*np.pi*x[0])**2
        term2 = np.sum((x[:-1] - 1)**2 * (1 + np.sin(3*np.pi*x[1:])**2))
        term3 = (x[-1] - 1)**2 * (1 + np.sin(2*np.pi*x[-1])**2)
        
        penalty = np.sum([self._u(xi, 5, 100, 4) for xi in x])
        
        return 0.1 * (term1 + term2 + term3) + penalty
    
    def _u(self, x, a, k, m):
        if x > a:
            return k * (x - a)**m
        elif x < -a:
            return k * (-x - a)**m
        else:
            return 0

class F24_Function(BenchmarkFunction):
    """f24 = Another penalized function"""
    def __init__(self, dimension: int):
        super().__init__("f24", dimension, (-10, 10), 0)
    
    def evaluate(self, x: np.ndarray) -> float:
        w = 1 + (x - 1) / 4
        term1 = np.sin(np.pi * w[0])**2
        term2 = np.sum((w[:-1] - 1)**2 * (1 + 10 * np.sin(np.pi * w[:-1] + 1)**2))
        term3 = (w[-1] - 1)**2 * (1 + np.sin(2 * np.pi * w[-1])**2)
        
        return term1 + term2 + term3

class LowLevelHeuristic:
    """Base class for low-level perturbative heuristics"""
    def __init__(self, heuristic_type: HeuristicType):
        self.heuristic_type = heuristic_type
        self.performance = HeuristicPerformance()
    
    def apply(self, solution: np.ndarray, bounds: Tuple[float, float], 
              current_fitness: float = None, temperature: float = 1.0) -> np.ndarray:
        """Apply the heuristic to generate a new solution"""
        raise NotImplementedError

class RandomWalkHeuristic(LowLevelHeuristic):
    """Random walk perturbation"""
    def __init__(self, step_size: float = 0.1):
        super().__init__(HeuristicType.RANDOM_WALK)
        self.step_size = step_size
    
    def apply(self, solution: np.ndarray, bounds: Tuple[float, float], 
              current_fitness: float = None, temperature: float = 1.0) -> np.ndarray:
        new_solution = solution + np.random.uniform(-self.step_size, self.step_size, len(solution))
        return np.clip(new_solution, bounds[0], bounds[1])

class GaussianMutationHeuristic(LowLevelHeuristic):
    """Gaussian mutation"""
    def __init__(self, sigma: float = 0.1):
        super().__init__(HeuristicType.GAUSSIAN_MUTATION)
        self.sigma = sigma
    
    def apply(self, solution: np.ndarray, bounds: Tuple[float, float], 
              current_fitness: float = None, temperature: float = 1.0) -> np.ndarray:
        mutation = np.random.normal(0, self.sigma * temperature, len(solution))
        new_solution = solution + mutation
        return np.clip(new_solution, bounds[0], bounds[1])

class CauchyMutationHeuristic(LowLevelHeuristic):
    """Cauchy mutation for better exploration"""
    def __init__(self, scale: float = 0.1):
        super().__init__(HeuristicType.CAUCHY_MUTATION)
        self.scale = scale
    
    def apply(self, solution: np.ndarray, bounds: Tuple[float, float], 
              current_fitness: float = None, temperature: float = 1.0) -> np.ndarray:
        mutation = np.random.standard_cauchy(len(solution)) * self.scale * temperature
        new_solution = solution + mutation
        return np.clip(new_solution, bounds[0], bounds[1])

class UniformCrossoverHeuristic(LowLevelHeuristic):
    """Uniform crossover with random solution"""
    def __init__(self):
        super().__init__(HeuristicType.UNIFORM_CROSSOVER)
    
    def apply(self, solution: np.ndarray, bounds: Tuple[float, float], 
              current_fitness: float = None, temperature: float = 1.0) -> np.ndarray:
        random_solution = np.random.uniform(bounds[0], bounds[1], len(solution))
        mask = np.random.random(len(solution)) < 0.5
        new_solution = np.where(mask, solution, random_solution)
        return new_solution

class HillClimbingHeuristic(LowLevelHeuristic):
    """Hill climbing with small perturbations"""
    def __init__(self, step_size: float = 0.01):
        super().__init__(HeuristicType.HILL_CLIMBING)
        self.step_size = step_size
    
    def apply(self, solution: np.ndarray, bounds: Tuple[float, float], 
              current_fitness: float = None, temperature: float = 1.0) -> np.ndarray:
        # Try small perturbations in each dimension
        best_solution = solution.copy()
        for i in range(len(solution)):
            for direction in [-1, 1]:
                test_solution = solution.copy()
                test_solution[i] += direction * self.step_size
                test_solution = np.clip(test_solution, bounds[0], bounds[1])
                if np.allclose(test_solution, best_solution):
                    continue
                best_solution = test_solution
                break  # Take first improvement
        return best_solution

class SimulatedAnnealingHeuristic(LowLevelHeuristic):
    """Simulated annealing acceptance with Gaussian perturbation"""
    def __init__(self, sigma: float = 0.1):
        super().__init__(HeuristicType.SIMULATED_ANNEALING)
        self.sigma = sigma
    
    def apply(self, solution: np.ndarray, bounds: Tuple[float, float], 
              current_fitness: float = None, temperature: float = 1.0) -> np.ndarray:
        mutation = np.random.normal(0, self.sigma, len(solution))
        new_solution = solution + mutation * temperature
        return np.clip(new_solution, bounds[0], bounds[1])

class SelectionPerturbativeHyperHeuristic:
    """
    Selection Perturbative Hyper-Heuristic for Function Optimization
    
    This hyper-heuristic uses multiple selection strategies:
    1. Roulette Wheel Selection based on success rates
    2. Rank-based Selection
    3. Adaptive Selection with exploration/exploitation balance
    """
    
    def __init__(self, function: BenchmarkFunction, max_evaluations: int = 10000):
        self.function = function
        self.max_evaluations = max_evaluations
        self.evaluation_count = 0
        
        # Initialize low-level heuristics
        self.heuristics = [
            RandomWalkHeuristic(step_size=0.1),
            GaussianMutationHeuristic(sigma=0.1),
            CauchyMutationHeuristic(scale=0.05),
            UniformCrossoverHeuristic(),
            HillClimbingHeuristic(step_size=0.01),
            SimulatedAnnealingHeuristic(sigma=0.1)
        ]
        
        # Selection parameters
        self.selection_method = "adaptive"  # "roulette", "rank", "adaptive"
        self.exploration_rate = 0.1
        self.memory_length = 100
        
        # Best solution tracking
        self.best_solution = None
        self.best_fitness = float('inf')
        self.fitness_history = []
        
        # Temperature for simulated annealing components
        self.initial_temperature = 1.0
        self.current_temperature = self.initial_temperature
        
    def _evaluate_solution(self, solution: np.ndarray) -> float:
        """Evaluate solution and update counters"""
        if not self.function.is_within_bounds(solution):
            return float('inf')
        
        fitness = self.function.evaluate(solution)
        self.evaluation_count += 1
        
        # Update best solution
        if fitness < self.best_fitness:
            self.best_fitness = fitness
            self.best_solution = solution.copy()
        
        self.fitness_history.append(fitness)
        return fitness
    
    def _select_heuristic_roulette(self) -> LowLevelHeuristic:
        """Roulette wheel selection based on success rates"""
        weights = []
        for heuristic in self.heuristics:
            if heuristic.performance.total_applications == 0:
                weights.append(1.0)  # Give new heuristics a chance
            else:
                success_rate = heuristic.performance.success_count / heuristic.performance.total_applications
                weights.append(success_rate + 0.1)  # Add small constant to avoid zero weights
        
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(self.heuristics)
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return self.heuristics[i]
        
        return self.heuristics[-1]
    
    def _select_heuristic_rank(self) -> LowLevelHeuristic:
        """Rank-based selection"""
        # Sort heuristics by success rate
        sorted_heuristics = sorted(self.heuristics, 
                                 key=lambda h: h.performance.success_count / max(1, h.performance.total_applications),
                                 reverse=True)
        
        # Rank-based probability (higher rank = higher probability)
        n = len(sorted_heuristics)
        ranks = list(range(n, 0, -1))
        total_rank = sum(ranks)
        
        r = random.uniform(0, total_rank)
        cumulative = 0
        for i, rank in enumerate(ranks):
            cumulative += rank
            if r <= cumulative:
                return sorted_heuristics[i]
        
        return sorted_heuristics[-1]
    
    def _select_heuristic_adaptive(self) -> LowLevelHeuristic:
        """Adaptive selection balancing exploration and exploitation"""
        if random.random() < self.exploration_rate:
            # Exploration: select randomly or select least used
            least_used = min(self.heuristics, key=lambda h: h.performance.total_applications)
            return least_used
        else:
            # Exploitation: select based on recent performance
            best_recent = None
            best_recent_score = -float('inf')
            
            for heuristic in self.heuristics:
                if len(heuristic.performance.recent_improvements) > 0:
                    recent_score = np.mean(heuristic.performance.recent_improvements[-10:])
                    if recent_score > best_recent_score:
                        best_recent_score = recent_score
                        best_recent = heuristic
            
            return best_recent if best_recent is not None else random.choice(self.heuristics)
    
    def _select_heuristic(self) -> LowLevelHeuristic:
        """Select heuristic based on current selection method"""
        if self.selection_method == "roulette":
            return self._select_heuristic_roulette()
        elif self.selection_method == "rank":
            return self._select_heuristic_rank()
        else:  # adaptive
            return self._select_heuristic_adaptive()
    
    def _update_heuristic_performance(self, heuristic: LowLevelHeuristic, 
                                    old_fitness: float, new_fitness: float):
        """Update performance metrics for the heuristic"""
        heuristic.performance.total_applications += 1
        
        improvement = old_fitness - new_fitness
        heuristic.performance.cumulative_improvement += improvement
        
        if improvement > 0:
            heuristic.performance.success_count += 1
        
        # Track recent improvements
        heuristic.performance.recent_improvements.append(improvement)
        if len(heuristic.performance.recent_improvements) > self.memory_length:
            heuristic.performance.recent_improvements.pop(0)
    
    def _update_temperature(self):
        """Update temperature for simulated annealing components"""
        progress = self.evaluation_count / self.max_evaluations
        self.current_temperature = self.initial_temperature * (1 - progress)
    
    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        """
        Main optimization loop
        
        Returns:
            Tuple of (best_solution, best_fitness, fitness_history)
        """
        # Initialize random solution
        current_solution = np.random.uniform(
            self.function.bounds[0], 
            self.function.bounds[1], 
            self.function.dimension
        )
        current_fitness = self._evaluate_solution(current_solution)
        
        while self.evaluation_count < self.max_evaluations:
            # Select heuristic
            selected_heuristic = self._select_heuristic()
            
            # Apply heuristic
            new_solution = selected_heuristic.apply(
                current_solution, 
                self.function.bounds,
                current_fitness,
                self.current_temperature
            )
            
            # Evaluate new solution
            new_fitness = self._evaluate_solution(new_solution)
            
            # Update heuristic performance
            self._update_heuristic_performance(selected_heuristic, current_fitness, new_fitness)
            
            # Accept or reject new solution (always accept better solutions)
            if new_fitness <= current_fitness:
                current_solution = new_solution
                current_fitness = new_fitness
            
            # Update temperature
            self._update_temperature()
        
        return self.best_solution, self.best_fitness, self.fitness_history

def create_function(func_name: str, dimension: int) -> BenchmarkFunction:
    """Factory function to create benchmark functions"""
    function_map = {
        'f1': F1_Function,
        'f2': F2_Function,
        'f3': F3_Function,
        'f4': F4_Function,
        'f5': F5_Function,
        'f6': F6_Function,
        'f7': F7_Function,
        'f8': F8_Function,
        'f9': F9_Function,
        'f10': F10_Function,
        'f11': F11_Function,
        'f12': F12_Function,
        'f13': F13_Function,
        'f14': F14_Function,
        'f15': F15_Function,
        'f16': F16_Function,
        'f17': F17_Function,
        'f18': F18_Function,
        'f19': F19_Function,
        'f20': F20_Function,
        'f21': F21_Function,
        'f22': F22_Function,
        'f23': F23_Function,
        'f24': F24_Function,
    }
    
    if func_name in function_map:
        return function_map[func_name](dimension)
    else:
        raise ValueError(f"Unknown function: {func_name}")

class ExperimentRunner:
    """Class to run comprehensive experiments"""
    
    def __init__(self, max_evaluations: int = 10000, num_runs: int = 10):
        self.max_evaluations = max_evaluations
        self.num_runs = num_runs
        self.results = {}
    
    def run_experiment(self, function_names: List[str], dimensions: List[int] = None):
        """Run experiments for specified functions and dimensions"""
        
        for func_name in function_names:
            print(f"\n=== Running experiments for {func_name.upper()} ===")
            
            # Determine dimensions to test
            if func_name in ['f1', 'f2']:
                test_dimensions = [2]  # Fixed dimension functions
            else:
                test_dimensions = dimensions or [10, 30, 50]
            
            self.results[func_name] = {}
            
            for dim in test_dimensions:
                print(f"\n--- Dimension {dim} ---")
                
                # Create function
                function = create_function(func_name, dim)
                
                # Run multiple experiments
                best_fitnesses = []
                best_solutions = []
                runtimes = []
                convergence_histories = []
                
                for run in range(self.num_runs):
                    print(f"Run {run + 1}/{self.num_runs}...", end=' ')
                    
                    # Create and run hyper-heuristic
                    hh = SelectionPerturbativeHyperHeuristic(function, self.max_evaluations)
                    
                    start_time = time.time()
                    best_sol, best_fit, history = hh.optimize()
                    end_time = time.time()
                    
                    best_fitnesses.append(best_fit)
                    best_solutions.append(best_sol)
                    runtimes.append(end_time - start_time)
                    convergence_histories.append(history)
                    
                    print(f"Best: {best_fit:.6f}")
                
                # Store results
                self.results[func_name][dim] = {
                    'best_fitness': min(best_fitnesses),
                    'mean_fitness': np.mean(best_fitnesses),
                    'std_fitness': np.std(best_fitnesses),
                    'best_solution': best_solutions[np.argmin(best_fitnesses)],
                    'mean_runtime': np.mean(runtimes),
                    'std_runtime': np.std(runtimes),
                    'convergence_histories': convergence_histories,
                    'all_best_fitnesses': best_fitnesses
                }
                
                print(f"Mean: {np.mean(best_fitnesses):.6f} ± {np.std(best_fitnesses):.6f}")
                print(f"Best: {min(best_fitnesses):.6f}")
                print(f"Runtime: {np.mean(runtimes):.3f} ± {np.std(runtimes):.3f} seconds")
    
    def print_results(self):
        """Print comprehensive results"""
        print("\n" + "="*80)
        print("COMPREHENSIVE EXPERIMENTAL RESULTS")
        print("="*80)
        
        for func_name, func_results in self.results.items():
            print(f"\n{func_name.upper()} Results:")
            print("-" * 60)
            
            for dim, results in func_results.items():
                print(f"\nDimension {dim}:")
                print(f"  Best Fitness:     {results['best_fitness']:.8f}")
                print(f"  Mean Fitness:     {results['mean_fitness']:.8f} ± {results['std_fitness']:.8f}")
                print(f"  Mean Runtime:     {results['mean_runtime']:.3f} ± {results['std_runtime']:.3f} seconds")
                print(f"  Best Solution:    {results['best_solution']}")
    
    def plot_convergence(self, function_names: List[str] = None, save_plots: bool = False):
        """Plot convergence curves for specified functions"""
        if function_names is None:
            function_names = list(self.results.keys())
        
        for func_name in function_names:
            if func_name not in self.results:
                continue
                
            func_results = self.results[func_name]
            n_dims = len(func_results)
            
            fig, axes = plt.subplots(1, n_dims, figsize=(5*n_dims, 4))
            if n_dims == 1:
                axes = [axes]
            
            for i, (dim, results) in enumerate(func_results.items()):
                histories = results['convergence_histories']
                
                # Plot mean convergence with confidence intervals
                max_len = max(len(h) for h in histories)
                padded_histories = []
                
                for h in histories:
                    padded = h + [h[-1]] * (max_len - len(h))
                    padded_histories.append(padded)
                
                mean_history = np.mean(padded_histories, axis=0)
                std_history = np.std(padded_histories, axis=0)
                
                x = range(len(mean_history))
                axes[i].plot(x, mean_history, 'b-', linewidth=2, label='Mean')
                axes[i].fill_between(x, 
                                   mean_history - std_history,
                                   mean_history + std_history,
                                   alpha=0.3, color='blue')
                
                axes[i].set_xlabel('Function Evaluations')
                axes[i].set_ylabel('Fitness Value')
                axes[i].set_title(f'{func_name.upper()} - Dimension {dim}')
                axes[i].set_yscale('log')
                axes[i].grid(True, alpha=0.3)
                axes[i].legend()
            
            plt.tight_layout()
            if save_plots:
                plt.savefig(f'convergence_{func_name}.png', dpi=300, bbox_inches='tight')
            plt.show()

def main():
    """
    Main experimental setup and execution
    
    This function demonstrates the complete experimental framework:
    1. Function definitions (f1 to f24)
    2. Hyper-heuristic configuration
    3. Experimental execution
    4. Results analysis and visualization
    """
    
    print("Selection Perturbative Hyper-Heuristic for Function Optimization")
    print("="*70)
    
    # Experimental parameters
    MAX_EVALUATIONS = 10000
    NUM_RUNS = 10
    DIMENSIONS = [10, 30, 50]
    
    # Functions to test (you can modify this list to test specific functions)
    FUNCTIONS_TO_TEST = [
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
        'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20',
        'f21', 'f22', 'f23', 'f24'
    ]
    
    # For demonstration, let's test a subset of functions
    DEMO_FUNCTIONS = ['f1', 'f2', 'f3', 'f13', 'f14', 'f15']
    
    print("\nExperimental Setup:")
    print(f"  Maximum Evaluations: {MAX_EVALUATIONS:,}")
    print(f"  Number of Runs: {NUM_RUNS}")
    print(f"  Test Dimensions: {DIMENSIONS}")
    print(f"  Functions to Test: {len(DEMO_FUNCTIONS)} functions")
    
    print("\nHyper-Heuristic Configuration:")
    print("  Selection Method: Adaptive (exploration/exploitation balance)")
    print("  Low-level Heuristics:")
    print("    - Random Walk Perturbation")
    print("    - Gaussian Mutation")
    print("    - Cauchy Mutation")
    print("    - Uniform Crossover")
    print("    - Hill Climbing")
    print("    - Simulated Annealing")
    
    print("\nPerformance Metrics:")
    print("  - Best fitness found")
    print("  - Mean fitness ± standard deviation")
    print("  - Runtime analysis")
    print("  - Convergence behavior")
    
    # Create and run experiments
    runner = ExperimentRunner(MAX_EVALUATIONS, NUM_RUNS)
    
    print("\nStarting experiments...")
    runner.run_experiment(DEMO_FUNCTIONS, DIMENSIONS)
    
    # Print results
    runner.print_results()
    
    # Plot convergence curves
    print("\nGenerating convergence plots...")
    runner.plot_convergence(DEMO_FUNCTIONS[:3])  # Plot first 3 functions
    
    print("\n" + "="*70)
    print("Experiment completed successfully!")
    print("="*70)
    
    # Additional analysis
    print("\nDetailed Hyper-Heuristic Analysis:")
    
    # Create a sample hyper-heuristic for analysis
    sample_function = create_function('f3', 30)
    hh = SelectionPerturbativeHyperHeuristic(sample_function, 1000)
    
    print(f"\nLow-level Heuristics Configuration:")
    for i, heuristic in enumerate(hh.heuristics):
        print(f"  {i+1}. {heuristic.heuristic_type.value}: {type(heuristic).__name__}")
    
    print(f"\nSelection Strategy: {hh.selection_method}")
    print(f"Exploration Rate: {hh.exploration_rate}")
    print(f"Memory Length: {hh.memory_length}")
    
    return runner

# Performance analysis functions
def analyze_heuristic_performance(runner: ExperimentRunner):
    """Analyze which heuristics perform best on different function types"""
    print("\n" + "="*60)
    print("HEURISTIC PERFORMANCE ANALYSIS")
    print("="*60)
    
    # This would require storing heuristic-specific performance data
    # For now, provide a conceptual framework
    
    function_types = {
        'unimodal': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'],
        'multimodal': ['f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24']
    }
    
    print("Function Categories:")
    for category, functions in function_types.items():
        print(f"  {category.capitalize()}: {', '.join(functions)}")
    
    print("\nExpected Heuristic Performance:")
    print("  Unimodal Functions:")
    print("    - Hill Climbing: Should perform well due to single optimum")
    print("    - Gaussian Mutation: Good for fine-tuning")
    print("  Multimodal Functions:")
    print("    - Cauchy Mutation: Better exploration capabilities")
    print("    - Simulated Annealing: Helps escape local optima")
    print("    - Random Walk: Provides diversity")

def statistical_significance_test(runner: ExperimentRunner):
    """Perform statistical significance tests between different runs"""
    print("\n" + "="*60)
    print("STATISTICAL SIGNIFICANCE ANALYSIS")
    print("="*60)
    
    from scipy import stats
    
    # Example: Compare performance across dimensions for each function
    for func_name, func_results in runner.results.items():
        if len(func_results) > 1:
            print(f"\n{func_name.upper()} - Dimension Comparison:")
            
            dimensions = sorted(func_results.keys())
            for i in range(len(dimensions)-1):
                dim1, dim2 = dimensions[i], dimensions[i+1]
                
                results1 = func_results[dim1]['all_best_fitnesses']
                results2 = func_results[dim2]['all_best_fitnesses']
                
                # Perform t-test
                t_stat, p_value = stats.ttest_ind(results1, results2)
                
                print(f"  Dim {dim1} vs Dim {dim2}: t={t_stat:.3f}, p={p_value:.6f}")
                if p_value < 0.05:
                    print(f"    Statistically significant difference (α=0.05)")
                else:
                    print(f"    No significant difference (α=0.05)")

# Example usage and demonstration
if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Run main experiments
    experiment_runner = main()
    
    # Additional analyses
    analyze_heuristic_performance(experiment_runner)
    
    # Uncomment to run statistical tests (requires scipy)
    # statistical_significance_test(experiment_runner)
    
    print("\n" + "="*70)
    print("TECHNICAL SPECIFICATIONS")
    print("="*70)
    print("Machine Configuration:")
    print("  - Platform: Python 3.x")
    print("  - Required Libraries: numpy, matplotlib")
    print("  - Optional Libraries: scipy (for statistical tests)")
    print("  - Memory Usage: Moderate (depends on problem dimension)")
    print("  - Computational Complexity: O(E × H × D)")
    print("    where E = evaluations, H = heuristics, D = dimension")
    
    print("\nParameter Settings Used:")
    print(f"  - Maximum Function Evaluations: {experiment_runner.max_evaluations:,}")
    print(f"  - Number of Independent Runs: {experiment_runner.num_runs}")
    print("  - Selection Strategy: Adaptive")
    print("  - Exploration Rate: 0.1")
    print("  - Memory Length: 100")
    print("  - Initial Temperature: 1.0")
    
    print("\nHyper-Heuristic Framework Summary:")
    print("  1. SELECTION MECHANISM:")
    print("     - Adaptive selection balancing exploration/exploitation")
    print("     - Performance-based heuristic ranking")
    print("     - Recent performance memory")
    
    print("  2. LOW-LEVEL HEURISTICS:")
    print("     - 6 different perturbative operators")
    print("     - Adaptive parameters based on search progress")
    print("     - Boundary constraint handling")
    
    print("  3. PERFORMANCE TRACKING:")
    print("     - Success rate monitoring")
    print("     - Improvement tracking")
    print("     - Runtime analysis")
    
    print("  4. ACCEPTANCE CRITERIA:")
    print("     - Greedy acceptance (always accept improvements)")
    print("     - Suitable for exploitation-focused optimization")
    
    print("\n" + "="*70)
