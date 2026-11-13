import sys
sys.path.insert(0, r"C:\Users\Ram Singh Bairwa\OneDrive\Desktop\youtube statics\.venv\Lib\site-packages")

import kagglehub
from kagglehub import KaggleDatasetAdapter

# Set the path to the file you'd like to load
file_path = "USvideos.csv"

print(f"Loading '{file_path}' from datasnaek/youtube-new using kagglehub...")

# Load the latest version
df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "datasnaek/youtube-new",
    file_path,
    pandas_kwargs={"nrows": 5, "encoding_errors": "replace"}
)

print("First 5 records:")
print(df.head())
