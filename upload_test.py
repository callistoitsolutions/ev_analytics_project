import pandas as pd
from elt.column_mapper import map_columns
from sqlalchemy import create_engine

# MySQL connection
engine = create_engine("mysql+pymysql://pbiuser:PbiPassword123!@localhost/ev_analytics")

# Load the file
file_path = "data/raw/new_ev_dataset.xlsx"
df = pd.read_excel(file_path)

# Map columns dynamically
df_mapped = map_columns(df)

# Optional: see mapping
print("Original columns:", df.columns.tolist())
print("Mapped columns:", df_mapped.columns.tolist())

# Upload to database
df_mapped.to_sql("ev_data", con=engine, if_exists="append", index=False)
print("✅ Data uploaded successfully!")
