import pandas as pd
# 분석용 집계 함수: 월별 카테고리 합계/일자별 순증감 시리즈 생성
def month_summary(df: pd.DataFrame, year_month: str) -> pd.DataFrame:
    """
    year_month: 'YYYY-MM' 문자열 (예: '2025-08')
    반환: 카테고리별 수입/지출/순합(수입-지출) 테이블
    - 그래프 막대 차트에 사용
    """
    if df.empty:
        return pd.DataFrame(columns=["category", "수입", "지출", "순합"])

    # 지정 월만 필터
    dff = df[df["date"].str.startswith(year_month)].copy()
    if dff.empty:
        return pd.DataFrame(columns=["category", "수입", "지출", "순합"])

    # 수입/지출 각각 카테고리별 합계
    inc = dff[dff["type"] == "수입"].groupby("category")["amount"].sum().rename("수입")
    exp = dff[dff["type"] == "지출"].groupby("category")["amount"].sum().rename("지출")

    # 두 시리즈를 합치고 NaN을 0으로 채움
    out = pd.concat([inc, exp], axis=1).fillna(0).astype(int)
    out["순합"] = out["수입"] - out["지출"]
    return out.reset_index().sort_values("순합", ascending=False)

def daily_net_series(df: pd.DataFrame, year_month: str):
    """
    일자별 '순증감(수입-지출)' 시리즈 반환.
    - 선 그래프에 사용.
    """
    if df.empty:
        return pd.Series(dtype=int)

    dff = df[df["date"].str.startswith(year_month)].copy()
    if dff.empty:
        return pd.Series(dtype=int)

    # 수입은 +, 지출은 - 로 부호 적용
    dff["sign_amt"] = dff.apply(lambda r: r["amount"] if r["type"] == "수입" else -r["amount"], axis=1)
    ser = dff.groupby("date")["sign_amt"].sum().sort_index()
    return ser
