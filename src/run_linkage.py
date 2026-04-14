import pandas as pd
import splink.comparison_library as cl
from splink import DuckDBAPI, Linker, SettingsCreator, block_on

# Load data
df_a = pd.read_csv("data/raw/hospital_a.csv")
df_b = pd.read_csv("data/raw/hospital_b.csv")

# Backend
db_api = DuckDBAPI()

# Settings
settings = SettingsCreator(
    link_type="link_only",
    unique_id_column_name="record_id",
    comparisons=[
        cl.ExactMatch("dob"),
        cl.JaroAtThresholds("first_name"),
        cl.JaroAtThresholds("surname"),
        cl.ExactMatch("postcode"),
    ],
    blocking_rules_to_generate_predictions=[
        block_on("surname"),
    ],
)

# Linker
linker = Linker([df_a, df_b], settings, db_api)

# --- TRAINING (optional but good) ---
linker.training.estimate_u_using_random_sampling(max_pairs=1e5)

# --- PREDICT ---
pairwise_predictions = linker.inference.predict()

# Save results
df_predictions = pairwise_predictions.as_pandas_dataframe()
df_predictions.to_csv("data/output/predictions.csv", index=False)

print(df_predictions.head())