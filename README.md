# Brooklyn Home Price Prediction API

Productionized machine learning project for predicting **Brooklyn residential home sale prices** using **Python, scikit-learn, FastAPI, Docker, and AWS**.

**Live API:** http://brooklyn-home-price-alb-1717097516.us-east-1.elb.amazonaws.com/docs#/  
**Formatted frontend:** http://d1gedfxor1cz4c.cloudfront.net

---

## Overview

This project predicts **Brooklyn residential sale prices** from property characteristics, neighborhood context, and transit accessibility.

The workflow starts with raw NYC home sales data, enriches each property with **PLUTO geospatial data** and **nearest subway distance**, applies structured preprocessing and feature engineering, compares multiple regression models, and serves the final model through a **FastAPI inference API** deployed on **AWS EC2 behind an Application Load Balancer**.

This repo reflects a full applied ML workflow:
- raw data preprocessing
- exploratory analysis and outlier handling
- feature engineering and preprocessing pipeline creation
- model comparison and selection
- export of a reusable end-to-end inference pipeline
- API packaging and AWS deployment

---

## Business Case

Accurate home price estimation is useful for:
- real estate analytics
- internal pricing support
- property valuation benchmarking
- identifying how location and property characteristics influence sale price

The project was designed to answer a practical question:

> Given a Brooklyn residential property’s size, age, neighborhood, building class, and subway accessibility, what sale price would the model predict?

---

## Data Sources

This project uses NYC property and transit datasets for Brooklyn residential properties:
- **NYC rolling sales data** for historical transactions
- **PLUTO** property data for lot-level geographic attributes
- **MTA subway station data** for nearest-station distance features

> Raw source files are not included in the repository because of file size.

---

## End-to-End Workflow

### 1) Preprocessing
The preprocessing notebook builds the initial cleaned dataset used across the project.

Key steps:
- loaded the **Brooklyn** sheet from the rolling sales file
- standardized column names
- converted numeric fields into usable numeric types
- created **`build_age_yrs = 2026 - year_built`**
- built a **BBL** key from borough, block, and lot
- filtered to **residential sales only**
- removed invalid transactions such as non-positive sale prices
- merged **PLUTO latitude/longitude** into the sales records
- dropped rows missing geolocation
- loaded **Brooklyn subway station** data
- used a **BallTree with haversine distance** to find the nearest station for each property
- created **`nearest_station`** and **`distance_to_station`**

Output artifact:
- `clean_data/01_preprocessing.parquet`

### 2) Exploratory Analysis
The EDA notebook cleaned the target and stabilized the modeling dataset.

Key steps:
- removed very small sale prices likely to be non-market transactions
- created the target **`log_sale_price = log10(sale_price)`**
- removed missing or zero **gross square footage**
- created **`log_gross_sqft`**
- trimmed **gross square feet** outliers above the **99.5th percentile**
- created **`price_sqft`** for exploratory filtering
- trimmed **price per square foot** outside the **1st to 99.5th percentile** range
- created **`within_half_mi`** from subway distance
- created **`log_dist_to_station`**
- standardized **neighborhood** names
- standardized **building class category** labels
- removed sparse categories with too few observations

Output artifact:
- `clean_data/02_exploratory_analysis.parquet`

### 3) Feature Engineering
This notebook built the final model-ready design matrix.

Final input features:
- **Binary:** `within_half_mi`
- **Categorical:** `neighborhood`, `building_class_category`
- **Numeric:** `log_gross_sqft`, `build_age_yrs`, `log_dist_to_station`

Preprocessing steps:
- evaluated numeric predictors with **VIF** for multicollinearity
- removed `residential_units` from the final numeric feature set
- used **StandardScaler** on numeric features
- used **OneHotEncoder(handle_unknown="ignore")** on categorical features
- combined everything with a **ColumnTransformer**

Final transformed matrix shape:
- **5,596 rows × 63 features**

Output artifacts:
- `clean_data/03_feature_engineering.parquet`
- `models/preprocessing_pipeline.joblib`

### 4) Modeling
The modeling notebook compared multiple regression approaches on the engineered dataset.

Models tested:
- **OLS / Linear Regression**
- **Elastic Net**
- **Random Forest Regressor**
- **XGBoost Regressor**

Primary evaluation metric:
- **MAE in dollars**

Supporting metrics:
- **R-squared**
- **Adjusted R-squared**

Final selected model:
- **Elastic Net**

Saved model artifact:
- `models/home_price_model.joblib`

### 5) Export Pipeline
The final notebook packaged the project into a reusable inference artifact.

The exported pipeline combines:
1. raw input feature builder
2. saved preprocessing pipeline
3. final trained model

Saved inference artifact:
- `models/brooklyn_price_pipeline_raw_inputs.joblib`

This made it possible to move from notebook experimentation to API-based prediction.

---

## Key Notebook Insights

These insights come directly from the project notebooks.

### Dataset progression
- Rows after preprocessing: **8,229**
- Rows after removing invalid/missing square footage: **5,731**
- Rows after trimming gross square footage outliers: **5,702**
- Rows after filtering price-per-square-foot extremes: **5,615**
- Rows after neighborhood/category cleanup: **5,596**

### Property size distribution after cleanup
- Median gross square feet: **2,209**
- Mean gross square feet: **2,700.90**
- 99.5th percentile cutoff used for trimming: **44,122 sq ft**

### Transit accessibility findings
- Properties within half a mile of a subway station: **4,107**
- Properties beyond half a mile: **1,508**
- Correlation between **distance to station** and **log sale price**: **-0.2998**

This suggests that homes farther from the subway tended to have lower sale prices on average in the working dataset.

### Most common building categories
- **two_family_dwellings:** 2,383
- **one_family_dwellings:** 1,656
- **three_family_dwellings:** 903
- **rentals_walkup_apartments:** 630

### Interpretable OLS findings
From the statsmodels OLS summary and coefficient table:
- **`log_gross_sqft`** coefficient: **0.1157**
- **`within_half_mi`** coefficient: **0.0419**
- **`log_dist_to_station`** coefficient: **0.0091**
- **`build_age_yrs`** coefficient: **-0.0078**

The strongest interpretable signals in the selected summary were:
- larger homes were associated with higher predicted prices
- homes within half a mile of a station were associated with higher predicted prices

---

## Model Results

### Baseline: OLS / Linear Regression
- **Train Adjusted R²:** 0.599
- **Test Adjusted R²:** 0.541
- **Test MAE:** **$474,825.12**
- **Test RMSE:** **$908,444.85**
- **Median Brooklyn sale price in dataset:** **$1,216,998.36**

### Elastic Net
- **Best alpha:** 0.000251
- **Best l1_ratio:** 0.9
- **Train Adjusted R²:** 0.599
- **Test Adjusted R²:** 0.542
- **Test MAE:** **$474,111.60**

### Random Forest
- **Train Adjusted R²:** 0.737
- **Test Adjusted R²:** 0.541
- **Test MAE:** **$482,645.38**

### XGBoost
- **Train Adjusted R²:** 0.701
- **Test Adjusted R²:** 0.542
- **Test MAE:** **$487,822.11**

### Final ranking by MAE
| Model | Train Adjusted R² | Test Adjusted R² | MAE |
|---|---:|---:|---:|
| Elastic Net | 0.599 | 0.542 | $474,111.60 |
| OLS | 0.599 | 0.541 | $474,825.12 |
| Random Forest | 0.737 | 0.541 | $482,645.38 |
| XGBoost | 0.701 | 0.542 | $487,822.11 |

**Final model chosen:** Elastic Net  
Elastic Net slightly outperformed the alternatives on test MAE while maintaining similar explanatory power, so it was selected as the production model.

---

## API and Deployment

After model selection, the project was productionized as a **FastAPI application**.

Deployment stack:
- **FastAPI** for serving predictions
- **Uvicorn** as the application server
- **Docker** for containerization
- **AWS EC2** for hosting
- **Application Load Balancer (ALB)** for external access
- **CloudFront/S3 frontend** linked from the repo for a formatted interface

Live resources listed in the repository:
- **API docs:** http://brooklyn-home-price-alb-1717097516.us-east-1.elb.amazonaws.com/docs#/ 
- **Formatted frontend:** http://d1gedfxor1cz4c.cloudfront.net

---

## Repository Structure

```text
brooklyn-home-price-api/
├── app/
├── models/
├── notebooks/
├── Dockerfile
├── requirements.txt
├── brooklyn_home_sales_unique_values.md
└── Readme.md
```

---

## Tech Stack

- Python
- Pandas
- NumPy
- scikit-learn
- XGBoost
- statsmodels
- FastAPI
- Uvicorn
- Docker
- AWS EC2
- AWS Application Load Balancer

---

## Example Prediction Inputs

The exported pipeline was tested on raw property inputs such as:
- neighborhood
- building class category
- gross square footage
- distance to station
- building age
- within-half-mile subway flag

Those raw inputs were passed through:
1. a custom feature builder
2. the saved preprocessing pipeline
3. the trained Elastic Net model

This setup made the project reusable for live inference instead of notebook-only scoring.

---

## Why This Project Matters

This project demonstrates:
- applied regression modeling on real housing data
- geospatial feature engineering using external datasets
- structured preprocessing with reusable sklearn pipelines
- model comparison using business-readable error metrics
- transition from notebook analysis to deployable API infrastructure

It is both a **machine learning modeling project** and a **production ML deployment project**.
