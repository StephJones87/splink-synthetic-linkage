# This allows us to use modern type hints (like tuple[...] instead of Tuple)
# and also delays evaluation of type hints (useful for larger projects)
from __future__ import annotations

# Standard Python random module (used for reproducibility + corruption logic)
import random

# dataclass = cleaner way to define structured data (like a row schema)
# asdict = converts a dataclass instance → dictionary
from dataclasses import dataclass, asdict

# Used to create file paths in a clean, OS-independent way
from pathlib import Path

# Pandas for working with tabular data
import pandas as pd

# Faker generates synthetic but realistic-looking data
from faker import Faker


# Create a Faker instance with UK-specific data (names, postcodes etc.)
fake = Faker("en_GB")

# Seed BOTH random systems so results are reproducible
# (i.e. same fake data every time you run this script)
random.seed(42)      # Python's random module
Faker.seed(42)       # Faker's internal randomness


# -------------------------------
# DEFINE A PERSON STRUCTURE
# -------------------------------

# A dataclass is like a lightweight schema for a "person"
# Think: one row in your dataset
@dataclass
class Person:
    person_id: int
    first_name: str
    surname: str
    dob: str
    postcode: str
    city: str
    email: str
    phone: str


# -------------------------------
# CREATE CLEAN "GROUND TRUTH" DATA
# -------------------------------

def make_base_people(n: int = 1000) -> pd.DataFrame:
    """
    Create a clean dataset of n people.
    This is your "true" dataset before introducing errors.
    """

    rows = []

    # Loop to create n people
    for person_id in range(1, n + 1):

        # Generate fake but realistic attributes
        first_name = fake.first_name()
        surname = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
        postcode = fake.postcode()
        city = fake.city()
        email = fake.email()
        phone = fake.phone_number()

        # Create a Person object, then convert it to a dictionary
        rows.append(
            asdict(
                Person(
                    person_id=person_id,
                    first_name=first_name,
                    surname=surname,
                    dob=dob,
                    postcode=postcode,
                    city=city,
                    email=email,
                    phone=phone,
                )
            )
        )

    # Convert list of dictionaries → pandas DataFrame
    return pd.DataFrame(rows)


# -------------------------------
# HELPER: CREATE A SMALL TYPO
# -------------------------------

def small_typo(value: str) -> str:
    """
    Introduce a small typo by swapping two adjacent characters.
    Example: "Smith" → "Smtih"
    """

    # If value is too short, don't modify it
    if not value or len(value) < 3:
        return value

    # Pick a random position in the string
    i = random.randint(0, len(value) - 2)

    # Convert string → list (so we can modify characters)
    chars = list(value)

    # Swap two adjacent characters
    chars[i], chars[i + 1] = chars[i + 1], chars[i]

    # Convert back to string
    return "".join(chars)


# -------------------------------
# CORRUPT A RECORD (SIMULATE REAL DATA ISSUES)
# -------------------------------

def corrupt_record(row: pd.Series) -> pd.Series:
    """
    Take a clean row and randomly introduce errors.
    This simulates real-world messy data.
    """

    # Copy so we don't overwrite the original row
    row = row.copy()

    # 20% chance: typo in first name
    if random.random() < 0.20:
        row["first_name"] = small_typo(str(row["first_name"]))

    # 20% chance: typo in surname
    if random.random() < 0.20:
        row["surname"] = small_typo(str(row["surname"]))

    # 15% chance: missing email
    if random.random() < 0.15:
        row["email"] = None

    # 15% chance: missing phone
    if random.random() < 0.15:
        row["phone"] = None

    # 10% chance: remove space from postcode (common formatting issue)
    if random.random() < 0.10 and pd.notna(row["postcode"]):
        row["postcode"] = str(row["postcode"]).replace(" ", "")

    # 10% chance: lowercase city (inconsistent formatting)
    if random.random() < 0.10 and pd.notna(row["city"]):
        row["city"] = str(row["city"]).lower()

    return row


# -------------------------------
# BUILD TWO DATASETS FOR LINKAGE
# -------------------------------

def build_linkage_datasets(base_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create two datasets (A and B) that:
    - share some people (duplicates across datasets)
    - have some unique people
    - contain errors

    Also creates a "truth" table showing which records match.
    """

    # Select 700 people that appear in BOTH datasets
    both_ids = set(random.sample(list(base_df["person_id"]), 700))

    # Remaining people
    remaining = [x for x in base_df["person_id"] if x not in both_ids]

    # 150 people only in dataset A
    a_only = set(random.sample(remaining, 150))

    # Update remaining
    remaining = [x for x in remaining if x not in a_only]

    # 150 people only in dataset B
    b_only = set(random.sample(remaining, 150))


    # Build dataset A (shared + A-only)
    df_a_people = base_df[base_df["person_id"].isin(both_ids | a_only)].copy()

    # Build dataset B (shared + B-only)
    df_b_people = base_df[base_df["person_id"].isin(both_ids | b_only)].copy()


    # Introduce errors into both datasets
    df_a_people = df_a_people.apply(corrupt_record, axis=1)
    df_b_people = df_b_people.apply(corrupt_record, axis=1)


    # Add record IDs (these simulate real system IDs)
    df_a_people["record_id"] = [f"A{i:04d}" for i in range(1, len(df_a_people) + 1)]
    df_b_people["record_id"] = [f"B{i:04d}" for i in range(1, len(df_b_people) + 1)]

    # Label source datasets
    df_a_people["source_dataset"] = "hospital_a"
    df_b_people["source_dataset"] = "hospital_b"


    # -------------------------------
    # BUILD GROUND TRUTH MATCHES
    # -------------------------------

    # Find matching records between A and B using person_id
    truth = (
        df_a_people[df_a_people["person_id"].isin(both_ids)][["record_id", "person_id"]]
        .merge(
            df_b_people[df_b_people["person_id"].isin(both_ids)][["record_id", "person_id"]],
            on="person_id",
            suffixes=("_a", "_b"),
        )
    )

    # This gives you:
    # record_id_a | record_id_b | person_id
    # → which records truly match


    # Remove person_id from datasets (this simulates real-world scenario
    # where you DON'T have a perfect ID)
    return (
        df_a_people.drop(columns=["person_id"]),
        df_b_people.drop(columns=["person_id"]),
        truth,
    )


# -------------------------------
# MAIN SCRIPT (RUN EVERYTHING)
# -------------------------------

if __name__ == "__main__":

    # Create output directory
    outdir = Path("data/raw")
    outdir.mkdir(parents=True, exist_ok=True)

    # Step 1: create clean dataset
    base = make_base_people(1000)

    # Step 2: create messy datasets + truth table
    a, b, truth = build_linkage_datasets(base)

    # Step 3: save to CSV
    a.to_csv(outdir / "hospital_a.csv", index=False)
    b.to_csv(outdir / "hospital_b.csv", index=False)
    truth.to_csv(outdir / "ground_truth_links.csv", index=False)