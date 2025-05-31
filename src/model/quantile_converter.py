from typing import Dict, Tuple, List
import numpy as np
import pandas as pd
from scipy import interpolate

class QuantileConverter:

    def __init__(self, quantile_levels=None):
        self.quantile_levels = quantile_levels or [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    def quantiles_to_hit_probability(self, quantile_predictions: List[float], threshold):
        
        quantile_values = np.array(quantile_predictions)
        quantile_levels = np.array(self.quantile_levels)
        
        # Add boundary points for better interpolation
        # Add 0th percentile (min possible value) and 100th percentile (max possible value)
        extended_values = np.concatenate([
            [quantile_values[0] - (quantile_values[1] - quantile_values[0])],  # Extrapolate min
            quantile_values,
            [quantile_values[-1] + (quantile_values[-1] - quantile_values[-2])]  # Extrapolate max
        ])
        extended_levels = np.concatenate([[0.0], quantile_levels, [1.0]])
        
        kind = 'linear'
        cdf_interpolator = interpolate.interp1d(
            extended_values, extended_levels, 
            kind=kind, bounds_error=False, fill_value=(0, 1)
        )
        cdf_func = cdf_interpolator
        
        under_prob = float(cdf_func(threshold))
        over_prob = 1.0 - under_prob
        
        return {
            'threshold': threshold,
            'over': over_prob,
            'under': under_prob
        }
