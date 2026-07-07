import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, RobustScaler, MinMaxScaler
import category_encoders as ce


def encode_categoricals(df: pd.DataFrame, encoding_map: dict, target: pd.Series = None) -> pd.DataFrame:
    """
    Deterministic execution of encoding strategy decided by
    PreprocessingAgent._decide_encoding_strategy.
    target is only required if encoding_map contains "target_encode" for any column.
    """
    df = df.copy()

    for column, strategy in encoding_map.items():
        if column not in df.columns:
            continue

        if strategy == "one_hot":
            dummies = pd.get_dummies(df[column], prefix=column, drop_first=True)
            df = pd.concat([df.drop(columns=[column]), dummies], axis=1)

        elif strategy == "ordinal":
            encoder = OrdinalEncoder()
            df[column] = encoder.fit_transform(df[[column]])

        elif strategy == "target_encode":
            if target is None:
                raise ValueError(f"target_encode strategy for '{column}' requires target values, none provided")
            encoder = ce.TargetEncoder(cols=[column])
            df[column] = encoder.fit_transform(df[column], target)

        elif strategy == "drop_column":
            df = df.drop(columns=[column])

        else:
            raise ValueError(f"Unknown encoding strategy '{strategy}' for column '{column}'")

    return df


def scale_numeric(df: pd.DataFrame, scaling_map: dict) -> pd.DataFrame:
    """
    Deterministic execution of scaling strategy decided by
    PreprocessingAgent._decide_scaling_strategy.
    """
    df = df.copy()

    for column, strategy in scaling_map.items():
        if column not in df.columns:
            continue

        if strategy == "none":
            continue
        elif strategy == "standard":
            scaler = StandardScaler()
        elif strategy == "robust":
            scaler = RobustScaler()
        elif strategy == "minmax":
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling strategy '{strategy}' for column '{column}'")

        df[column] = scaler.fit_transform(df[[column]])

    return df