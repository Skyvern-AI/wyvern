# -*- coding: utf-8 -*-
import polars as pl


def cast_float32_to_float64(df) -> pl.DataFrame:
    float32_cols = [
        col for col, dtype in zip(df.columns, df.dtypes) if dtype == pl.Float32
    ]
    return df.with_columns([df[col].cast(pl.Float64) for col in float32_cols])
