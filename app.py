from flask import Flask, request, send_file, render_template
import pandas as pd
import numpy as np
from faker import Faker
import io
import random

app = Flask(__name__)
fake = Faker()

def is_categorical(series):
    """Detects if a column is categorical based on its unique values and data type."""
    if series.dtype == 'object' or series.nunique() <= 10:
        return True
    return False

def generate_synthetic_column(series):
    """Generates synthetic data for a single column based on its format."""
    if is_categorical(series):
        # For categorical columns, randomly choose from unique values
        unique_values = series.dropna().unique()
        return [random.choice(unique_values) for _ in range(len(series))]
    elif series.dtype == 'int64':
        # For integer columns, generate integer values based on the original range
        return np.random.randint(series.min(), series.max() + 1, len(series))
    elif series.dtype == 'float64':
        # For float columns, generate float values with normal distribution
        return np.random.normal(series.mean(), series.std(), len(series)).round(2)
    else:
        # For any other type (like strings with high cardinality), use random fake data
        return [fake.word() for _ in range(len(series))]

def generate_privacy_preserving_synthetic_data(df):
    """Generates synthetic data for each column in the dataframe while preserving privacy."""
    synthetic_data = pd.DataFrame()

    for column in df.columns:
        synthetic_data[column] = generate_synthetic_column(df[column])
    
    return synthetic_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Upload file from form
    file = request.files['file']
    df = pd.read_csv(file)

    # Generate synthetic data with privacy
    synthetic_data = generate_privacy_preserving_synthetic_data(df)

    # Convert DataFrame to CSV using BytesIO
    output = io.BytesIO()
    synthetic_data.to_csv(output, index=False)
    output.seek(0)

    return send_file(output, mimetype='text/csv', download_name='synthetic_data.csv', as_attachment=True)

# Run Flask app locally
if __name__ == '__main__':
    app.run(port=5000, debug=True)
