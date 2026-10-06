from etl.run import run_pipeline

if __name__ == "__main__":
    df = run_pipeline()
    print(df.head())
    print(df.isna().sum())