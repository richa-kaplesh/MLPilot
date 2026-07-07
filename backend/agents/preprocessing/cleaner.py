import pandas as pd


def impute_missing(df: pd.DataFrame, strategy_map: dict) -> pd.DataFrame:
    """
    Deterministic execution of missing-value strategy decided by
    PreprocessingAgent._decide_missing_value_strategy.
    """
    df = df.copy()

    for column, strategy in strategy_map.items():
        if column not in df.columns:
            continue

        if strategy == "mean":
            df[column] = df[column].fillna(df[column].mean())
        elif strategy == "median":
            df[column] = df[column].fillna(df[column].median())
        elif strategy == "mode":
            mode_value = df[column].mode()
            if not mode_value.empty:
                df[column] = df[column].fillna(mode_value[0])
        elif strategy == "drop_column":
            df = df.drop(columns=[column])
        elif strategy == "forward_fill":
            df[column] = df[column].ffill()
        else:
            raise ValueError(f"Unknown imputation strategy '{strategy}' for column '{column}'")

    return df

def handle_outliers(df: pd.DataFrame, outlier_strategy_map: dict) -> pd.DataFrame:
    """
    Deterministic execution of outlier strategy decided by
    PreprocessingAgent._decide_outlier_strategy.
    Uses IQR bounds recomputed fresh here (cheap), rather than pulling
    stale bounds from the EDA report — bounds should reflect current data
    state, since imputation/encoding already ran before this step.
    """
    df = df.copy()

    for column, strategy in outlier_strategy_map.items():
        if column not in df.columns:
            continue

        if strategy == "leave":
            continue

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        if strategy == "clip":
            df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        elif strategy == "remove":
            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        else:
            raise ValueError(f"Unknown outlier strategy '{strategy}' for column '{column}'")

    return df