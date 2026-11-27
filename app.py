"""
외국인은 돌아왔는데, 면세점은 왜 텅 비었을까?
- 대상: 한국관광공사 쇼핑관광 마케터
- 데이터: 법무부 출입국(관광지식정보시스템), 한국면세점협회, 국가데이터처 온라인쇼핑동향, 한국관광데이터랩
"""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="면세점은 왜 텅 비었을까", page_icon="🛍️", layout="wide")
DATA = Path(__file__).parent / "data"

# ---------------------------------------------------------------- 색상 (의미별로 고정)
INK, MUTED, GRID = "#1F2933", "#6B7280", "#E5E7EB"
OLD = "#9CA3AF"      # 면세점 = 줄어드는 쪽 (회색)
DOWN = "#D9480F"     # 감소 강조
NEW = "#1C7ED6"      # 새로 커지는 쪽 (파랑)
NEW2 = "#0CA678"     # 두 번째 새 채널 (초록)
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"

st.markdown(f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
html, body, [class*="css"], .stMarkdown, .stTabs, button, input {{ font-family: {FONT}; }}
.block-container {{ padding-top: 3.4rem; max-width: 1180px; }}
h1 {{ font-size: 2.1rem !important; letter-spacing: -0.02em; }}
.kicker {{ color:{NEW}; font-weight:700; font-size:0.95rem; margin-bottom:-0.4rem; }}
.sub {{ color:{MUTED}; font-size:1.05rem; margin-top:-0.4rem; }}
.kpi {{ border:1px solid {GRID}; border-radius:14px; padding:16px 18px; background:#fff; height:100%; }}
.kpi .l {{ color:{MUTED}; font-size:0.9rem; }}
.kpi .v {{ font-size:1.9rem; font-weight:800; color:{INK}; letter-spacing:-0.02em; }}
.kpi .d {{ font-size:0.92rem; font-weight:600; }}
.q {{ font-size:1.35rem; font-weight:800; color:{INK}; margin:0.6rem 0 0.1rem; letter-spacing:-0.01em; }}
.a {{ font-size:1.02rem; color:{INK}; background:#F1F5F9; border-left:4px solid {NEW};
      padding:8px 12px; border-radius:6px; margin:0.3rem 0 0.4rem; }}
.verdict {{ display:inline-block; padding:2px 10px; border-radius:999px; font-weight:700; font-size:0.85rem; margin-right:6px; }}
.yes {{ background:#E7F5FF; color:{NEW}; }}
.no {{ background:#FFF4E6; color:{DOWN}; }}
.todo {{ border:1px dashed {NEW}; border-radius:10px; padding:10px 14px; color:{INK}; background:#F8FBFF; }}
.note {{ color:{MUTED}; font-size:0.85rem; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- 데이터
@st.cache_data
def load():
    y = pd.read_csv(DATA / "yearly.csv", index_col="연")
    card = pd.read_csv(DATA / "card_industry.csv")
    onl = pd.read_csv(DATA / "online_app.csv")
    rl = pd.read_csv(DATA / "region_link.csv")
    vrq = pd.read_csv(DATA / "visitors_region_q.csv")
    return y, card, onl, rl, vrq


y, card, onl, rl, vrq = load()


def base_layout(fig, height=420, ytitle=None, legend=True):
    fig.update_layout(
        height=height, margin=dict(l=10, r=20, t=30, b=10), plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family=FONT, size=15, color=INK), hoverlabel=dict(font_family=FONT, font_size=14),
        showlegend=legend, legend=dict(orientation="h", y=1.1, x=0, font=dict(size=14)),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(size=14))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title_text=ytitle, tickformat=",", title_font=dict(size=13, color=MUTED),
                     tickfont=dict(size=13, color=MUTED))
    return fig


def kpi(col, label, value, delta, color):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                 f'<div class="d" style="color:{color}">{delta}</div></div>', unsafe_allow_html=True)


def question(q, a):
    st.markdown(f'<div class="q">{q}</div><div class="a">{a}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- 헤더
st.markdown('<div class="kicker">한국관광공사 쇼핑관광 마케터를 위한 대시보드</div>', unsafe_allow_html=True)
st.title("외국인은 돌아왔는데, 면세점은 왜 텅 비었을까?")
st.markdown('<div class="sub">외국인 관광객 쇼핑의 돈이 어디로 옮겨갔는지 공공데이터 4종으로 추적했습니다.</div>',
            unsafe_allow_html=True)
st.write("")

# 비교 기준 (전체 탭 공통)
c1, c2 = st.columns([1.2, 3])
with c1:
    year = st.select_slider("비교할 연도 (기준: 코로나 전 2019년)", options=[2023, 2024, 2025], value=2025)
with c2:
    st.markdown(f'<div class="note" style="margin-top:1.9rem">위 카드와 ①–③탭의 숫자·차트가 <b>2019년 vs {year}년</b> 비교로 바뀝니다. '
                '2020–2022년(코로나)은 관광객이 거의 없어 비교 기준에서 뺐습니다.</div>', unsafe_allow_html=True)

b, n = y.loc[2019], y.loc[year]
k1, k2, k3, k4 = st.columns(4)
kpi(k1, f"방한 외국인 ({year})", f"{n['방한객_만명']:,.0f}만 명",
    f"2019년 대비 {n['방한객_만명']/b['방한객_만명']-1:+.0%}", NEW if n['방한객_만명'] >= b['방한객_만명'] else DOWN)
kpi(k2, f"면세점 외국인 매출 ({year})", f"{n['면세_외국인매출_조']:.1f}조 원",
    f"2019년 대비 {n['면세_외국인매출_조']/b['면세_외국인매출_조']-1:+.0%}", DOWN)
kpi(k3, "외국인 1명이 면세점에서 쓴 돈", f"{n['1인당_면세지출_만원']:.0f}만 원",
    f"2019년 {b['1인당_면세지출_만원']:.0f}만 원 → {n['1인당_면세지출_만원']/b['1인당_면세지출_만원']-1:+.0%}", DOWN)
kpi(k4, "해외 온라인 화장품 판매", f"{n['온라인_일반_화장품_조']*1e4:,.0f}억 원",
    f"2019년의 {n['온라인_일반_화장품_조']/b['온라인_일반_화장품_조']:.1f}배", NEW)
st.write("")

tab0, tab1, tab2, tab3, tab4 = st.tabs(
    ["① 무슨 일이?", "② 왜 줄었나", "③ 돈은 어디로 갔나", "④ 나라별로 보면", "데이터·처리 과정"])

# ================================================================ ① 무슨 일이?
with tab0:
    question("관광객이 늘면 면세점 매출도 늘었을까?",
             f"<b>아니요.</b> 2019년을 100으로 놓으면 {year}년 관광객은 <b>{n['방한객_만명']/b['방한객_만명']*100:.0f}</b>, "
             f"면세점 외국인 매출은 <b>{n['면세_외국인매출_조']/b['면세_외국인매출_조']*100:.0f}</b>입니다. "
             + ("관광객은 2019년보다 많은데 면세점 매출은 거의 반토막입니다." if n['방한객_만명'] >= b['방한객_만명']
                else "관광객보다 면세점 매출이 훨씬 더 많이 줄었습니다."))
    show_covid = st.toggle("코로나 기간(2020–2022)도 보기", value=False,
                           help="이 기간엔 관광객이 거의 없는데 면세점 매출은 컸습니다. ②탭에서 이유를 설명합니다.")
    yy = y.copy()
    if not show_covid:   # 코로나 기간은 점을 지워 선을 끊는다 (이어 그리면 잘못된 추세처럼 보임)
        yy.loc[yy["코로나기간"], ["방한객_만명", "면세_외국인매출_조"]] = None
    idx_v = yy["방한객_만명"] / b["방한객_만명"] * 100
    idx_d = yy["면세_외국인매출_조"] / b["면세_외국인매출_조"] * 100
    fig = go.Figure()
    fig.add_hline(y=100, line=dict(color=GRID, width=1.5, dash="dot"))
    fig.add_trace(go.Scatter(x=yy.index, y=idx_v, name="방한 외국인 수", mode="lines+markers",
                             line=dict(color=NEW, width=3.5), marker=dict(size=9),
                             customdata=yy["방한객_만명"], hovertemplate="%{x}년 관광객 %{customdata:,.0f}만 명<extra></extra>",
                             connectgaps=False))
    fig.add_trace(go.Scatter(x=yy.index, y=idx_d, name="면세점 외국인 매출", mode="lines+markers",
                             line=dict(color=OLD, width=3.5), marker=dict(size=9),
                             customdata=yy["면세_외국인매출_조"], hovertemplate="%{x}년 면세점 %{customdata:.1f}조 원<extra></extra>"))
    for s, v, c in [(idx_v, n['방한객_만명'], NEW), (idx_d, n['면세_외국인매출_조'], DOWN)]:
        fig.add_annotation(x=year, y=s.loc[year], text=f"<b>{s.loc[year]:.0f}</b>", showarrow=False,
                           xshift=24, font=dict(size=17, color=c))
    if not show_covid:
        fig.add_vrect(x0=2019.4, x1=2022.6, fillcolor="#F3F4F6", line_width=0, layer="below",
                      annotation_text="코로나 기간 제외", annotation_position="top", annotation_font_color=MUTED)
    fig.update_xaxes(dtick=1)
    st.plotly_chart(base_layout(fig, 430, "2019년 = 100"), width="stretch")
    st.markdown(f'<div class="todo">👉 <b>마케터 시사점</b> — 관광객 수 목표만으로는 쇼핑 매출을 예측할 수 없습니다. '
                f'관광객이 <b>어디서</b> 돈을 쓰는지 따로 봐야 합니다.</div>', unsafe_allow_html=True)

# ================================================================ ② 왜 줄었나
with tab1:
    r_cnt = n["1인당_구매건수"] / b["1인당_구매건수"]
    r_amt = n["1건당_구매액_만원"] / b["1건당_구매액_만원"]
    import math
    if r_amt < 1:
        share_cnt = math.log(r_cnt) / (math.log(r_cnt) + math.log(r_amt))
        why = f"감소의 약 <b>{share_cnt:.0%}</b>가 '구매 횟수' 때문입니다."
    else:
        why = "1번 살 때 금액은 오히려 늘었으니, 감소는 전부 '구매 횟수'가 줄어서입니다."
    question("외국인 1명당 면세점 지출은 왜 줄었을까? '덜 사서'일까, '안 가서'일까?",
             f"<b>주로 '안 가서'입니다.</b> 1명당 면세점 지출 = <b>방문객 1명당 구매 횟수</b> × <b>1번 살 때 금액</b>. "
             f"{year}년엔 구매 횟수가 {r_cnt-1:+.0%}, 1번 금액이 {r_amt-1:+.0%} 변했습니다. {why}")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**방문객 1명당 면세점 구매 횟수**")
        f1 = go.Figure(go.Bar(x=["2019년", f"{year}년"], y=[b["1인당_구매건수"], n["1인당_구매건수"]],
                              marker_color=[OLD, DOWN], text=[f"{b['1인당_구매건수']:.2f}회", f"{n['1인당_구매건수']:.2f}회"],
                              textposition="outside", textfont=dict(size=18), width=0.5,
                              hovertemplate="%{x}: %{y:.2f}회<extra></extra>"))
        f1.update_yaxes(range=[0, 1.45])
        st.plotly_chart(base_layout(f1, 330, "회", legend=False), width="stretch")
    with col_b:
        st.markdown("**한 번 살 때 평균 금액**")
        f2 = go.Figure(go.Bar(x=["2019년", f"{year}년"], y=[b["1건당_구매액_만원"], n["1건당_구매액_만원"]],
                              marker_color=[OLD, DOWN], text=[f"{b['1건당_구매액_만원']:.0f}만 원", f"{n['1건당_구매액_만원']:.0f}만 원"],
                              textposition="outside", textfont=dict(size=18), width=0.5,
                              hovertemplate="%{x}: %{y:.0f}만 원<extra></extra>"))
        f2.update_yaxes(range=[0, max(b["1건당_구매액_만원"], n["1건당_구매액_만원"]) * 1.3])
        st.plotly_chart(base_layout(f2, 330, "만 원", legend=False), width="stretch")

    st.markdown("---")
    c21 = y.loc[2021]
    question("그런데 예전 면세점 매출은 정말 '관광객' 쇼핑이었을까?",
             f"<b>꼭 그렇진 않습니다.</b> 2021년엔 관광객이 <b>{c21['방한객_만명']:.0f}만 명</b>뿐인데 면세점 외국인 매출은 "
             f"<b>{c21['면세_외국인매출_조']:.0f}조 원</b>, 한 번 구매에 평균 <b>{c21['1건당_구매액_만원']:,.0f}만 원</b>이었습니다. "
             "물건을 대량으로 사서 해외에 되파는 업자가 매출을 채웠다는 뜻입니다.")
    yy2 = y.loc[2015:2025]
    f3 = go.Figure(go.Bar(x=yy2.index, y=yy2["1건당_구매액_만원"],
                          marker_color=[DOWN if v in (2020, 2021, 2022) else OLD for v in yy2.index],
                          text=[f"{v:,.0f}" for v in yy2["1건당_구매액_만원"]], textposition="outside", textfont=dict(size=13),
                          hovertemplate="%{x}년 1번 구매 평균 %{y:,.0f}만 원<extra></extra>"))
    f3.update_xaxes(dtick=1)
    st.plotly_chart(base_layout(f3, 360, "한 번 살 때 평균 금액 (만 원)", legend=False), width="stretch")
    st.markdown('<div class="todo">👉 <b>마케터 시사점</b> — 면세점 할인 쿠폰을 더 뿌려도 효과가 작습니다. '
                '문제는 "덜 산다"가 아니라 "면세점에 안 온다"이기 때문입니다. 관광객이 실제로 가는 곳을 찾아야 합니다(③탭).</div>',
                unsafe_allow_html=True)

# ================================================================ ③ 돈은 어디로 갔나
with tab2:
    cp = card.pivot(index="연", columns="묶음", values="조원")
    cats = ["면세점", "로드샵·기념품", "백화점·대형쇼핑몰", "뷰티(피부·미용)", "의료(성형·피부과 등)", "음식·카페", "숙박"]
    ratio = (cp.loc[year, cats] / cp.loc[2019, cats]).sort_values()
    top = ratio.idxmax()
    question("관광객이 한국에서 카드로 쓴 돈은 어디로 옮겨갔을까?",
             f"<b>면세점은 줄고, 로드샵·뷰티·의료는 크게 늘었습니다.</b> {year}년 면세점 카드 지출은 2019년의 "
             f"<b>{ratio['면세점']:.1f}배</b>, 로드샵·기념품은 <b>{ratio['로드샵·기념품']:.1f}배</b>, "
             f"가장 많이 늘어난 곳은 <b>{top}({ratio[top]:.1f}배)</b>입니다.")
    view = st.radio("보는 방법", ["몇 배로 변했나", "금액(조 원)"], horizontal=True, key="cardview")
    if view == "몇 배로 변했나":
        f4 = go.Figure(go.Bar(y=ratio.index, x=ratio.values, orientation="h",
                              marker_color=[DOWN if v < 1 else NEW for v in ratio.values],
                              text=[f"{v:.1f}배" for v in ratio.values], textposition="outside", textfont=dict(size=16),
                              hovertemplate="%{y}: 2019년의 %{x:.2f}배<extra></extra>"))
        f4.add_vline(x=1, line=dict(color=INK, width=1.5, dash="dot"))
        f4.add_annotation(x=1, y=1.04, yref="paper", text="2019년과 같음", showarrow=False, font=dict(color=MUTED, size=12))
        f4.update_xaxes(range=[0, ratio.max() * 1.2], title_text=f"{year}년 지출 ÷ 2019년 지출")
        f4 = base_layout(f4, 420, None, legend=False)
        f4.update_yaxes(tickfont=dict(size=15, color=INK))
        st.plotly_chart(f4, width="stretch")
    else:
        order = ratio.index.tolist()
        f4 = go.Figure()
        f4.add_trace(go.Bar(y=order, x=cp.loc[2019, order], orientation="h", name="2019년", marker_color=OLD,
                            hovertemplate="%{y} 2019년 %{x:.2f}조 원<extra></extra>"))
        f4.add_trace(go.Bar(y=order, x=cp.loc[year, order], orientation="h", name=f"{year}년", marker_color=NEW,
                            text=[f"{v:.2f}조" for v in cp.loc[year, order]], textposition="outside",
                            hovertemplate="%{y} " + str(year) + "년 %{x:.2f}조 원<extra></extra>"))
        f4.update_layout(barmode="group", bargap=0.25)
        st.plotly_chart(base_layout(f4, 460, None), width="stretch")
    st.markdown('<div class="note">외국에서 발급된 카드로 결제한 금액(한국관광데이터랩). 현금·간편결제는 빠져 있습니다. '
                '로드샵·기념품 = 화장품 가게·편의점·기념품점 등 관광 쇼핑.</div>', unsafe_allow_html=True)

    st.markdown("---")
    items = {"전체 상품": "합계", "화장품": "화장품", "옷·패션": "의류및패션관련상품",
             "음반·굿즈(K-팝)": "음반·비디오·악기", "식품": "음·식료품"}
    pick = st.selectbox("상품 고르기", list(items), index=1)
    q = onl[(onl["지역"] == "합계") & (onl["상품군"] == items[pick]) & (onl["연"] >= 2017)].copy()
    q["t"] = q["연"].astype(str) + "-Q" + q["분기"].astype(str)
    qa = q.groupby(["연", "경로"])["백만원"].sum().unstack() / 1e2   # 억원
    nq = q.groupby("연")["분기"].nunique()
    qa = qa[nq == 4]
    g_on = qa.loc[year, "일반 온라인"] / qa.loc[2019, "일반 온라인"]
    df0 = qa.loc[2019, "면세점 경유"]
    g_df = qa.loc[year, "면세점 경유"] / df0 if df0 > 0 else None
    df_txt = "면세점을 거친 판매는 없고" if g_df is None else f"면세점을 거친 판매는 2019년의 {g_df:.1f}배"
    if g_on > 1 and (g_df is None or g_df < 1):
        head = f"{df_txt}, 일반 온라인몰 판매는 {g_on:.1f}배로 늘었습니다."
        tail = " 관광객이 한국에서 산 물건을 귀국 후 온라인으로 다시 사는 흐름과 맞닿아 있습니다."
    elif g_on > 1:
        head = f"{df_txt}, 일반 온라인몰 판매는 {g_on:.1f}배입니다."
        tail = " 이 상품은 두 경로 모두 늘었지만, 일반 온라인이 더 빨리 컸습니다." if g_on > g_df else " 이 상품은 두 경로 모두 늘었습니다."
    else:
        head = f"{df_txt}, 일반 온라인몰 판매도 {g_on:.1f}배로 2019년보다 적습니다."
        tail = " 모든 상품이 온라인으로 옮겨간 건 아닙니다. 화장품과 비교해 보세요."
    question(f"한국에 오지 않고도 산다? 해외로 팔린 한국 {pick} (온라인)", f"<b>{head}</b>{tail}")
    piv = q.pivot_table(index="t", columns="경로", values="백만원", aggfunc="sum").sort_index() / 1e2
    f5 = go.Figure()
    f5.add_trace(go.Scatter(x=piv.index, y=piv["면세점 경유"], name="면세점을 거쳐 해외로", mode="lines",
                            line=dict(color=OLD, width=3), hovertemplate="%{x}: %{y:,.0f}억 원<extra></extra>"))
    f5.add_trace(go.Scatter(x=piv.index, y=piv["일반 온라인"], name="일반 온라인몰에서 해외로", mode="lines",
                            line=dict(color=NEW, width=3.5), hovertemplate="%{x}: %{y:,.0f}억 원<extra></extra>"))
    f5.add_vrect(x0="2020-Q1", x1="2022-Q4", fillcolor="#F3F4F6", line_width=0, layer="below",
                 annotation_text="코로나", annotation_position="top left", annotation_font_color=MUTED)
    f5.update_xaxes(tickangle=0, nticks=10)
    st.plotly_chart(base_layout(f5, 400, "분기 판매액 (억 원)"), width="stretch")
    st.markdown('<div class="note">국가데이터처 온라인쇼핑동향조사 「해외 직접 판매」. 국내 업체가 해외 소비자에게 온라인으로 판 금액(분기). '
                '판매 경로 구분은 2017년부터 제공.</div>', unsafe_allow_html=True)
    st.markdown('<div class="todo">👉 <b>마케터 시사점</b> — 쇼핑 홍보의 중심을 면세점에서 <b>로드샵·K-뷰티 체험</b>으로 옮기고, '
                '여행 중 산 물건을 <b>귀국 후 온라인으로 다시 살 수 있게</b> 연결(영수증 QR·글로벌몰 안내)하면 여행이 끝난 뒤의 소비까지 잡을 수 있습니다.</div>',
                unsafe_allow_html=True)

# ================================================================ ④ 나라별로 보면
with tab3:
    on_col = "온라인_증가배수"
    rl2 = rl.copy()
    jp = rl2.set_index("지역").loc["일본"]
    question("한국에 많이 온 나라일수록, 귀국 후 온라인으로도 많이 샀을까?",
             f"<b>아니요, 뚜렷한 관계는 없습니다.</b> 예를 들어 일본은 관광객이 <b>{jp['방한객_증가배수']:.2f}배</b>로 조금 늘었는데 "
             f"한국 물건 온라인 구매는 <b>{jp['온라인_증가배수']:.1f}배</b>로 뛰었습니다. 온라인 구매는 방문객 수와 따로 커지고 있습니다.")
    st.markdown('<span class="verdict no">가설 기각</span><span class="note">8개 지역뿐이라 강한 결론보다는 "방향 확인" 수준으로 봐 주세요. '
                '비교: 2019년 → 2025년 (온라인 통계는 2025년이 가장 최근의 완전한 1년)</span>', unsafe_allow_html=True)
    sel = st.selectbox("강조할 지역", rl2["지역"].tolist(), index=1)
    f6 = go.Figure()
    f6.add_hline(y=1, line=dict(color=GRID, dash="dot"))
    f6.add_vline(x=1, line=dict(color=GRID, dash="dot"))
    for _, r in rl2.iterrows():
        hi = r["지역"] == sel
        f6.add_trace(go.Scatter(
            x=[r["방한객_증가배수"]], y=[r[on_col]], mode="markers+text", text=[r["지역"]],
            textposition="top center", textfont=dict(size=15 if hi else 13, color=INK if hi else MUTED),
            marker=dict(size=10 + r["온라인_2025_억원"] ** 0.5 / 3, color=NEW if hi else "#A5D8FF",
                        line=dict(color="white", width=2)),
            hovertemplate=(f"<b>{r['지역']}</b><br>방한객 {r['방한객_2019_만명']:.0f}만→{r['방한객_2025_만명']:.0f}만 명"
                           f" ({r['방한객_증가배수']:.2f}배)<br>온라인 구매 {r['온라인_2019_억원']:,.0f}억→{r['온라인_2025_억원']:,.0f}억 원"
                           f" ({r[on_col]:.1f}배)<extra></extra>"), showlegend=False))
    f6.update_xaxes(title_text="방한 관광객 증가 (2025 ÷ 2019, 배)", range=[0.7, 2.25])
    f6.update_yaxes(range=[0.8, 5.4])
    st.plotly_chart(base_layout(f6, 470, "한국 물건 온라인 구매 증가 (배)", legend=False), width="stretch")
    st.markdown('<div class="note">원 크기 = 2025년 온라인 구매액. 오른쪽일수록 관광객이 많이 늘었고, 위쪽일수록 온라인 구매가 많이 늘었습니다.</div>',
                unsafe_allow_html=True)

    r = rl2.set_index("지역").loc[sel]
    m1, m2, m3 = st.columns(3)
    kpi(m1, f"{sel} 방한객 (2019→2025)", f"{r['방한객_2025_만명']:.0f}만 명", f"{r['방한객_증가배수']-1:+.0%}",
        NEW if r['방한객_증가배수'] >= 1 else DOWN)
    kpi(m2, f"{sel} 한국 물건 온라인 구매 (2025)", f"{r['온라인_2025_억원']:,.0f}억 원", f"2019년의 {r[on_col]:.1f}배", NEW)
    kpi(m3, f"그중 화장품 (2025)", f"{r['화장품온라인_2025_억원']:,.0f}억 원",
        f"2019년의 {r['화장품온라인_2025_억원']/r['화장품온라인_2019_억원']:.1f}배", NEW)
    st.write("")
    vq = vrq[(vrq["지역"] == sel) & (vrq["연"] >= 2017)].copy()
    oq = onl[(onl["지역"] == sel) & (onl["상품군"] == "합계") & (onl["경로"] == "일반 온라인") & (onl["연"] >= 2017)]
    mq = vq.merge(oq[["연", "분기", "백만원"]], on=["연", "분기"], how="inner")
    mq["t"] = mq["연"].astype(str) + "-Q" + mq["분기"].astype(str)
    base_v = mq[mq["연"] == 2019]["방한객"].mean()
    base_o = mq[mq["연"] == 2019]["백만원"].mean()
    f7 = go.Figure()
    f7.add_hline(y=100, line=dict(color=GRID, dash="dot"))
    f7.add_trace(go.Scatter(x=mq["t"], y=mq["방한객"] / base_v * 100, name=f"{sel} 방한객", mode="lines",
                            line=dict(color=OLD, width=3), customdata=mq["방한객"] / 1e4,
                            hovertemplate="%{x}: %{customdata:,.1f}만 명<extra></extra>"))
    f7.add_trace(go.Scatter(x=mq["t"], y=mq["백만원"] / base_o * 100, name=f"{sel} 온라인 구매(일반 온라인몰)", mode="lines",
                            line=dict(color=NEW, width=3.5), customdata=mq["백만원"] / 1e2,
                            hovertemplate="%{x}: %{customdata:,.0f}억 원<extra></extra>"))
    f7.update_xaxes(nticks=10)
    st.markdown(f"**{sel}: 관광객과 온라인 구매, 같이 움직였을까?** (2019년 평균 = 100)")
    st.plotly_chart(base_layout(f7, 380, "2019년 평균 = 100"), width="stretch")
    st.markdown('<div class="todo">👉 <b>마케터 시사점</b> — 일본·미국처럼 관광객보다 온라인 구매가 훨씬 빨리 크는 나라는 '
                '"방문 유치"와 "귀국 후 재구매"를 함께 설계할 우선 시장입니다.</div>', unsafe_allow_html=True)

# ================================================================ 데이터·처리 과정
with tab4:
    st.markdown("### 누가, 왜 쓰나요?")
    st.markdown(
        "- **누가:** 한국관광공사 쇼핑관광 마케터 (외국인 쇼핑 홍보·캠페인 기획)\n"
        "- **왜:** 관광객은 역대 최대인데 면세점 매출은 반토막입니다. 홍보 예산을 어디에 써야 할지 판단하려면 "
        "'외국인 쇼핑 돈이 어디로 갔는지'를 한 화면에서 봐야 합니다.")
    st.markdown("### 가설과 결과")
    st.markdown(
        '<span class="verdict yes">맞음</span> **H1. 관광객은 늘었지만 1명당 면세점 지출은 줄었다** — 121만 원 → 50만 원(2025). 원인의 대부분은 "면세점에 안 간다".<br>'
        '<span class="verdict yes">맞음</span> **H2. 줄어든 쇼핑은 로드샵·체험·온라인으로 옮겨갔다** — 카드: 면세점 0.6배, 로드샵 2.1배, 뷰티 3.2배 / 온라인 화장품 7배.<br>'
        '<span class="verdict no">기각</span> **H3. 관광객이 많이 늘어난 나라일수록 온라인 구매도 많이 늘었다** — 관계 없음. 온라인은 방문과 따로 큰다.',
        unsafe_allow_html=True)
    st.markdown("### 데이터")
    st.dataframe(pd.DataFrame([
        ["방한 외국인 (국적별, 월)", "관광지식정보시스템 (법무부 출입국 통계)", "2015.01–2026.10", "1명당 지출 계산의 분모, 지역별 방한객"],
        ["면세점 매출·구매 횟수 (내/외국인, 연)", "한국면세점협회 산업동향", "2015–2025", "면세점 외국인 매출, 구매 횟수"],
        ["해외 직접 판매 (지역·상품·경로, 분기)", "국가데이터처 온라인쇼핑동향조사 (KOSIS)", "2014.1Q–2026.3Q", "귀국 후 온라인 구매의 대리 지표"],
        ["외국인 카드 지출 (업종별, 연)", "한국관광데이터랩 (외국 발행 카드)", "2018–2025", "관광객이 한국에서 돈을 쓴 곳"],
    ], columns=["데이터", "출처", "기간", "쓰임"]), hide_index=True, width="stretch")
    st.markdown("### 처리 과정")
    st.markdown(
        "1. **방한객 합계:** 국적별 입국 표에서 대륙 소계(아시아·미주·유럽·대양주·아프리카·교포)를 더함. 목적은 '전체'(면세점은 목적 무관하게 이용).\n"
        "2. **1명당 면세점 지출** = 면세점 외국인 매출 ÷ 방한 외국인 수. 이것을 '구매 횟수 ÷ 방한객'과 '매출 ÷ 구매 횟수' 두 요소의 곱으로 나눠 원인을 분리.\n"
        "3. **비교 기준:** 코로나 전 2019년 vs 2023–2025년. 2020–2022년은 관광객이 거의 없어 비교에서 제외(표시만 함).\n"
        "4. **온라인 판매:** 분기 값만 사용(연간 합계 행은 중복이라 제거), 4개 분기가 다 있는 해만 연간 합산. '면세점 경유'와 '일반 온라인'을 분리.\n"
        "5. **지역 맞추기:** 온라인 통계의 지역(중국·일본·미국·아세안·EU+영국·대양주·중동·중남미)에 맞게 국적을 묶음.\n"
        "6. **카드 업종 묶기:** 23개 업종을 면세점 / 로드샵·기념품 / 백화점·대형쇼핑몰 / 뷰티 / 의료 / 음식 / 숙박으로 정리.")
    st.markdown("### 한계 (솔직하게)")
    st.markdown(
        "- 면세점 '구매 인원'은 같은 사람이 여러 번 사면 여러 번 세어집니다 → **구매 횟수**로 해석했습니다.\n"
        "- 면세점 매출에는 관광객이 아닌 **되팔이 업자** 몫이 섞여 있고, 공개 자료로는 둘을 분리할 수 없습니다. 그래서 '1번 구매 평균 금액' 변화로 간접 확인했습니다.\n"
        "- 온라인 해외 판매는 **관광객만의 구매가 아닙니다.** 한국에 안 와본 사람도 포함되므로 '귀국 후 재구매'의 대리 지표로만 씁니다.\n"
        "- 카드 지출은 **외국 발행 카드** 기준이라 현금·간편결제는 빠져 있습니다.")
    st.markdown("### 확장하면")
    st.markdown(
        "- 매달 새 통계가 나오면 CSV만 바꿔 넣어 자동 갱신 → 월간 쇼핑 트렌드 모니터링 도구로 확장\n"
        "- 외래관광객조사(쇼핑 장소 응답)를 붙이면 '올리브영·다이소' 같은 구체적 매장 단위로 확장\n"
        "- 지역(서울·부산·제주) 카드 데이터를 붙이면 지자체별 쇼핑 관광 전략으로 확장")
    st.markdown('<div class="note">AI 활용: 데이터 수집 보조, 전처리·대시보드 코드 작성에 Claude(Anthropic)를 사용했습니다.</div>',
                unsafe_allow_html=True)
