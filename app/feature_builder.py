import numpy as np

def build_model_features(df):
    df = df.copy()

    df["log_gross_sqft"] = np.log10(df["gross_sqft"])
    df["log_dist_to_station"] = np.log10(df["dist_to_station"])

    return df[[
        "within_half_mi",
        "neighborhood",
        "building_class_category",
        "log_gross_sqft",
        "build_age_yrs",
        "log_dist_to_station"
    ]]