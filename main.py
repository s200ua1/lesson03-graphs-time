import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("365일 동안의 일별 박스오피스 데이터를 이용해 영화의 관객 변화를 살펴봅니다.")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 실제 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자형 열 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# ==================================================
# 그래프 1
# ==================================================
st.header("1. 영화별 일관객 변화")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()
movie_df = movie_df.sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig1.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,.0f}명"
    "<extra></extra>"
)

fig1.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)"
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: "
    "영화가 날짜에 따라 얼마나 많은 관객을 모았는지와 관객 수의 변화 추이를 알 수 있습니다."
)


# ==================================================
# 그래프 2
# ==================================================
st.divider()

st.header("2. 기간 동안 일관객 합계가 가장 큰 영화 5편")

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)
)

top5_movie_names = top5_movies["영화명"].tolist()

top5_df = df[df["영화명"].isin(top5_movie_names)].copy()
top5_df = top5_df.sort_values(["날짜", "영화명"])

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    title="일관객 합계 상위 5편의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=
    "영화: %{fullData.name}<br>"
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,.0f}명"
    "<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    legend_title="영화",
    legend=dict(
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    )
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: "
    "전체 기간 동안 관객을 많이 모은 영화 5편의 날짜별 관객 수 변화와 흥행 추이를 비교할 수 있습니다."
)


# ==================================================
# 그래프 3
# ==================================================
st.divider()

st.header("3. 날짜별 10위권 일관객 합계")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total
    .sort_values("일관객", ascending=False)
    .head(3)
)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)

fig3.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "10위권 일관객 합계: %{y:,.0f}명"
    "<extra></extra>"
)

fig3.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 합계(명)"
)

for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=row["날짜"].strftime("%Y-%m-%d"),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-45
    )

st.plotly_chart(fig3, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: "
    "날짜별 영화관 관객 규모의 변화를 확인하고, 10위권 영화의 관객 합계가 특히 높았던 날을 알 수 있습니다."
)


# ==================================================
# 그래프 4
# ==================================================
st.divider()

st.header("4. 영화별 일관객 합계 TOP 10")

movie_total = (
    df.groupby("영화명")["일관객"]
    .sum()
    .reset_index()
)

movie_days = (
    df.groupby("영화명")["날짜"]
    .nunique()
    .reset_index()
    .rename(columns={"날짜": "10위권에 든 날수"})
)

movie_rank = movie_total.merge(
    movie_days,
    on="영화명"
)

top10 = (
    movie_rank
    .sort_values("일관객", ascending=False)
    .head(10)
    .copy()
)

top10 = top10.sort_values("일관객", ascending=True)

fig4 = px.bar(
    top10,
    x="일관객",
    y="영화명",
    orientation="h",
    title="영화별 기간 전체 일관객 합계 TOP 10",
    labels={
        "영화명": "영화",
        "일관객": "기간 전체 일관객 합계"
    },
    hover_data={
        "일관객": ":,.0f",
        "10위권에 든 날수": True
    }
)

fig4.update_traces(
    hovertemplate=
    "영화: %{y}<br>"
    "기간 전체 일관객: %{x:,.0f}명<br>"
    "10위권에 든 날수: %{customdata[0]}일"
    "<extra></extra>",
    customdata=top10[["10위권에 든 날수"]].values
)

fig4.update_layout(
    xaxis_title="기간 전체 일관객 합계(명)",
    yaxis_title="영화",
    hovermode="closest"
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: "
    "전체 기간 동안 가장 많은 관객을 모은 영화 10편과 각 영화가 10위권에 머문 기간을 비교할 수 있습니다."
)


# ==================================================
# 그래프 5
# ==================================================
st.divider()

st.header("5. 월 × 요일별 10위권 일관객 합계")

# 날짜에서 월과 요일 추출
heatmap_df = df.copy()

heatmap_df["월"] = heatmap_df["날짜"].dt.month

weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}

heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek.map(weekday_map)

# 월 × 요일별 일관객 합계
heatmap_data = (
    heatmap_df
    .groupby(["월", "요일"])["일관객"]
    .sum()
    .reset_index()
)

# 요일 순서 고정
weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

heatmap_data["요일"] = pd.Categorical(
    heatmap_data["요일"],
    categories=weekday_order,
    ordered=True
)

# 피벗
heatmap_pivot = heatmap_data.pivot(
    index="월",
    columns="요일",
    values="일관객"
)

# 월 순서 정렬
heatmap_pivot = heatmap_pivot.sort_index()

fig5 = px.imshow(
    heatmap_pivot,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    },
    x=weekday_order,
    y=heatmap_pivot.index,
    text_auto=".2s",
    aspect="auto",
    title="월 × 요일별 10위권 일관객 합계",
    color_continuous_scale="Blues"
)

fig5.update_traces(
    hovertemplate=
    "%{y}월 %{x}<br>"
    "일관객 합계: %{z:,.0f}명"
    "<extra></extra>"
)

fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월"
)

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "이 그래프로 알 수 있는 것: "
    "월과 요일에 따라 10위권 영화의 일관객 합계가 어떻게 달라지는지 한눈에 비교할 수 있습니다."
)


# ==================================================
# 앞으로 추가할 그래프 영역
# ==================================================
st.divider()

st.header("6. 다음 그래프")
st.caption("앞으로 새로운 그래프를 추가할 공간입니다.")

st.divider()

st.header("7. 다음 그래프")
st.caption("앞으로 새로운 그래프를 추가할 공간입니다.")
