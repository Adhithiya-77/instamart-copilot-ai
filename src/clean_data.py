import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"

CLEAN_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD CUSTOMER DATA
# ==========================================

customers = pd.read_csv(RAW_DIR / "customers.csv")

print("Original customer records:", len(customers))


# ==========================================
# 3. CLEAN CITY NAMES
# ==========================================

customers["city"] = (
    customers["city"]
    .astype("string")
    .str.strip()
    .str.title()
)


# ==========================================
# 4. CLEAN GENDER VALUES
# ==========================================

gender_map = {
    "male": "male",
    "m": "male",
    "female": "female",
    "f": "female"
}

customers["gender"] = (
    customers["gender"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map(gender_map)
    .fillna("unknown")
)


# ==========================================
# 5. CLEAN AGE VALUES
# ==========================================

# Convert age to numeric
customers["age"] = pd.to_numeric(
    customers["age"],
    errors="coerce"
)

# Replace invalid ages with missing values
invalid_age = ~customers["age"].between(10, 100)

customers.loc[invalid_age, "age"] = float("nan")

# Calculate the median age for each city
city_median = customers.groupby("city")["age"].transform("median")

# Use the overall median if a city has no valid ages
overall_median = customers["age"].median()

city_median = city_median.fillna(overall_median)

# Fill missing ages and convert to integers
customers["age"] = (
    customers["age"]
    .fillna(city_median)
    .round()
    .astype("int64")
)


# ==========================================
# 6. CLEAN SIGNUP DATE
# ==========================================

customers["signup_date"] = pd.to_datetime(
    customers["signup_date"],
    errors="raise"
)


# ==========================================
# 7. SAVE CLEAN DATA
# ==========================================

output_file = CLEAN_DIR / "customers.csv"

customers.to_csv(
    output_file,
    index=False,
    date_format="%Y-%m-%d"
)


# ==========================================
# 8. DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 45)
print("CUSTOMER CLEANING RESULTS")
print("=" * 45)

print("\nTotal customers:", len(customers))

print("\nCity counts:")
print(customers["city"].value_counts().sort_index())

print("\nGender counts:")
print(customers["gender"].value_counts())

print("\nMissing ages:", customers["age"].isna().sum())

print("Minimum age:", customers["age"].min())

print("Maximum age:", customers["age"].max())

print("Missing signup dates:", customers["signup_date"].isna().sum())

print("Unique cities:", customers["city"].nunique())

print("\nCleaned file saved to:")
print(output_file)


# ==========================================
# 9. VALIDATE DATA
# ==========================================

assert len(customers) == 1200, (
    f"Expected 1200 customers, got {len(customers)}"
)

expected_cities = {
    "Pune": 227,
    "Delhi": 210,
    "Bengaluru": 197,
    "Chennai": 191,
    "Hyderabad": 191,
    "Mumbai": 184
}

actual_cities = customers["city"].value_counts().to_dict()

assert actual_cities == expected_cities, (
    f"City counts mismatch: {actual_cities}"
)

expected_genders = {
    "female": 610,
    "male": 560,
    "unknown": 30
}

actual_genders = customers["gender"].value_counts().to_dict()

assert actual_genders == expected_genders, (
    f"Gender counts mismatch: {actual_genders}"
)

assert customers["age"].notna().all(), "Missing ages remain!"

assert customers["age"].between(18, 60).all(), (
    "Unexpected ages found!"
)

assert customers["signup_date"].notna().all(), (
    "Missing signup dates remain!"
)

print("\nALL CUSTOMER CHECKS PASSED!")