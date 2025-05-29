import numpy as np
import pandas as pd
from scipy import interpolate

class QuantileToHitProbability:
    """
    Convert quantile regression predictions to hit probabilities using empirical CDF
    """
    
    def __init__(self, quantile_levels=None):
        """
        Initialize with quantile levels used in training
        
        Args:
            quantile_levels: List of quantile levels (e.g., [0.1, 0.2, 0.3, ..., 0.9])
        """
        self.quantile_levels = quantile_levels or [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    def quantiles_to_hit_probability(self, quantile_predictions, threshold, interpolate_method='linear'):
        """
        Convert quantile predictions to hit probability for a given threshold
        
        Args:
            quantile_predictions: Array or list of quantile predictions [Q(0.1), Q(0.2), ..., Q(0.9)]
            threshold: The prop line/threshold to evaluate (e.g., 28.5 points)
            interpolate_method: 'linear', 'step', or 'cubic' for interpolation
            
        Returns:
            dict: Contains over_probability, under_probability, and interpolated_cdf
        """
        
        # Ensure we have arrays
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
        
        # Create interpolation function
        if interpolate_method == 'step':
            # Step function (more conservative)
            def cdf_func(x):
                return np.interp(x, extended_values, extended_levels, left=0, right=1)
        else:
            # Linear or cubic interpolation
            kind = 'linear' if interpolate_method == 'linear' else 'cubic'
            cdf_interpolator = interpolate.interp1d(
                extended_values, extended_levels, 
                kind=kind, bounds_error=False, fill_value=(0, 1)
            )
            cdf_func = cdf_interpolator
        
        # Calculate probabilities
        under_prob = float(cdf_func(threshold))
        over_prob = 1.0 - under_prob
        
        return {
            'threshold': threshold,
            'over_probability': over_prob,
            'under_probability': under_prob,
            'quantile_at_threshold': under_prob,
            'interpolation_method': interpolate_method
        }
    
    def get_multiple_thresholds(self, quantile_predictions, thresholds, interpolate_method='linear'):
        """
        Get hit probabilities for multiple thresholds at once
        
        Args:
            quantile_predictions: Array of quantile predictions
            thresholds: List of thresholds to evaluate
            
        Returns:
            pandas.DataFrame: Results for all thresholds
        """
        results = []
        
        for threshold in thresholds:
            result = self.quantiles_to_hit_probability(
                quantile_predictions, threshold, interpolate_method
            )
            results.append(result)
        
        return pd.DataFrame(results)
    
    def find_threshold_for_probability(self, quantile_predictions, target_probability, 
                                     over_or_under='over', interpolate_method='linear'):
        """
        Find what threshold gives you a specific hit probability
        
        Args:
            quantile_predictions: Array of quantile predictions
            target_probability: Desired probability (e.g., 0.6 for 60%)
            over_or_under: 'over' or 'under'
            
        Returns:
            float: Threshold that gives the target probability
        """
        quantile_values = np.array(quantile_predictions)
        quantile_levels = np.array(self.quantile_levels)
        
        if over_or_under == 'over':
            target_quantile = 1.0 - target_probability
        else:
            target_quantile = target_probability
        
        # Interpolate to find the value at target quantile
        threshold = np.interp(target_quantile, quantile_levels, quantile_values)
        
        return threshold
    
    def plot_distribution(self, quantile_predictions, thresholds=None, title="Predicted Distribution"):
        """
        Plot the predicted distribution and hit probabilities
        """
        try:
            import matplotlib.pyplot as plt
            
            quantile_values = np.array(quantile_predictions)
            quantile_levels = np.array(self.quantile_levels)
            
            # Create smooth curve for plotting
            x_smooth = np.linspace(quantile_values.min() * 0.9, quantile_values.max() * 1.1, 200)
            cdf_interpolator = interpolate.interp1d(
                quantile_values, quantile_levels, 
                kind='cubic', bounds_error=False, fill_value=(0, 1)
            )
            y_smooth = cdf_interpolator(x_smooth)
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Plot CDF
            ax1.plot(x_smooth, y_smooth, 'b-', linewidth=2, label='Predicted CDF')
            ax1.scatter(quantile_values, quantile_levels, color='red', s=50, zorder=5, label='Quantile Points')
            
            if thresholds:
                for threshold in thresholds:
                    prob_under = float(cdf_interpolator(threshold))
                    ax1.axvline(threshold, color='green', linestyle='--', alpha=0.7, 
                               label=f'Threshold: {threshold}')
                    ax1.axhline(prob_under, color='orange', linestyle=':', alpha=0.7)
                    ax1.text(threshold, prob_under + 0.05, f'P(≤{threshold}) = {prob_under:.3f}', 
                            rotation=0, ha='center')
            
            ax1.set_xlabel('Stat Value')
            ax1.set_ylabel('Cumulative Probability')
            ax1.set_title(f'{title} - CDF')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot PDF (derivative of CDF)
            pdf_smooth = np.gradient(y_smooth, x_smooth)
            ax2.plot(x_smooth, pdf_smooth, 'b-', linewidth=2, label='Predicted PDF')
            
            if thresholds:
                for threshold in thresholds:
                    ax2.axvline(threshold, color='green', linestyle='--', alpha=0.7)
            
            ax2.set_xlabel('Stat Value')
            ax2.set_ylabel('Probability Density')
            ax2.set_title(f'{title} - PDF')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("matplotlib not available for plotting")

# Example usage with your data
def example_usage():
    """
    Example of how to use with your Brunson data
    """
    
    # Your quantile predictions from the output
    brunson_quantiles = [26.151064, 26.928772, 27.861038, 28.295649, 28.67631, 
                        29.216074, 29.767246, 30.552994, 31.761806]
    
    # Initialize converter
    converter = QuantileToHitProbability()
    
    # Example: What's the probability Brunson scores over 28.5 points?
    threshold = 28.5
    result = converter.quantiles_to_hit_probability(brunson_quantiles, threshold)
    
    print(f"Brunson Points Prediction Analysis:")
    print(f"Threshold: {result['threshold']} points")
    print(f"Probability of scoring OVER {threshold}: {result['over_probability']:.3f} ({result['over_probability']*100:.1f}%)")
    print(f"Probability of scoring UNDER {threshold}: {result['under_probability']:.3f} ({result['under_probability']*100:.1f}%)")
    print()
    
    # Multiple thresholds
    thresholds = [27.5, 28.0, 28.5, 29.0, 29.5, 30.0]
    multiple_results = converter.get_multiple_thresholds(brunson_quantiles, thresholds)
    
    print("Multiple Threshold Analysis:")
    for _, row in multiple_results.iterrows():
        print(f"Over {row['threshold']}: {row['over_probability']:.3f} ({row['over_probability']*100:.1f}%)")
    
    print()
    
    # Find threshold for specific probability
    target_prob = 0.6  # 60% chance of going over
    threshold_for_60pct = converter.find_threshold_for_probability(
        brunson_quantiles, target_prob, 'over'
    )
    print(f"For 60% chance of going OVER: {threshold_for_60pct:.1f} points")

    converter.plot_distribution(brunson_quantiles, thresholds)
    
    return converter, brunson_quantiles

if __name__ == "__main__":
    example_usage()