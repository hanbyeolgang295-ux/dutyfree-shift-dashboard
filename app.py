"""
외국인 관광객 쇼핑, 그 돈은 어디로 갔을까?
- 대상: 한국관광공사 쇼핑관광 마케터
- 데이터: 법무부 출입국(관광지식정보시스템), 한국면세점협회, 국가데이터처 온라인쇼핑동향, 한국관광데이터랩
- 차트: 전부 Plotly (애니메이션·클릭 선택·hover 연동)
"""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="그 돈은 어디로 갔을까", page_icon="🛍️", layout="wide")
DATA = Path(__file__).parent / "data"

# ---------------------------------------------------------------- 색상 (의미 고정)
INK, MUTED, GRID = "#1F2933", "#6B7280", "#E5E7EB"
OLD = "#9CA3AF"      # 기준(2019)·면세점 = 회색
DOWN = "#E8590C"     # 줄어든 것 = 주황
NEW = "#1C7ED6"      # 늘어난 것 = 파랑
LIGHT = "#A5D8FF"
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
PCFG = {"displayModeBar": False}

st.markdown(f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
html, body, [class*="css"], .stMarkdown, .stTabs, button, input {{ font-family: {FONT}; }}
.block-container {{ padding-top: 2.6rem; max-width: 1240px; }}
h1 {{ font-size: 2.3rem !important; letter-spacing: -0.02em; padding-bottom: 0.2rem !important; }}
.kicker {{ color:{NEW}; font-weight:700; font-size:1rem; margin-bottom:-0.6rem; }}
.kpi {{ border:1px solid {GRID}; border-radius:12px; padding:10px 16px; background:#fff; }}
.kpi .l {{ color:{MUTED}; font-size:0.95rem; }}
.kpi .v {{ font-size:1.75rem; font-weight:800; color:{INK}; letter-spacing:-0.02em; line-height:1.25; }}
.kpi .d {{ font-size:1rem; font-weight:700; }}
.q {{ font-size:1.5rem; font-weight:800; color:{INK}; margin:0.4rem 0 0.2rem; letter-spacing:-0.01em; }}
.a {{ font-size:1.15rem; color:{INK}; background:#F1F5F9; border-left:5px solid {NEW};
      padding:8px 14px; border-radius:6px; margin:0.2rem 0 0.6rem; }}
.badge {{ display:inline-block; padding:3px 12px; border-radius:999px; font-weight:800; font-size:0.95rem; margin-right:8px; }}
.yes {{ background:#E7F5FF; color:{NEW}; }}
.no {{ background:#FFF4E6; color:{DOWN}; }}
.take {{ font-size:1.05rem; color:{INK}; margin-top:0.2rem; }}
[data-testid="stTab"] p, [data-testid="stTab"] [data-testid="stMarkdownContainer"] {{ font-size:1.2rem !important; font-weight:700 !important; }}
[data-testid="stWidgetLabel"] p {{ font-size:1.02rem !important; font-weight:600; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load():
    y = pd.read_csv(DATA / "yearly.csv", index_col="연")
    card = pd.read_csv(DATA / "card_industry.csv")
    onl = pd.read_csv(DATA / "online_app.csv")
    rl = pd.read_csv(DATA / "region_link.csv")
    vrq = pd.read_csv(DATA / "visitors_region_q.csv")
    return y, card, onl, rl, vrq


y, card, onl, rl, vrq = load()
B = y.loc[2019]


def style(fig, height=500, legend=True, hover="closest"):
    fig.update_layout(
        height=height, margin=dict(l=10, r=30, t=40, b=10), plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family=FONT, size=17, color=INK), hovermode=hover,
        hoverlabel=dict(font_family=FONT, font_size=16, bgcolor="white"),
        showlegend=legend, legend=dict(orientation="h", y=1.1, x=0, font=dict(size=16)),
        transition=dict(duration=500, easing="cubic-in-out"), uirevision="keep",
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(size=16, color=INK))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(size=15, color=MUTED), tickformat=",")
    return fig


def kpi(col, label, value, delta, color):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                 f'<div class="d" style="color:{color}">{delta}</div></div>', unsafe_allow_html=True)


def qa(q, a):
    st.markdown(f'<div class="q">{q}</div><div class="a">{a}</div>', unsafe_allow_html=True)


def take(text):
    st.markdown(f'<div class="take">👉 <b>마케터라면:</b> {text}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- 첫 화면
st.markdown('<div class="kicker">한국관광공사 쇼핑관광 마케터를 위한 대시보드</div>', unsafe_allow_html=True)
st.title("외국인 관광객 쇼핑, 그 돈은 어디로 갔을까?")
N = y.loc[2025]
k1, k2, k3 = st.columns(3)
kpi(k1, "방한 외국인 (2025)", f"{N['방한객_만명']:,.0f}만 명", f"2019년보다 {N['방한객_만명']/B['방한객_만명']-1:+.0%} ▲", NEW)
kpi(k2, "면세점 외국인 매출 (2025)", f"{N['면세_외국인매출_조']:.1f}조 원", f"2019년보다 {N['면세_외국인매출_조']/B['면세_외국인매출_조']-1:+.0%} ▼", DOWN)
kpi(k3, "외국인 1명이 면세점에서 쓴 돈 (2025)", f"{N['1인당_면세지출_만원']:.0f}만 원",
    f"2019년 {B['1인당_면세지출_만원']:.0f}만 원 → {N['1인당_면세지출_만원']/B['1인당_면세지출_만원']-1:+.0%} ▼", DOWN)
st.write("")

tab0, tab1, tab2, tab3, tab4 = st.tabs(
    ["① 관광객↑ 면세점↓?", "② 덜 사서? 안 가서?", "③ 돈은 어디로?", "④ 나라별로는?", "데이터·처리·결론"])

# ================================================================ ① 관광객↑ 면세점↓?
with tab0:
    c1, c2 = st.columns([3, 1])
    with c1:
        yr = st.select_slider("연도를 움직여 보세요", options=list(range(2015, 2026)), value=2025, key="yr0")
    with c2:
        st.write("")
        covid = st.toggle("코로나 기간도 보기", value=False)
    iv = y["방한객_만명"] / B["방한객_만명"] * 100
    idf = y["면세_외국인매출_조"] / B["면세_외국인매출_조"] * 100
    is_covid = yr in (2020, 2021, 2022)
    if is_covid:
        msg = (f"<b>{yr}년은 코로나 기간</b> — 관광객은 {iv[yr]:.0f}인데 면세점은 {idf[yr]:.0f}. "
               "관광객이 거의 없는데도 면세점이 컸다는 건, 매출의 상당 부분이 관광객이 아닌 '되팔이 업자' 몫이었다는 뜻입니다.")
    else:
        gap = iv[yr] - idf[yr]
        msg = (f"<b>2019년 = 100일 때, {yr}년 관광객 {iv[yr]:.0f} · 면세점 {idf[yr]:.0f}</b> — "
               + ("면세점이 관광객보다 더 빨리 컸습니다." if gap < 0 else f"관광객보다 면세점이 {gap:.0f}포인트 뒤처집니다."))
    qa("관광객이 늘면 면세점 매출도 같이 늘까?", msg)
    yy = y.copy()
    if not covid:
        yy.loc[yy["코로나기간"], ["방한객_만명", "면세_외국인매출_조"]] = None
    ivp = yy["방한객_만명"] / B["방한객_만명"] * 100
    idp = yy["면세_외국인매출_조"] / B["면세_외국인매출_조"] * 100
    fig = go.Figure()
    fig.add_hline(y=100, line=dict(color=MUTED, width=1.5, dash="dot"))
    fig.add_annotation(x=2015, y=100, text="2019년 수준", showarrow=False, yshift=12, xanchor="left",
                       font=dict(size=14, color=MUTED))
    fig.add_trace(go.Scatter(x=yy.index, y=ivp, name="방한 외국인 수", mode="lines+markers",
                             line=dict(color=NEW, width=4), marker=dict(size=10),
                             customdata=yy["방한객_만명"],
                             hovertemplate="관광객 %{y:.0f} (%{customdata:,.0f}만 명)<extra></extra>"))
    fig.add_trace(go.Scatter(x=yy.index, y=idp, name="면세점 외국인 매출", mode="lines+markers",
                             line=dict(color=OLD, width=4), marker=dict(size=10),
                             customdata=yy["면세_외국인매출_조"],
                             hovertemplate="면세점 %{y:.0f} (%{customdata:.1f}조 원)<extra></extra>"))
    if yr in ivp.dropna().index:
        fig.add_vline(x=yr, line=dict(color=INK, width=2))
        fig.add_trace(go.Scatter(x=[yr, yr], y=[iv[yr], idf[yr]], mode="markers+text",
                                 marker=dict(size=20, color=[NEW, DOWN], line=dict(color="white", width=3)),
                                 text=[f"<b>{iv[yr]:.0f}</b>", f"<b>{idf[yr]:.0f}</b>"], textposition="middle right",
                                 textfont=dict(size=22, color=[NEW, DOWN]), hoverinfo="skip", showlegend=False))
    if not covid:
        fig.add_vrect(x0=2019.5, x1=2022.5, fillcolor="#F3F4F6", line_width=0, layer="below",
                      annotation_text="코로나(제외)", annotation_position="top", annotation_font=dict(color=MUTED, size=14))
    fig.update_xaxes(dtick=1, range=[2014.6, 2025.8])
    st.plotly_chart(style(fig, 500, hover="x unified"), width="stretch", config=PCFG)
    take("관광객 수만 늘린다고 쇼핑 매출이 따라오지 않습니다. 관광객이 '어디서' 쓰는지를 따로 봐야 합니다.")

# ================================================================ ② 덜 사서? 안 가서?
with tab1:
    yr2 = st.segmented_control("비교 연도 (2019년 대비)", [2023, 2024, 2025], default=2025, key="yr2") or 2025
    n2 = y.loc[yr2]
    s0, cnt, amt = B["1인당_면세지출_만원"], n2["1인당_구매건수"] / B["1인당_구매건수"], n2["1건당_구매액_만원"] / B["1건당_구매액_만원"]
    s1 = n2["1인당_면세지출_만원"]
    # 두 요소의 기여도: '횟수 먼저'와 '금액 먼저' 두 순서의 평균 (순서에 따라 값이 달라지지 않게)
    step1 = ((s0 * cnt - s0) + (s1 - s0 * amt)) / 2      # 구매 횟수 변화(안 가서)
    total = s1 - s0
    step2 = total - step1                                 # 1번 금액 변화(덜 사서)
    if amt < 1:
        verdict = f"<b>'안 가서'가 {step1/total:.0%}</b> — 구매 횟수 {cnt-1:+.0%}, 한 번 살 때 금액 {amt-1:+.0%}"
    else:
        verdict = f"<b>전부 '안 가서'</b> — 구매 횟수는 {cnt-1:+.0%}, 한 번 살 때 금액은 오히려 {amt-1:+.0%}"
    qa(f"1명당 면세점 지출 {s0:.0f}만 원 → {n2['1인당_면세지출_만원']:.0f}만 원. 덜 사서일까, 안 가서일까?", verdict)
    st.markdown('<span class="badge yes">H1 맞음</span><span style="font-size:1.05rem">관광객 1명이 면세점에서 쓰는 돈은 줄었고, 주된 이유는 면세점에 덜 가는 것</span>',
                unsafe_allow_html=True)
    wf = go.Figure(go.Waterfall(
        x=["2019년<br>1명당 지출", "구매 횟수 변화<br>(안 가서)", "1번 금액 변화<br>(덜 사서)", f"{yr2}년<br>1명당 지출"],
        measure=["absolute", "relative", "relative", "total"], y=[s0, step1, step2, 0],
        text=[f"{s0:.0f}만", f"{step1:+.0f}만", f"{step2:+.0f}만", f"{n2['1인당_면세지출_만원']:.0f}만"],
        textposition="outside", textfont=dict(size=22),
        decreasing=dict(marker=dict(color=DOWN)), increasing=dict(marker=dict(color=NEW)),
        totals=dict(marker=dict(color=OLD)), connector=dict(line=dict(color=GRID, width=2)),
        hovertemplate="%{x}: %{text}원<extra></extra>"))
    wf.update_yaxes(range=[0, max(s0, s0 + step1 + max(step2, 0)) * 1.2])
    st.plotly_chart(style(wf, 500, legend=False), width="stretch", config=PCFG)
    take("면세점 할인 쿠폰을 더 뿌리는 건 효과가 작습니다. 문제는 '덜 산다'가 아니라 '안 간다'이기 때문입니다.")

# ================================================================ ③ 돈은 어디로?
with tab2:
    cp = card.pivot(index="연", columns="묶음", values="조원")
    cats = ["면세점", "백화점·대형쇼핑몰", "숙박", "로드샵·기념품", "음식·카페", "뷰티(피부·미용)", "의료(성형·피부과 등)"]
    ratio = cp[cats] / cp.loc[2019, cats]
    order = ratio.loc[2025].sort_values().index.tolist()
    qa("관광객이 한국에서 카드로 쓴 돈은 어디로 옮겨갔을까?",
       f"<b>면세점만 2019년의 {ratio.loc[2025,'면세점']:.1f}배로 줄고</b>, 로드샵 {ratio.loc[2025,'로드샵·기념품']:.1f}배 · "
       f"뷰티 {ratio.loc[2025,'뷰티(피부·미용)']:.1f}배 · 의료 {ratio.loc[2025,'의료(성형·피부과 등)']:.1f}배 — ▶ 재생을 눌러 2018→2025를 보세요")

    def bar_frame(yr_):
        v = ratio.loc[yr_, order]
        return go.Bar(y=order, x=v.values, orientation="h",
                      marker_color=[DOWN if (c == "면세점") else (NEW if x >= 1 else LIGHT) for c, x in zip(order, v.values)],
                      text=[f"{x:.1f}배" for x in v.values], textposition="outside", textfont=dict(size=20),
                      hovertemplate="%{y}: 2019년의 %{x:.2f}배<extra></extra>")

    yrs = [2018, 2019, 2023, 2024, 2025]   # 코로나(2020–2022)는 모든 업종이 같이 꺼져 흐름을 가려서 제외
    fa = go.Figure(data=[bar_frame(2025)],
                   frames=[go.Frame(data=[bar_frame(t)], name=str(t),
                                    layout=dict(annotations=[dict(x=0.98, y=0.06, xref="paper", yref="paper", text=f"<b>{t}</b>",
                                                                  showarrow=False, font=dict(size=56, color="#D0D7DE"))]))
                           for t in yrs])
    fa.add_vline(x=1, line=dict(color=INK, width=2, dash="dot"))
    fa.update_layout(
        annotations=[dict(x=0.98, y=0.06, xref="paper", yref="paper", text="<b>2025</b>", showarrow=False,
                          font=dict(size=56, color="#D0D7DE"))],
        updatemenus=[dict(type="buttons", x=0, y=-0.2, xanchor="left", direction="left", showactive=False,
                          buttons=[dict(label="▶ 2018→2025 재생", method="animate",
                                        args=[None, dict(frame=dict(duration=1300, redraw=True), transition=dict(duration=800),
                                                         fromcurrent=False, mode="immediate")]),
                                   dict(label="❚❚ 멈춤", method="animate",
                                        args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])],
                          font=dict(size=16))],
        sliders=[dict(active=len(yrs) - 1, x=0.3, len=0.7, y=-0.08, currentvalue=dict(visible=False),
                      font=dict(size=14),
                      steps=[dict(label=str(t), method="animate",
                                  args=[[str(t)], dict(frame=dict(duration=0, redraw=True), mode="immediate")]) for t in yrs])])
    fa.update_xaxes(range=[0, 5.2])
    fa.add_annotation(x=1, y=1.04, yref="paper", text="점선 = 2019년 수준", showarrow=False, font=dict(size=15, color=MUTED))
    fa.update_yaxes(tickfont=dict(size=17, color=INK))
    fa = style(fa, 580, legend=False)
    fa.update_layout(margin=dict(b=90))
    st.plotly_chart(fa, width="stretch", config=PCFG)
    st.caption("외국에서 발급된 카드 결제액(한국관광데이터랩). 현금·간편결제 제외. 로드샵·기념품 = 화장품 가게·편의점·기념품점 등.")

    st.divider()
    items = {"화장품": "화장품", "전체 상품": "합계", "옷·패션": "의류및패션관련상품", "K-팝 음반·굿즈": "음반·비디오·악기", "식품": "음·식료품"}
    pick = st.pills("상품을 골라 보세요", list(items), default="화장품", key="item") or "화장품"
    q = onl[(onl["지역"] == "합계") & (onl["상품군"] == items[pick])].copy()
    q["t"] = q["연"].astype(str) + " " + q["분기"].astype(str) + "분기"
    piv = q.pivot_table(index=["연", "분기", "t"], columns="경로", values="백만원", aggfunc="sum").reset_index()
    piv[["면세점 경유", "일반 온라인"]] = piv[["면세점 경유", "일반 온라인"]] / 1e2
    ya = q.groupby(["연", "경로"])["백만원"].sum().unstack()
    g_on = ya.loc[2025, "일반 온라인"] / ya.loc[2019, "일반 온라인"]
    df0 = ya.loc[2019, "면세점 경유"]
    g_df = ya.loc[2025, "면세점 경유"] / df0 if df0 > 0 else None
    dtxt = "면세점 경유 판매 없음" if g_df is None else f"면세점 경유 {g_df:.1f}배"
    qa(f"한국에 다시 오지 않고도 산다? 해외로 팔린 한국 {pick}",
       f"<b>2019→2025: 일반 온라인몰 {g_on:.1f}배</b>, {dtxt}"
       + (" — 여행이 끝난 뒤에도 한국 물건을 온라인으로 삽니다." if g_on > 1 else " — 이 상품은 온라인도 줄었습니다. 화장품과 비교해 보세요."))
    fo = go.Figure()
    fo.add_trace(go.Scatter(x=piv["t"], y=piv["면세점 경유"], name="면세점을 거쳐 해외로", mode="lines",
                            line=dict(color=OLD, width=2.5), hovertemplate="면세점 경유 %{y:,.0f}억 원<extra></extra>"))
    fo.add_trace(go.Scatter(x=piv["t"], y=piv["일반 온라인"], name="일반 온라인몰에서 해외로", mode="lines",
                            line=dict(color=NEW, width=5),
                            hovertemplate="일반 온라인 %{y:,.0f}억 원<extra></extra>"))
    last = piv.iloc[-1]
    fo.add_annotation(x=last["t"], y=last["일반 온라인"], text=f"<b>{g_on:.1f}배</b> (2019 대비)", showarrow=False, yshift=28, xanchor="right",
                      font=dict(size=22, color=NEW))
    cross = piv[(piv["연"] >= 2023) & (piv["일반 온라인"] > piv["면세점 경유"])]
    if g_df is not None and len(cross) and (piv[piv["연"] == 2019]["면세점 경유"] > piv[piv["연"] == 2019]["일반 온라인"]).all():
        ct = cross.iloc[0]
        fo.add_annotation(x=ct["t"], y=ct["일반 온라인"], text="온라인이 면세점 추월", showarrow=True, arrowhead=2, ay=-60,
                          font=dict(size=16, color=NEW), arrowcolor=NEW)
    fo.add_vrect(x0="2020 1분기", x1="2022 4분기", fillcolor="#F3F4F6", line_width=0, layer="below",
                 annotation_text="코로나", annotation_position="top left", annotation_font=dict(color=MUTED, size=14))
    fo.update_xaxes(nticks=10, tickfont=dict(size=14))
    st.plotly_chart(style(fo, 480, hover="x unified"), width="stretch", config=PCFG)
    st.caption("국가데이터처 온라인쇼핑동향조사 「해외 직접 판매」: 국내 업체가 해외 소비자에게 온라인으로 판 금액(분기).")
    st.markdown('<span class="badge yes">H2 맞음</span><span style="font-size:1.05rem">면세점에서 줄어든 쇼핑은 로드샵·뷰티·의료 체험과 귀국 후 온라인 구매로 옮겨감</span>',
                unsafe_allow_html=True)
    take("쇼핑 홍보의 중심을 면세점에서 <b>로드샵·K-뷰티 체험</b>으로 옮기고, 여행 중 산 물건을 <b>귀국 후 온라인으로 다시 살 수 있게</b> 연결하세요.")

# ================================================================ ④ 나라별로는?
with tab3:
    jp = rl.set_index("지역").loc["일본"]
    qa("한국에 많이 온 나라일수록, 귀국 후 온라인으로도 많이 살까?",
       f"<b>아니요.</b> 일본은 관광객 {jp['방한객_증가배수']:.2f}배인데 온라인 구매 {jp['온라인_증가배수']:.1f}배 — 온라인은 방문객 수와 따로 큽니다.")
    st.markdown('<span class="badge no">H3 기각</span><span style="font-size:1.2rem;font-weight:800;color:#1C7ED6">👆 원을 클릭하면 아래 숫자와 그래프가 그 지역으로 바뀝니다</span>',
                unsafe_allow_html=True)
    if "sel_region" not in st.session_state:
        st.session_state.sel_region = "일본"
    sel = st.session_state.sel_region
    fs = go.Figure()
    fs.add_hline(y=1, line=dict(color=GRID, dash="dot"))
    fs.add_vline(x=1, line=dict(color=GRID, dash="dot"))
    fs.add_trace(go.Scatter(
        x=rl["방한객_증가배수"], y=rl["온라인_증가배수"], mode="markers+text", text=rl["지역"], customdata=rl["지역"],
        textposition="top center",
        textfont=dict(size=[19 if r == sel else 15 for r in rl["지역"]], color=[INK if r == sel else MUTED for r in rl["지역"]]),
        marker=dict(size=[16 + v ** 0.5 / 2.2 for v in rl["온라인_2025_억원"]],
                    color=[NEW if r == sel else "rgba(156,163,175,0.7)" for r in rl["지역"]],
                    line=dict(color=[INK if r == sel else "white" for r in rl["지역"]], width=[3 if r == sel else 1.5 for r in rl["지역"]])),
        hovertemplate="<b>%{customdata}</b><br>관광객 %{x:.2f}배 · 온라인 구매 %{y:.1f}배<br>(클릭해서 자세히)<extra></extra>",
        selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1)),
        showlegend=False))
    fs.add_annotation(x=2.2, y=0.95, text="관광객 많이 늘어남 →", showarrow=False, xanchor="right", font=dict(size=14, color=MUTED))
    fs.add_annotation(x=0.72, y=5.3, text="↑ 온라인 구매 많이 늘어남", showarrow=False, xanchor="left", font=dict(size=14, color=MUTED))
    fs.update_xaxes(range=[0.7, 2.25], title_text="방한 관광객 증가 (2025 ÷ 2019, 배)", title_font=dict(size=16, color=INK))
    fs.update_yaxes(range=[0.8, 5.5], title_text="온라인 구매 증가 (배)", title_font=dict(size=16, color=INK))
    ev = st.plotly_chart(style(fs, 480, legend=False), width="stretch", config=PCFG,
                         on_select="rerun", selection_mode="points", key="scatter")
    pts = (ev or {}).get("selection", {}).get("points", []) if isinstance(ev, dict) else getattr(getattr(ev, "selection", None), "points", [])
    if pts:
        clicked = pts[0].get("customdata")
        if isinstance(clicked, list):
            clicked = clicked[0]
        if clicked and clicked != st.session_state.sel_region:
            st.session_state.sel_region = clicked
            st.rerun()
    st.caption("원 크기 = 2025년 온라인 구매액. 8개 지역뿐이라 '방향 확인' 수준으로 해석합니다.")

    r = rl.set_index("지역").loc[sel]
    m1, m2, m3 = st.columns(3)
    kpi(m1, f"{sel} · 방한 관광객 2025", f"{r['방한객_2025_만명']:.0f}만 명", f"2019년보다 {r['방한객_증가배수']-1:+.0%}",
        NEW if r["방한객_증가배수"] >= 1 else DOWN)
    kpi(m2, f"{sel} · 한국 물건 온라인 구매 2025", f"{r['온라인_2025_억원']:,.0f}억 원", f"2019년의 {r['온라인_증가배수']:.1f}배", NEW)
    kpi(m3, f"{sel} · 그중 화장품", f"{r['화장품온라인_2025_억원']:,.0f}억 원",
        f"2019년의 {r['화장품온라인_2025_억원']/r['화장품온라인_2019_억원']:.1f}배", NEW)

    vq = vrq[(vrq["지역"] == sel) & (vrq["연"] >= 2017)]
    oq = onl[(onl["지역"] == sel) & (onl["상품군"] == "합계") & (onl["경로"] == "일반 온라인")]
    mq = vq.merge(oq[["연", "분기", "백만원"]], on=["연", "분기"])
    mq["t"] = mq["연"].astype(str) + " " + mq["분기"].astype(str) + "분기"
    bv, bo = mq[mq["연"] == 2019]["방한객"].mean(), mq[mq["연"] == 2019]["백만원"].mean()
    ft = go.Figure()
    ft.add_hline(y=100, line=dict(color=MUTED, dash="dot"))
    ft.add_trace(go.Scatter(x=mq["t"], y=mq["방한객"] / bv * 100, name=f"{sel} 방한 관광객", mode="lines",
                            line=dict(color=OLD, width=4), customdata=mq["방한객"] / 1e4,
                            hovertemplate="관광객 %{y:.0f} (%{customdata:,.1f}만 명)<extra></extra>"))
    ft.add_trace(go.Scatter(x=mq["t"], y=mq["백만원"] / bo * 100, name=f"{sel} 한국 물건 온라인 구매", mode="lines",
                            line=dict(color=NEW, width=5), customdata=mq["백만원"] / 1e2,
                            hovertemplate="온라인 %{y:.0f} (%{customdata:,.0f}억 원)<extra></extra>"))
    ft.update_xaxes(nticks=10, tickfont=dict(size=14))
    st.markdown(f'<div class="q" style="font-size:1.3rem">{sel}: 관광객과 온라인 구매가 같이 움직였을까? (2019년 평균 = 100)</div>',
                unsafe_allow_html=True)
    st.plotly_chart(style(ft, 430, hover="x unified"), width="stretch", config=PCFG)
    take("일본·미국처럼 관광객보다 온라인 구매가 훨씬 빨리 크는 나라는 '방문 유치'와 '귀국 후 재구매'를 함께 설계할 우선 시장입니다.")

# ================================================================ 데이터·처리·결론
with tab4:
    _c = y.loc[2025, "1인당_구매건수"] / B["1인당_구매건수"]; _a = y.loc[2025, "1건당_구매액_만원"] / B["1건당_구매액_만원"]
    _s0, _s1 = B["1인당_면세지출_만원"], y.loc[2025, "1인당_면세지출_만원"]
    _st1 = ((_s0 * _c - _s0) + (_s1 - _s0 * _a)) / 2
    st.markdown("### 결론: 가설 검증 결과")
    st.markdown(
        f'<span class="badge yes">H1 맞음</span> 관광객은 늘었지만 1명당 면세점 지출은 121만 → 50만 원. 줄어든 {_s0-_s1:.0f}만 원 중 {-_st1:.0f}만 원({_st1/(_s1-_s0):.0%})이 "면세점에 안 가서".<br><br>'
        '<span class="badge yes">H2 맞음</span> 카드 지출: 면세점 0.6배 ↔ 로드샵 2.1배 · 뷰티 3.2배 · 의료 4.4배 / 해외 온라인 화장품 7.1배.<br><br>'
        '<span class="badge no">H3 기각</span> 많이 온 나라일수록 온라인으로 더 산다? 관계 없음 → 온라인은 방문과 따로 큰다.',
        unsafe_allow_html=True)
    st.markdown("### 그래서 관광공사 쇼핑 마케터는")
    st.markdown("1. 면세점 할인 대신 **로드샵·K-뷰티·의료 체험 동선**을 홍보\n"
                "2. 여행 중 산 물건을 **귀국 후 온라인으로 다시 사게** 연결 (영수증 QR, 글로벌몰 안내)\n"
                "3. **일본·미국**은 방문 유치와 온라인 재구매를 함께 노리는 우선 시장")
    st.markdown("### 누가, 왜")
    st.markdown("- **누가:** 한국관광공사 쇼핑관광 마케터 (외국인 쇼핑 홍보·캠페인 기획)\n"
                "- **왜:** 관광객은 역대 최대인데 면세점은 반토막 — 홍보 예산을 어디에 쓸지 판단하려면 '쇼핑 돈의 이동'을 한 화면에서 봐야 함")
    st.markdown("### 데이터")
    st.dataframe(pd.DataFrame([
        ["방한 외국인 (국적별, 월)", "관광지식정보시스템 (법무부 출입국 통계)", "2015.01–2026.10"],
        ["면세점 매출·구매 횟수 (내/외국인, 연)", "한국면세점협회 산업동향", "2015–2025"],
        ["해외 직접 판매 (지역·상품·경로, 분기)", "국가데이터처 온라인쇼핑동향조사 (KOSIS)", "2017.1Q–2026.3Q"],
        ["외국인 카드 지출 (업종별, 연)", "한국관광데이터랩 (외국 발행 카드)", "2018–2025"],
    ], columns=["데이터", "출처", "기간"]), hide_index=True, width="stretch")
    st.markdown("### 처리 과정")
    st.markdown(
        "1. **방한객 합계:** 국적별 입국 표의 대륙 소계를 더함 (목적은 '전체' — 면세점은 목적과 무관하게 이용)\n"
        "2. **1명당 면세점 지출** = 면세점 외국인 매출 ÷ 방한객 → '1명당 구매 횟수' × '1번 구매 금액'으로 나눔. 두 요소를 바꾸는 순서(횟수 먼저 / 금액 먼저)에 따라 기여도가 달라지지 않도록 두 순서의 평균으로 계산\n"
        "3. **비교 기준:** 코로나 전 2019년 vs 최근. 2020–2022년은 관광객이 거의 없어 비교에서 제외\n"
        "4. **온라인 판매:** 분기 값만 사용(연간 합계 행 중복 제거), '면세점 경유'와 '일반 온라인' 분리\n"
        "5. **지역 맞추기:** 온라인 통계 지역(중국·일본·미국·아세안·EU+영국·대양주·중동·중남미)에 맞게 국적을 묶음\n"
        "6. **카드 업종 묶기:** 23개 업종 → 면세점 / 로드샵·기념품 / 백화점·대형쇼핑몰 / 뷰티 / 의료 / 음식 / 숙박")
    with st.expander("한계 (질문 대비)"):
        st.markdown(
            "- 면세점 '구매 인원'은 같은 사람이 여러 번 사면 여러 번 셈 → **구매 횟수**로 해석\n"
            "- 면세점 매출에는 **되팔이 업자** 몫이 섞여 있음. 2021년엔 관광객 93만 명인데 매출 17조, 1번 구매 평균 2,555만 원\n"
            "- 해외 온라인 판매는 관광객만의 구매가 아님 → '귀국 후 재구매'의 **대리 지표**로만 사용\n"
            "- 카드 지출은 **외국 발행 카드** 기준 (현금·간편결제 제외)")
        yy2 = y.loc[2015:2025]
        f3 = go.Figure(go.Bar(x=yy2.index, y=yy2["1건당_구매액_만원"],
                              marker_color=[DOWN if v in (2020, 2021, 2022) else OLD for v in yy2.index],
                              text=[f"{v:,.0f}" for v in yy2["1건당_구매액_만원"]], textposition="outside",
                              hovertemplate="%{x}년 1번 구매 평균 %{y:,.0f}만 원<extra></extra>"))
        f3.update_xaxes(dtick=1)
        f3.update_yaxes(title_text="1번 구매 평균 금액(만 원)", title_font=dict(size=14, color=MUTED))
        st.plotly_chart(style(f3, 380, legend=False), width="stretch", config=PCFG)
    st.markdown("### 확장하면")
    st.markdown("- 매달 새 통계를 넣으면 자동 갱신 → 월간 외국인 쇼핑 모니터링 도구\n"
                "- 외래관광객조사(쇼핑 장소 응답)를 붙이면 매장 유형 단위로 확장\n"
                "- 지역(서울·부산·제주) 카드 데이터를 붙이면 지자체별 쇼핑 관광 전략으로 확장")
    st.caption("AI 활용: 데이터 수집 보조, 전처리·대시보드 코드 작성에 Claude(Anthropic)를 사용했습니다.")
