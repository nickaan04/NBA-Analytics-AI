import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor
import os

def load_and_prepare_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Create features for prediction
    # We'll use the last 5 games as features
    feature_columns = ['pts', 'fg', 'fga', 'fg3', 'fg3a', 'ft', 'fta', 'ast', 'trb', 'stl', 'blk', 'tov']
    
    # Create lag features (previous game stats)
    for col in feature_columns:
        df[f'{col}_lag1'] = df[col].shift(1)
        df[f'{col}_lag2'] = df[col].shift(2)
        df[f'{col}_lag3'] = df[col].shift(3)
        df[f'{col}_lag4'] = df[col].shift(4)
        df[f'{col}_lag5'] = df[col].shift(5)
    
    # Drop rows with NaN values (first 5 games)
    df = df.dropna()
    
    return df

def train_predictor(df):
    # Split data into train and test sets
    train_data = df.iloc[:-1]  # All but last game
    test_data = df.iloc[-1:]   # Last game
    
    # Define target column
    target_column = 'pts'
    
    # Create predictor
    predictor = TabularPredictor(label=target_column)
    
    # Train the model
    predictor.fit(train_data)
    
    # Make prediction
    prediction = predictor.predict(test_data)
    
    # Return the first prediction value
    return float(prediction.iloc[0])

def main():
    # Get the path to the data file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data', 'csv', 'players')
    file_path = os.path.join(data_dir, 'lebronjames.csv')
    
    # Load and prepare data
    df = load_and_prepare_data(file_path)
    
    # Train model and make prediction
    predicted_points = train_predictor(df)
    
    print(f"Predicted points for LeBron James's next game: {predicted_points:.1f}")

if __name__ == "__main__":
    main() 