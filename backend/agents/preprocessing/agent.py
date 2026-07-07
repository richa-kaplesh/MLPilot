from agents.base import BaseAgent
from database.postgres.connection import SessionLocal
from database.postgres.models.eda_report import EDAReport
import json


class PreprocessingAgent(BaseAgent):

    def _load_eda_report(self) -> EDAReport:
        """
        Fetch the EDAReport row for this pipeline's dataset.
        Simplified: dataset_id now comes directly from BaseAgent, no
        PipelineRun lookup needed.
        """
        db = SessionLocal()
        try:
            eda_report = db.query(EDAReport).filter(
                EDAReport.dataset_id == self.dataset_id
            ).first()

            if not eda_report:
                raise ValueError(
                    f"No EDAReport found for dataset_id {self.dataset_id}. "
                    f"Data Intelligence agent must run before Preprocessing."
                )

            return eda_report
        finally:
            db.close()

    def _decide_missing_value_strategy(self, eda_report: EDAReport) -> dict:
        """
        LLM judgment: for each column with missing values, decide the strategy.
        Uses missingness %, statistical significance vs target, and
        feature_importance — not raw correlation.
        """
        missing_values = eda_report.missing_values or {}
        target_analysis = eda_report.target_analysis or {}
        feature_importance = eda_report.feature_importance or {}
        target_column = eda_report.target_column

        columns_with_missing = {
            col: pct for col, pct in missing_values.items() if pct and pct > 0
        }
        if not columns_with_missing:
            return {}

        categorical_tests = target_analysis.get("categorical_feature_tests", {})
        numerical_tests = target_analysis.get("numerical_feature_tests", {})

        column_context = {}
        for col, missing_pct in columns_with_missing.items():
            significance = categorical_tests.get(col) or numerical_tests.get(col)

            column_context[col] = {
                "missing_pct": missing_pct,
                "importance_score": feature_importance.get(col),
                "significant_vs_target": significance.get("significant") if significance else None,
                "p_value_vs_target": significance.get("p_value") if significance else None
            }

        prompt = f"""You are deciding missing-value imputation strategy for a dataset.
Problem statement: {self.problem_statement}
Target column: {target_column}

For each column below, you're given: % missing, feature importance score
(0-1, higher means more predictive of the target), whether it's statistically
significant vs the target (p < 0.05), and the p-value itself.

{json.dumps(column_context, indent=2)}

For each column, choose exactly one strategy: "mean", "median", "mode", "drop_column", "forward_fill".

Guidance:
- High missing % (>50%) AND low importance/not significant -> drop_column
- High missing % but high importance or significant vs target -> impute carefully
  (median for skewed numeric, mode for categorical), don't drop a column that matters
- Low missing % (<5%) -> safe to impute regardless of importance, simple strategies are fine
- Numeric + skewed distribution -> prefer median over mean
- Categorical -> mode

Respond ONLY with valid JSON, no preamble, in this exact format:
{{"column_name": "strategy_name", ...}}
"""

        response = self.llm.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return json.loads(response.choices[0].message.content)

    def _decide_encoding_strategy(self, eda_report: EDAReport, df) -> dict:
        """
        LLM judgment: for each categorical column, decide one-hot vs ordinal
        vs target vs drop, based on cardinality + relevance to target.
        """
        data_types = eda_report.data_types or {}
        feature_importance = eda_report.feature_importance or {}
        target_analysis = eda_report.target_analysis or {}
        target_column = eda_report.target_column

        categorical_cols = [
            col for col, dtype in data_types.items()
            if dtype == "object" and col != target_column and col in df.columns
        ]
        if not categorical_cols:
            return {}

        categorical_tests = target_analysis.get("categorical_feature_tests", {})

        column_context = {}
        for col in categorical_cols:
            cardinality = df[col].nunique()
            significance = categorical_tests.get(col)

            column_context[col] = {
                "cardinality": int(cardinality),
                "importance_score": feature_importance.get(col),
                "significant_vs_target": significance.get("significant") if significance else None
            }

        prompt = f"""You are deciding categorical encoding strategy for a dataset.
Problem statement: {self.problem_statement}
Target column: {target_column}

For each categorical column below: cardinality (number of unique values),
feature importance score (0-1), and whether it's statistically significant vs target.

{json.dumps(column_context, indent=2)}

For each column, choose exactly one strategy: "one_hot", "ordinal", "target_encode", "drop_column".

Guidance:
- Low cardinality (<=10) -> one_hot
- High cardinality (>10) and important/significant -> target_encode
- High cardinality and not important -> drop_column
- Natural order exists (e.g. size: small/medium/large) -> ordinal

Respond ONLY with valid JSON, no preamble, in this exact format:
{{"column_name": "strategy_name", ...}}
"""

        response = self.llm.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return json.loads(response.choices[0].message.content)

    def _decide_scaling_strategy(self, eda_report: EDAReport, df) -> dict:
        """
        LLM judgment: for each numeric column, decide scaler type based on
        distribution shape (normality/skewness) already computed in EDA.
        """
        data_types = eda_report.data_types or {}
        normality = eda_report.normality or {}
        skewness = eda_report.skewness or {}
        target_column = eda_report.target_column

        numeric_cols = [
            col for col, dtype in data_types.items()
            if dtype in ("int64", "float64") and col != target_column and col in df.columns
        ]
        if not numeric_cols:
            return {}

        column_context = {}
        for col in numeric_cols:
            norm_info = normality.get(col, {})
            column_context[col] = {
                "is_normal": norm_info.get("is_normal"),
                "skewness": skewness.get(col)
            }

        prompt = f"""You are deciding numeric scaling strategy for a dataset.
Problem statement: {self.problem_statement}

For each numeric column below: whether its distribution is approximately
normal (Shapiro-Wilk test), and its skewness value.

{json.dumps(column_context, indent=2)}

For each column, choose exactly one strategy: "standard", "robust", "minmax", "none".

Guidance:
- Approximately normal distribution -> standard
- Skewed or has outliers (|skewness| > 1) -> robust
- Bounded/known range needed -> minmax
- Default to standard for normal, robust for skewed

Respond ONLY with valid JSON, no preamble, in this exact format:
{{"column_name": "strategy_name", ...}}
"""

        response = self.llm.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return json.loads(response.choices[0].message.content)

    # run() not yet written — pending outlier handling functions first