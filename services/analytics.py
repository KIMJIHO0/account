import pandas as pd

def month_summary(df: pd.DataFrame, year_month: str) -> pd.DataFrame:
    """
    year_month: "YYYY-MM" 문자열 기준으로 필터 후
    수입/지출 합계를 category별로 반환
    """
    if df.empty:
        return pd.DataFrame(columns=["category", "수입", "지출", "순합"])
    dff = df[df["date"].str.startswith(year_month)].copy()
    if dff.empty:
        return pd.DataFrame(columns=["category", "수입", "지출", "순합"])
    inc = dff[dff["type"] == "수입"].groupby("category")["amount"].sum().rename("수입")
    exp = dff[dff["type"] == "지출"].groupby("category")["amount"].sum().rename("지출")
    out = pd.concat([inc, exp], axis=1).fillna(0).astype(int)
    out["순합"] = out["수입"] - out["지출"]
    out = out.reset_index()
    return out.sort_values("순합", ascending=False)

def daily_net_series(df: pd.DataFrame, year_month: str):
    """일자별 순증감(수입-지출) 시리즈"""
    if df.empty:
        return pd.Series(dtype=int)
    dff = df[df["date"].str.startswith(year_month)].copy()
    if dff.empty:
        return pd.Series(dtype=int)
    dff["sign_amt"] = dff.apply(lambda r: r["amount"] if r["type"] == "수입" else -r["amount"], axis=1)
    ser = dff.groupby("date")["sign_amt"].sum().sort_index()
    return ser
