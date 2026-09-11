# UP EV Policy — Streamlit Dashboard

## 1. Add your data
Copy these files from your Colab `OUT_DIR` into this repo's `data/` folder
(exact filenames, as produced by the original notebook):

- `master_long.csv`
- `b_growth_comparison.csv`
- `c_up_category_share.csv`
- `extra1_segment_growth.csv`
- `d_forecast_12m.csv`
- `extra2_policy_design_comparison.csv`

## 2. Push to GitHub
```
git init
git add .
git commit -m "EV policy dashboard"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## 3. Deploy
Go to https://share.streamlit.io → New app → pick this repo/branch →
main file path: `app.py` → Deploy.

## Run locally (optional)
```
pip install -r requirements.txt
streamlit run app.py
```
