import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)


# ============================================================
# 데이터 주소
# ============================================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_daily.csv"
)


# ============================================================
# 데이터 불러오기
# ============================================================

@st.cache_data
def load_data():
    """
    GitHub에 있는 CSV 파일을 불러옵니다.

    한 번 불러온 데이터는 Streamlit이 캐시하기 때문에
    화면을 조작할 때마다 다시 다운로드하지 않습니다.
    """

    df = pd.read_csv(DATA_URL)

    # 날짜는 '20250901' 같은 8자리 문자열로 들어옵니다.
    # 이를 실제 날짜(datetime)로 변환합니다.
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
    )

    # 숫자 열은 숫자로 변환합니다.
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # 날짜와 순위를 기준으로 정렬합니다.
    df = df.sort_values(
        ["날짜", "순위"]
    ).reset_index(drop=True)

    return df


# ============================================================
# 그래프 설명 영역
# ============================================================

def show_graph_explanation(text=None):
    """
    그래프 아래에
    '이 그래프로 알 수 있는 것' 영역을 만듭니다.
    """

    st.markdown("**이 그래프로 알 수 있는 것**")

    if text:
        st.write(text)
    else:
        st.caption(
            "여기에 이 그래프에서 알 수 있는 내용을 적어 주세요."
        )


# ============================================================
# 데이터 불러오기
# ============================================================

try:
    df = load_data()

except Exception:
    st.error("데이터를 불러오지 못했습니다.")

    st.info(
        "다음 사항을 확인해 주세요.\n\n"
        "- 인터넷 연결이 되어 있는지 확인하세요.\n"
        "- GitHub의 CSV 주소가 정상적으로 열리는지 확인하세요.\n"
        "- CSV의 열 이름과 데이터 형식이 변경되지 않았는지 확인하세요."
    )

    st.stop()


# ============================================================
# 제목
# ============================================================

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

st.markdown(
    "지난 1년간의 일별 박스오피스 데이터를 "
    "시간의 흐름에 따라 살펴봅니다."
)


# ============================================================
# 데이터 기본 정보
# ============================================================

with st.expander("데이터 정보", expanded=False):
    min_date = df["날짜"].min()
    max_date = df["날짜"].max()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "데이터 행 수",
            f"{len(df):,}",
        )

    with col2:
        st.metric(
            "시작 날짜",
            min_date.strftime("%Y-%m-%d"),
        )

    with col3:
        st.metric(
            "마지막 날짜",
            max_date.strftime("%Y-%m-%d"),
        )


# ============================================================
# 그래프 구역 1
# ============================================================

st.divider()

st.header("1. 영화의 시간에 따른 일관객 변화")


# ------------------------------------------------------------
# 영화 선택
# ------------------------------------------------------------

movie_names = sorted(
    df["영화명"].dropna().unique().tolist()
)

if not movie_names:
    st.warning("선택할 영화 데이터가 없습니다.")
    st.stop()


selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_names,
)


# ------------------------------------------------------------
# 선택한 영화의 데이터
# ------------------------------------------------------------

movie_df = df[
    df["영화명"] == selected_movie
].copy()

movie_df = movie_df.sort_values("날짜")


# ------------------------------------------------------------
# Plotly 선 그래프
# ------------------------------------------------------------

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie} — 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객수",
    },
)

fig.update_traces(
    hovertemplate=(
        "<b>%{x|%Y-%m-%d}</b><br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig.update_layout(
    hovermode="x unified",
    height=500,
    margin={
        "l": 20,
        "r": 20,
        "t": 60,
        "b": 20,
    },
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


show_graph_explanation(
    "선의 높이와 움직임을 보면 선택한 영화의 일관객이 "
    "시간에 따라 어떻게 변했는지 알 수 있습니다."
)


# ============================================================
# 그래프 구역 2
# ============================================================

st.divider()

st.header("2. 일관객 합계가 가장 큰 영화 5편")


# ------------------------------------------------------------
# 기간 전체의 일관객 합계 계산
# ------------------------------------------------------------

movie_totals = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values(
        "일관객",
        ascending=False,
    )
)

top5_movies = movie_totals.head(5)["영화명"].tolist()


# ------------------------------------------------------------
# 상위 5편의 날짜별 데이터
# ------------------------------------------------------------

top5_df = df[
    df["영화명"].isin(top5_movies)
].copy()

top5_df = top5_df.sort_values(
    ["날짜", "영화명"]
)


# ------------------------------------------------------------
# Plotly 다중 선 그래프
# ------------------------------------------------------------

fig_top5 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="기간 전체 일관객 합계 상위 5편",
    labels={
        "날짜": "날짜",
        "일관객": "일관객수",
        "영화명": "영화",
    },
)

fig_top5.update_traces(
    hovertemplate=(
        "<b>%{x|%Y-%m-%d}</b><br>"
        "영화: %{fullData.name}<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig_top5.update_layout(
    hovermode="x unified",
    height=600,
    margin={
        "l": 20,
        "r": 20,
        "t": 60,
        "b": 20,
    },
    legend={
        "title": "영화",
    },
)

st.plotly_chart(
    fig_top5,
    use_container_width=True,
)


show_graph_explanation(
    "기간 전체의 일관객 합계가 큰 영화들이 언제 많은 관객을 모았고 "
    "시간에 따라 관객 규모가 어떻게 변했는지 비교할 수 있습니다."
)


# ============================================================
# 그래프 구역 3
# ============================================================

st.divider()

st.header("3. 다음 그래프")

st.info(
    "앞으로 새로운 그래프를 추가할 영역입니다."
)


# ============================================================
# 그래프 구역 4
# ============================================================

st.divider()

st.header("4. 기간 전체 일관객 TOP 10")


# ------------------------------------------------------------
# 영화별 일관객 합계와 10위권 등장 일수 계산
# ------------------------------------------------------------

top10_stats = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        **{"10위권 등장 일수": ("날짜", "nunique")},
    )
    .reset_index()
)


# 일관객 합계가 많은 순서로 정렬하고 TOP 10을 선택합니다.
top10_stats = (
    top10_stats
    .sort_values(
        "일관객합계",
        ascending=False,
    )
    .head(10)
    .copy()
)


# ------------------------------------------------------------
# 가로 막대그래프
# ------------------------------------------------------------

# Plotly의 가로 막대그래프는 y축을 영화명으로 두고
# x축을 관객수로 지정하면 만들 수 있습니다.
fig_top10 = px.bar(
    top10_stats,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="기간 전체 일관객 합계 TOP 10",
    labels={
        "일관객합계": "일관객 합계",
        "영화명": "영화",
    },
    text="일관객합계",
)


# 관객수가 많은 영화가 위에 오도록
# y축의 순서를 뒤집습니다.
fig_top10.update_layout(
    yaxis={
        "categoryorder": "total ascending",
    },
    height=600,
    margin={
        "l": 20,
        "r": 20,
        "t": 60,
        "b": 20,
    },
)


# 막대 위에 마우스를 올렸을 때
# 관객수와 10위권 등장 일수를 함께 보여줍니다.
fig_top10.update_traces(
    texttemplate="%{x:,}명",
    textposition="outside",
    hovertemplate=(
        "<b>%{y}</b><br>"
        "기간 일관객 합계: %{x:,}명<br>"
        "10위권 등장 일수: "
        "%{customdata}일"
        "<extra></extra>"
    ),
    customdata=top10_stats["10위권 등장 일수"],
)


st.plotly_chart(
    fig_top10,
    use_container_width=True,
)


show_graph_explanation(
    "이 기간 동안 어떤 영화가 가장 많은 일관객을 모았는지와 "
    "그 영화가 박스오피스 10위권에 며칠 동안 등장했는지를 함께 비교할 수 있습니다."
)


# ============================================================
# 데이터 출처
# ============================================================

st.divider()

st.caption(
    "데이터 출처: "
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)
