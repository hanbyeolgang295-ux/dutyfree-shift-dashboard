"""
외국인 관광객 쇼핑, 그 돈은 어디로 갔을까?
- 대상: 한국관광공사 쇼핑관광 마케터
- 구성: 왼쪽 사이드바 필터 + 탭 5개 (탭마다 한 화면, 왼쪽·오른쪽 차트 2개)
- 데이터: 법무부 출입국(관광지식정보시스템), 한국면세점협회, 국가데이터처 온라인쇼핑동향(KOSIS), 한국관광데이터랩
- 차트: 전부 Plotly
"""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="그 돈은 어디로 갔을까", page_icon="🛍️", layout="wide",
                   initial_sidebar_state="expanded")
DATA = Path(__file__).parent / "data"

# 색 규칙 (모든 탭 공통): 면세점 = 주황 / 관광객 = 회색 / 새로 커진 소비(로드샵·뷰티·온라인) = 파랑
DF_C, VIS_C, NEW_C = "#E8590C", "#9CA3AF", "#1C7ED6"
INK, MUTED, GRID, PALE = "#1F2933", "#6B7280", "#E5E7EB", "#A5D8FF"
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
PCFG = {"displayModeBar": False, "scrollZoom": False, "doubleClick": "reset", "showAxisDragHandles": False}

st.markdown(f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
html, body, [class*="css"], .stMarkdown, button, input {{ font-family: {FONT}; }}
.block-container {{ padding: 3rem 1.8rem 0.5rem; max-width: 100%; }}
[data-testid="stVerticalBlock"] {{ gap: 0.6rem; }}
[data-testid="stSidebar"] {{ background:#F8FAFC; }}
[data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] li {{ font-size:0.95rem; }}
.title {{ font-size:1.75rem; font-weight:800; color:{INK}; letter-spacing:-0.02em; line-height:1.25; }}
.title small {{ font-size:0.95rem; color:{MUTED}; font-weight:600; margin-left:10px; }}
.legendbar {{ font-size:0.95rem; color:{INK}; margin-top:2px; }}
.dot {{ display:inline-block; width:12px; height:12px; border-radius:3px; margin:0 5px -1px 12px; }}
[data-testid="stTab"] p {{ font-size:1.15rem !important; font-weight:700 !important; }}
.ct {{ font-size:1.2rem; font-weight:800; color:{INK}; letter-spacing:-0.01em; }}
.chips {{ margin:6px 0 4px; line-height:2; }}
.chip {{ display:inline-block; border-radius:7px; padding:1px 9px; margin-right:6px; font-size:0.93rem; font-weight:600; }}
.c1 {{ background:#1F2933; color:#fff; }} .c2 {{ background:#EEF2F6; color:{INK}; }} .c3 {{ background:#E7F5FF; color:#0B5394; }}
.kpi {{ border:1px solid {GRID}; border-radius:12px; padding:12px 16px; background:#fff; margin-bottom:10px; }}
.kpi .l {{ color:{MUTED}; font-size:0.95rem; }}
.kpi .v {{ font-size:2rem; font-weight:800; color:{INK}; letter-spacing:-0.02em; line-height:1.2; }}
.kpi .d {{ font-size:1rem; font-weight:700; }}
.badge {{ display:inline-block; padding:1px 9px; border-radius:999px; font-weight:800; font-size:0.85rem; margin-right:5px; }}
.yes {{ background:#E7F5FF; color:{NEW_C}; }} .no {{ background:#FFF4E6; color:{DF_C}; }}
.take {{ font-size:1.02rem; color:{INK}; background:#FFF8F1; border-left:4px solid {DF_C}; padding:6px 12px; border-radius:5px; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load():
    return (pd.read_csv(DATA / "yearly.csv", index_col="연"), pd.read_csv(DATA / "card_industry.csv"),
            pd.read_csv(DATA / "online_app.csv"), pd.read_csv(DATA / "region_link.csv"))


y, card, onl, rl = load()
B = y.loc[2019]
cp = card.pivot(index="연", columns="묶음", values="조원")


def style(fig, h=470, legend=True):
    fig.update_layout(height=h, margin=dict(l=4, r=18, t=36, b=4), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family=FONT, size=15, color=INK), hoverlabel=dict(font_family=FONT, font_size=15),
                      showlegend=legend, legend=dict(orientation="h", y=1.1, x=0, font=dict(size=15)),
                      transition=dict(duration=500), uirevision="keep", dragmode=False)
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(size=14, color=INK))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(size=13, color=MUTED))
    return fig


def head(title, chart, data, msg):
    """차트 제목 + 라벨 줄(차트 종류 · 데이터 · 하고 싶은 말)"""
    st.markdown(f'<div class="ct">{title}</div><div class="chips">'
                f'<span class="chip c1">📊 {chart}</span><span class="chip c2">🗂 데이터: {data}</span><br>'
                f'<span class="chip c3">💬 {msg}</span></div>', unsafe_allow_html=True)


def kpi(label, value, delta, color):
    st.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                f'<div class="d" style="color:{color}">{delta}</div></div>', unsafe_allow_html=True)


# ================================================================ 사이드바
REGIONS = rl["지역"].tolist()
ITEMS = {"화장품": "화장품", "전체 상품": "합계", "옷·패션": "의류및패션관련상품", "K-팝 음반·굿즈": "음반·비디오·악기", "식품": "음·식료품"}
with st.sidebar:
    st.markdown("### 🔎 필터")
    year = st.segmented_control("비교 연도 (기준: 코로나 전 2019년)", [2023, 2024, 2025], default=2025) or 2025
    item = st.selectbox("③ 온라인 판매 상품", list(ITEMS), index=0)
    regions = st.multiselect("④ 비교할 나라·지역", REGIONS, default=["일본", "미국", "중국", "아세안"])
    st.divider()
    st.markdown("**누가:** 한국관광공사 쇼핑관광 마케터  \n**왜:** 관광객은 늘었는데 면세점은 반토막 → 쇼핑 홍보를 어디에?")
    st.markdown('<span class="badge yes">H1 맞음</span> 면세점에 "안 가서" 줄었다<br>'
                '<span class="badge yes">H2 맞음</span> 돈은 로드샵·뷰티·온라인으로<br>'
                '<span class="badge no">H3 기각</span> 많이 온 나라 = 온라인도 많이?', unsafe_allow_html=True)

N = y.loc[year]

# ================================================================ 헤더
st.markdown(f'<div class="title">외국인 관광객 쇼핑, 그 돈은 어디로 갔을까?<small>한국관광공사 쇼핑관광 마케터용 · 2019년 vs {year}년</small></div>'
            f'<div class="legendbar">색 규칙:<span class="dot" style="background:{DF_C}"></span>면세점'
            f'<span class="dot" style="background:{VIS_C}"></span>관광객 · 2019년 기준'
            f'<span class="dot" style="background:{NEW_C}"></span>새로 커진 소비(로드샵·뷰티·온라인)</div>',
            unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs(["① 무슨 일이?", "② 왜 줄었나 (H1)", "③ 돈은 어디로 (H2)", "④ 나라별 (H3)", "⑤ 결론·데이터"])

# ================================================================ ① 무슨 일이?
with t1:
    L, R = st.columns([2.4, 1])
    with L:
        iv = y["방한객_만명"] / B["방한객_만명"] * 100
        idf = y["면세_외국인매출_조"] / B["면세_외국인매출_조"] * 100
        head("관광객이 늘면 면세점 매출도 늘까?", "꺾은선 그래프 (2019년 = 100)", "법무부 출입국 통계 · 한국면세점협회",
             f"{year}년 관광객 {iv[year]:.0f} vs 면세점 {idf[year]:.0f} — 면세점이 관광객보다 훨씬 덜 회복했다")
        yy = y.copy()
        a = yy["방한객_만명"] / B["방한객_만명"] * 100
        d = yy["면세_외국인매출_조"] / B["면세_외국인매출_조"] * 100
        f = go.Figure()
        f.add_vrect(x0=2019.5, x1=2022.5, fillcolor="#E5E7EB", opacity=0.55, line_width=0, layer="below",
                    annotation_text="코로나 기간", annotation_position="top", annotation_font=dict(color=MUTED, size=14))
        f.add_annotation(x=2021, y=62, text="관광객은 거의 없는데<br>면세점 매출은 유지<br>(되팔이 업자 몫)", showarrow=False,
                         font=dict(size=13, color=MUTED))
        f.add_hline(y=100, line=dict(color=MUTED, width=1, dash="dot"))
        after = [t for t in a.index if t >= 2023]
        f.add_trace(go.Scatter(x=after, y=d[after], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        f.add_trace(go.Scatter(x=after, y=a[after], mode="lines", line=dict(width=0), fill="tonexty",
                               fillcolor="rgba(232,89,12,0.10)", showlegend=False, hoverinfo="skip"))
        f.add_trace(go.Scatter(x=a.index, y=a, name="방한 관광객 수", mode="lines+markers+text", line=dict(color=VIS_C, width=4),
                               marker=dict(size=[16 if t == year else 8 for t in a.index]),
                               text=[f"{v:.0f}" if t in (2015, 2019, 2021, 2023, 2024, 2025) else "" for t, v in a.items()],
                               textposition="top center", textfont=dict(size=13, color="#4B5563"),
                               customdata=yy["방한객_만명"], hovertemplate="%{x}년 관광객 %{y:.0f} (%{customdata:,.0f}만 명)<extra></extra>"))
        f.add_trace(go.Scatter(x=d.index, y=d, name="면세점 외국인 매출", mode="lines+markers+text", line=dict(color=DF_C, width=4),
                               marker=dict(size=[16 if t == year else 8 for t in d.index]),
                               text=[f"{v:.0f}" if t in (2015, 2021, 2023, 2024, 2025) else "" for t, v in d.items()],
                               textposition="bottom center", textfont=dict(size=13, color=DF_C),
                               customdata=yy["면세_외국인매출_조"], hovertemplate="%{x}년 면세점 %{y:.0f} (%{customdata:.1f}조 원)<extra></extra>"))
        f.add_annotation(x=2024, y=(a[2024] + d[2024]) / 2, text="<b>벌어진 격차</b>", showarrow=False, font=dict(size=14, color=DF_C))
        f.update_xaxes(dtick=1, range=[2014.6, 2025.6])
        f.update_yaxes(range=[0, 125], title_text="2019년 = 100 (점선)", title_font=dict(size=13, color=MUTED))
        st.plotly_chart(style(f, 520), width="stretch", config=PCFG)
    with R:
        st.markdown(f'<div class="ct">{year}년 숫자로 보면</div>', unsafe_allow_html=True)
        st.write("")
        kpi(f"방한 외국인 ({year})", f"{N['방한객_만명']:,.0f}만 명",
            f"2019년 {B['방한객_만명']:,.0f}만 명 → {N['방한객_만명']/B['방한객_만명']-1:+.0%}", INK)
        kpi(f"면세점 외국인 매출 ({year})", f"{N['면세_외국인매출_조']:.1f}조 원",
            f"2019년 {B['면세_외국인매출_조']:.1f}조 원 → {N['면세_외국인매출_조']/B['면세_외국인매출_조']-1:+.0%}", DF_C)
        kpi(f"외국인 1명이 면세점에서 쓴 돈 ({year})", f"{N['1인당_면세지출_만원']:.0f}만 원",
            f"2019년 {B['1인당_면세지출_만원']:.0f}만 원 → {N['1인당_면세지출_만원']/B['1인당_면세지출_만원']-1:+.0%}", DF_C)
        st.markdown('<div class="take">👉 관광객 수만 늘린다고 쇼핑 매출이 따라오지 않는다. <b>왜 줄었는지(②)</b>, '
                    '<b>돈이 어디로 갔는지(③)</b>를 봐야 한다.</div>', unsafe_allow_html=True)

# ================================================================ ② 왜 줄었나
with t2:
    s0, s1 = B["1인당_면세지출_만원"], N["1인당_면세지출_만원"]
    c_r = N["1인당_구매건수"] / B["1인당_구매건수"]
    a_r = N["1건당_구매액_만원"] / B["1건당_구매액_만원"]
    by_cnt = ((s0 * c_r - s0) + (s1 - s0 * a_r)) / 2          # 구매 횟수 변화 몫 (두 계산 순서의 평균)
    by_amt = (s1 - s0) - by_cnt                                # 한 번 살 때 금액 변화 몫
    L, R = st.columns(2)
    with L:
        head("면세점에 '덜 가나', '덜 사나'?", "묶은 막대 그래프 (2019 vs 선택 연도)",
             "한국면세점협회 구매 횟수·매출 ÷ 법무부 방한객 수",
             (f"구매 횟수는 {c_r-1:+.0%}, 한 번 살 때 금액은 {a_r-1:+.0%} → 횟수가 훨씬 크게 줄었다" if a_r < 1 else
              f"한 번 살 때 금액은 오히려 {a_r-1:+.0%} 늘었는데, 구매 횟수가 {c_r-1:+.0%}로 반토막"))
        cats = ["관광객 1명당<br>면세점 구매 횟수", "한 번 살 때<br>평균 금액"]
        vN = [c_r * 100, a_r * 100]
        f = go.Figure()
        f.add_trace(go.Bar(x=cats, y=[100, 100], name="2019년", marker_color=VIS_C, width=0.35,
                           text=[f"{B['1인당_구매건수']:.2f}회", f"{B['1건당_구매액_만원']:.0f}만 원"], textposition="outside",
                           textfont=dict(size=17), cliponaxis=False, hovertemplate="2019년: %{text}<extra></extra>"))
        f.add_trace(go.Bar(x=cats, y=vN, name=f"{year}년", marker_color=DF_C, width=0.35,
                           text=[f"{N['1인당_구매건수']:.2f}회 ({c_r-1:+.0%})", f"{N['1건당_구매액_만원']:.0f}만 원 ({a_r-1:+.0%})"],
                           textposition="outside", textfont=dict(size=17, color=DF_C), cliponaxis=False,
                           hovertemplate=f"{year}년: %{{text}}<extra></extra>"))
        f.update_layout(barmode="group", bargap=0.3, uniformtext=dict(minsize=15, mode="show"))
        f.update_yaxes(range=[0, max(vN + [100]) * 1.25], title_text="2019년 = 100", title_font=dict(size=13, color=MUTED))
        f.update_xaxes(tickfont=dict(size=16, color=INK))
        st.plotly_chart(style(f, 520), width="stretch", config=PCFG)
    with R:
        if by_amt <= 0:
            msg = f"줄어든 {s0-s1:.1f}만 원 중 {by_cnt/(s1-s0):.0%}는 '안 가서', {by_amt/(s1-s0):.0%}는 '덜 사서'"
        else:
            msg = (f"한 번 살 때 금액은 오히려 {by_amt:+.0f}만 원 늘었지만, 구매 횟수 감소({by_cnt:+.0f}만 원)가 "
                   f"그보다 커서 1명당 지출이 {s1-s0:+.0f}만 원 → 감소는 '안 가서' 때문")
        if by_amt <= 0:
            head(f"1명당 지출 {s0:.1f}만 → {s1:.1f}만 원, 줄어든 이유는?", "파이 차트 (줄어든 금액의 이유 비중)",
                 "왼쪽 두 요소로 1명당 지출 감소를 나눔", msg)
            tot = s0 - s1
            f = go.Figure(go.Pie(
                labels=["안 가서 (구매 횟수 감소)", "덜 사서 (한 번 살 때 금액 감소)"], values=[-by_cnt, -by_amt],
                marker=dict(colors=[DF_C, "#FFC9A3"], line=dict(color="white", width=3)), sort=False, direction="clockwise",
                hole=0, textinfo="label+percent", texttemplate="<b>%{label}</b><br>%{percent:.0%} (%{value:.1f}만 원)",
                textposition="inside", insidetextorientation="horizontal", textfont=dict(size=17),
                hovertemplate="%{label}: %{value:.0f}만 원 (%{percent:.0%})<extra></extra>"))
        else:
            head(f"1명당 지출 {s0:.0f}만 → {s1:.0f}만 원, 줄어든 이유는?", "막대 그래프 (요소별 변화 금액)",
                 "왼쪽 두 요소로 1명당 지출 변화를 나눔", msg)
            f = go.Figure(go.Bar(x=["구매 횟수 변화<br>(안 가서)", "한 번 살 때 금액 변화<br>(오히려 더 삼)"], y=[by_cnt, by_amt],
                                 marker_color=[DF_C, "#FFC9A3"], width=0.45, text=[f"{by_cnt:+.0f}만 원", f"{by_amt:+.0f}만 원"],
                                 textposition="outside", textfont=dict(size=18), cliponaxis=False))
            f.add_hline(y=0, line=dict(color=INK, width=1.5))
            f.update_xaxes(tickfont=dict(size=16, color=INK))
        st.plotly_chart(style(f, 520, legend=False), width="stretch", config=PCFG)
    st.markdown('<div class="take">👉 <span class="badge yes">H1 맞음</span> 면세점 할인 쿠폰을 더 뿌려도 효과가 작다. '
                '문제는 "덜 산다"가 아니라 "면세점에 안 온다"이다.</div>', unsafe_allow_html=True)

# ================================================================ ③ 돈은 어디로
with t3:
    L, R = st.columns([1.1, 1])
    with L:
        cats = ["면세점", "백화점·대형쇼핑몰", "숙박", "로드샵·기념품", "음식·카페", "뷰티(피부·미용)", "의료(성형·피부과 등)"]
        amt = cp[cats]                                   # 조 원
        diff = amt.loc[year] - amt.loc[2019]
        order = (amt.loc[2025] - amt.loc[2019]).sort_values().index.tolist()   # 늘어난 금액 순 (위가 가장 많이 늘어남)
        SHOP = {"로드샵·기념품", "백화점·대형쇼핑몰", "뷰티(피부·미용)", "의료(성형·피부과 등)"}
        grow = diff.drop("면세점").sort_values(ascending=False)
        head("관광객이 한국에서 카드로 쓴 돈, 어디서 얼마나 늘었나?", "가로 막대 그래프 + ▶ 연도 애니메이션 (금액, 조 원)",
             "한국관광데이터랩 외국인 카드 지출",
             (f"2019→{year}: 면세점만 {diff['면세점']:+.2f}조 줄고, " if (diff < 0).sum() == 1 else
              f"2019→{year}: 줄어든 곳 " + " · ".join(f"{k} {v:+.2f}조" for k, v in diff[diff < 0].sort_values().items()) + " / 늘어난 곳 ")
             + f"{grow.index[0]} {grow.iloc[0]:+.2f}조 · {grow.index[1]} {grow.iloc[1]:+.2f}조 · {grow.index[2]} {grow.iloc[2]:+.2f}조")

        def bars(t):
            v = amt.loc[t, order]
            dv = v - amt.loc[2019, order]
            lab = [f"{x:.2f}조" + ("" if t == 2019 else f"  ({d:+.2f}조)") for x, d in zip(v.values, dv.values)]
            return go.Bar(y=order, x=v.values, orientation="h",
                          marker_color=[DF_C if c == "면세점" else (NEW_C if c in SHOP else PALE) for c in order],
                          text=lab, textposition="outside", textfont=dict(size=15), cliponaxis=False,
                          customdata=amt.loc[2019, order].values,
                          hovertemplate="%{y}: %{x:.2f}조 원 (2019년 %{customdata:.2f}조)<extra></extra>")

        yrs = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
        COVID = {2020, 2021, 2022}
        big = lambda t: [dict(x=0.99, y=0.04, xref="paper", yref="paper", text=f"<b>{t}</b>" + ("<br><span style='font-size:20px'>코로나</span>" if t in COVID else ""), showarrow=False,
                              font=dict(size=44, color="#D0D7DE")),
                         dict(x=1, y=1.03, xref="paper", yref="paper", xanchor="right", text="괄호 = 2019년 대비 증감 · 진한 파랑 = 쇼핑·뷰티·의료 · * = 코로나",
                              showarrow=False, font=dict(size=13, color=MUTED))]
        f = go.Figure(data=[bars(year)], frames=[go.Frame(data=[bars(t)], name=str(t), layout=dict(annotations=big(t))) for t in yrs])
        f.update_layout(
            annotations=big(year),
            updatemenus=[dict(type="buttons", x=0, y=-0.2, xanchor="left", direction="left", showactive=False, font=dict(size=14),
                              buttons=[dict(label="▶ 재생", method="animate",
                                            args=[None, dict(frame=dict(duration=1200, redraw=True), transition=dict(duration=700),
                                                             fromcurrent=False)]),
                                       dict(label="❚❚", method="animate",
                                            args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])])],
            sliders=[dict(active=yrs.index(year), x=0.2, len=0.8, y=-0.13, currentvalue=dict(visible=False), font=dict(size=13),
                          steps=[dict(label=str(t) + ("*" if t in COVID else ""), method="animate",
                                      args=[[str(t)], dict(frame=dict(duration=0, redraw=True), mode="immediate")]) for t in yrs])])
        f.update_xaxes(range=[0, amt.max().max() * 1.65], title_text="외국인 카드 지출 (조 원)", title_font=dict(size=13, color=MUTED))
        f.update_yaxes(tickfont=dict(size=14, color=INK))
        f = style(f, 520, legend=False)
        f.update_layout(margin=dict(b=100))
        st.plotly_chart(f, width="stretch", config=PCFG)
    with R:
        q = onl[(onl["지역"] == "합계") & (onl["상품군"] == ITEMS[item])].copy()
        q["t"] = q["연"].astype(str) + "." + q["분기"].astype(str) + "Q"
        piv = q.pivot_table(index=["연", "분기", "t"], columns="경로", values="백만원", aggfunc="sum").reset_index()
        piv[["면세점 경유", "일반 온라인"]] = piv[["면세점 경유", "일반 온라인"]] / 1e2
        ya = q.groupby(["연", "경로"])["백만원"].sum().unstack()
        g_on = ya.loc[year, "일반 온라인"] / ya.loc[2019, "일반 온라인"]
        df0 = ya.loc[2019, "면세점 경유"]
        g_df = ya.loc[year, "면세점 경유"] / df0 if df0 > 0 else None
        dtxt = "면세점 경유는 원래 없음" if g_df is None else f"면세점 경유 {g_df:.1f}배"
        head(f"한국에 다시 안 와도 산다? 해외로 팔린 한국 {item}", "꺾은선 그래프 (분기, 억 원)",
             "국가데이터처 KOSIS 온라인 해외 직접 판매 (2026.3Q까지)",
             f"연 합계 2019→{year}: 일반 온라인몰 {g_on:.1f}배, {dtxt}" + (" → 여행 뒤에도 온라인으로 산다" if g_on > 1 else " → 이 상품은 온라인도 줄었다"))
        f = go.Figure()
        f.add_vrect(x0="2020.1Q", x1="2022.4Q", fillcolor="#E5E7EB", opacity=0.55, line_width=0, layer="below",
                    annotation_text="코로나 기간", annotation_position="top left", annotation_font=dict(color=MUTED, size=13))
        f.add_trace(go.Scatter(x=piv["t"], y=piv["면세점 경유"], name="면세점을 거쳐 해외로", mode="lines",
                               line=dict(color=DF_C, width=3), hovertemplate="면세점 경유 %{y:,.0f}억 원<extra></extra>"))
        f.add_trace(go.Scatter(x=piv["t"], y=piv["일반 온라인"], name="일반 온라인몰에서 해외로", mode="lines",
                               line=dict(color=NEW_C, width=4.5), hovertemplate="일반 온라인 %{y:,.0f}억 원<extra></extra>"))
        pt = piv[piv["t"] == f"{year}.4Q"].iloc[0]
        f.add_annotation(x=pt["t"], y=pt["일반 온라인"], text=f"<b>{g_on:.1f}배</b> ({year}년 합계 ÷ 2019년 합계)", showarrow=True,
                         arrowhead=2, arrowcolor=NEW_C, ax=-30, ay=-85, xanchor="right", font=dict(size=17, color=NEW_C))
        f.update_layout(hovermode="x unified")
        f.update_xaxes(nticks=8, tickfont=dict(size=13))
        f.update_yaxes(tickformat=",", title_text="억 원", title_font=dict(size=13, color=MUTED))
        st.plotly_chart(style(f, 520), width="stretch", config=PCFG)
        st.caption("상품은 왼쪽 사이드바에서 바꿀 수 있어요.")
    st.markdown('<div class="take">👉 <span class="badge yes">H2 맞음</span> 쇼핑 홍보의 중심을 면세점에서 <b>로드샵·K-뷰티·의료 체험</b>으로, '
                '여행 중 산 물건을 <b>귀국 후 온라인으로 다시 살 수 있게</b> 연결(영수증 QR·글로벌몰).</div>', unsafe_allow_html=True)

# ================================================================ ④ 나라별
with t4:
    df = rl.set_index("지역").copy()
    rho = df["방한객_증가배수"].rank().corr(df["온라인_증가배수"].rank())
    sel = regions or ["일본", "미국"]
    L, R = st.columns(2)
    with L:
        sd = df.loc[sel].sort_values("온라인_증가배수")
        top = sd["온라인_증가배수"].idxmax()
        head("고른 나라들: 관광객 증가 vs 온라인 구매 증가", "묶은 가로 막대 그래프 (2025 ÷ 2019, 배 · 연도 고정)",
             "법무부 출입국 · KOSIS 온라인 해외 직접 판매",
             f"{top}: 관광객 {sd.loc[top,'방한객_증가배수']:.1f}배인데 한국 물건 온라인 구매는 {sd.loc[top,'온라인_증가배수']:.1f}배")
        f = go.Figure()
        f.add_trace(go.Bar(y=sd.index, x=sd["방한객_증가배수"], name="방한 관광객 증가", orientation="h", marker_color=VIS_C,
                           text=[f"{v:.1f}배" for v in sd["방한객_증가배수"]], textposition="inside", insidetextanchor="end",
                           textfont=dict(size=15, color=INK), cliponaxis=False,
                           hovertemplate="%{y} 관광객: 2019년의 %{x:.2f}배<extra></extra>"))
        f.add_trace(go.Bar(y=sd.index, x=sd["온라인_증가배수"], name="한국 물건 온라인 구매 증가", orientation="h", marker_color=NEW_C,
                           text=[f"<b>{v:.1f}배</b>" for v in sd["온라인_증가배수"]], textposition="outside", textfont=dict(size=15), cliponaxis=False,
                           hovertemplate="%{y} 온라인: 2019년의 %{x:.1f}배<extra></extra>"))
        f.add_vline(x=1, line=dict(color=INK, width=1.5, dash="dot"), layer="below")
        f.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08)
        f.update_xaxes(range=[0, max(sd["온라인_증가배수"].max(), 2.2) * 1.35])
        f.update_yaxes(tickfont=dict(size=15, color=INK))
        st.plotly_chart(style(f, 520), width="stretch", config=PCFG)
        st.caption("나라는 왼쪽 사이드바에서 고를 수 있어요.")
    with R:
        head("8개 지역 전체: 많이 온 나라일수록 많이 샀나?", "산점도 (점 하나 = 나라·지역, 2025 ÷ 2019)",
             "법무부 출입국 · KOSIS 온라인 해외 직접 판매",
             f"관계가 있다면 점이 오른쪽 위로 줄을 서야 하는데 흩어져 있다 (순위 상관 {rho:.2f} ≈ 무관)")
        f = go.Figure()
        f.add_hline(y=1, line=dict(color=GRID, dash="dot"))
        f.add_vline(x=1, line=dict(color=GRID, dash="dot"))
        is_sel = [r in sel for r in df.index]
        f.add_trace(go.Scatter(
            x=df["방한객_증가배수"], y=df["온라인_증가배수"], mode="markers+text", text=df.index, textposition="top center",
            textfont=dict(size=[16 if s else 13 for s in is_sel], color=[INK if s else MUTED for s in is_sel]),
            marker=dict(size=[14 + v ** 0.5 / 2.5 for v in df["온라인_2025_억원"]],
                        color=[NEW_C if s else "white" for s in is_sel],
                        line=dict(color=[NEW_C if s else "#6B7280" for s in is_sel], width=2)),
            customdata=df["온라인_2025_억원"],
            hovertemplate="<b>%{text}</b><br>관광객 %{x:.2f}배 · 온라인 %{y:.1f}배<br>2025년 온라인 %{customdata:,.0f}억 원<extra></extra>",
            showlegend=False))
        f.add_annotation(x=2.2, y=0.95, text="관광객 많이 늘어남 →", showarrow=False, xanchor="right", font=dict(size=13, color=MUTED))
        f.add_annotation(x=0.72, y=5.35, text="↑ 온라인 구매 많이 늘어남", showarrow=False, xanchor="left", font=dict(size=13, color=MUTED))
        f.update_xaxes(range=[0.7, 2.25], title_text="방한 관광객 증가 (배)", title_font=dict(size=14, color=INK))
        f.update_yaxes(range=[0.8, 5.5], title_text="온라인 구매 증가 (배)", title_font=dict(size=14, color=INK))
        st.plotly_chart(style(f, 520, legend=False), width="stretch", config=PCFG)
        st.caption("원 크기 = 2025년 온라인 구매액, 파란 원 = 사이드바에서 고른 나라, 빈 원 = 나머지. 8개 지역뿐이라 '방향 확인' 수준.")
    st.markdown('<div class="take">👉 <span class="badge no">H3 기각</span> 온라인 구매는 방문객 수와 따로 큰다. '
                '<b>일본·미국</b>처럼 온라인이 훨씬 빨리 크는 나라는 "방문 유치"와 "귀국 후 재구매"를 함께 노릴 우선 시장.</div>',
                unsafe_allow_html=True)

# ================================================================ ⑤ 결론·데이터
with t5:
    L, R = st.columns(2)
    with L:
        st.markdown('<div class="ct">가설 검증 결과</div>', unsafe_allow_html=True)
        _c = y.loc[2025, "1인당_구매건수"] / B["1인당_구매건수"]
        _a = y.loc[2025, "1건당_구매액_만원"] / B["1건당_구매액_만원"]
        _s0, _s1 = B["1인당_면세지출_만원"], y.loc[2025, "1인당_면세지출_만원"]
        _st = ((_s0 * _c - _s0) + (_s1 - _s0 * _a)) / 2
        st.markdown(
            f'<span class="badge yes">H1 맞음</span> 관광객 1명당 면세점 지출 {_s0:.0f}만 → {_s1:.0f}만 원. 줄어든 몫의 {_st/(_s1-_s0):.0%}는 "안 가서"<br><br>'
            f'<span class="badge yes">H2 맞음</span> 카드 지출(2019→2025): 면세점 {cp.loc[2025,"면세점"]-cp.loc[2019,"면세점"]:+.1f}조 ↔ '
            f'의료 {cp.loc[2025,"의료(성형·피부과 등)"]-cp.loc[2019,"의료(성형·피부과 등)"]:+.1f}조 · 로드샵 {cp.loc[2025,"로드샵·기념품"]-cp.loc[2019,"로드샵·기념품"]:+.1f}조 · 뷰티 {cp.loc[2025,"뷰티(피부·미용)"]-cp.loc[2019,"뷰티(피부·미용)"]:+.1f}조 / '
            f'해외 온라인 화장품 {y.loc[2025,"온라인_일반_화장품_조"]/B["온라인_일반_화장품_조"]:.1f}배<br><br>'
            f'<span class="badge no">H3 기각</span> 많이 온 나라일수록 온라인으로 더 산다? 순위 상관 {rho:.2f} → 관계 없음',
            unsafe_allow_html=True)
        st.markdown('<div class="ct" style="margin-top:14px">그래서 쇼핑관광 마케터는</div>', unsafe_allow_html=True)
        st.markdown("1. 면세점 할인 대신 **로드샵·K-뷰티·의료 체험 동선** 홍보\n"
                    "2. 여행 중 산 물건을 **귀국 후 온라인으로 다시 사게** 연결 (영수증 QR, 글로벌몰)\n"
                    "3. **일본·미국** = 방문 유치 + 온라인 재구매를 함께 노릴 우선 시장")
        st.markdown('<div class="ct" style="margin-top:14px">확장하면</div>', unsafe_allow_html=True)
        st.markdown("- 매달 새 통계를 넣으면 갱신되는 외국인 쇼핑 모니터링 도구\n- 외래관광객조사(쇼핑 장소) · 지역별 카드 데이터로 확장")
    with R:
        st.markdown('<div class="ct">데이터 (모두 공공데이터)</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([
            ["방한 외국인 (국적별, 월)", "관광지식정보시스템 (법무부 출입국)", "①②④"],
            ["면세점 매출·구매 횟수 (내/외국인, 연)", "한국면세점협회 산업동향", "①②"],
            ["외국인 카드 지출 (업종별, 연)", "한국관광데이터랩", "③ 왼쪽"],
            ["온라인 해외 직접 판매 (지역·상품·경로, 분기)", "국가데이터처 KOSIS", "③ 오른쪽, ④"],
        ], columns=["데이터", "출처", "쓰인 곳"]), hide_index=True, width="stretch")
        st.markdown('<div class="ct" style="margin-top:8px">처리 과정</div>', unsafe_allow_html=True)
        st.markdown("1. 방한객 = 국적별 입국 표의 대륙 소계 합 (입국 목적 전체, 승무원 제외)\n"
                    "2. 1명당 면세점 지출 = 면세점 외국인 매출 ÷ 방한객 = 구매 횟수 × 1번 금액\n"
                    "3. 이유 비중 = 두 요소를 바꾸는 순서의 평균 (순서에 따라 안 바뀌게)\n"
                    "4. 기준 2019년, 코로나 2020–2022년은 비교 계산에서 제외(차트엔 회색 칸으로 표시) · 온라인은 분기 값, 면세점 경유/일반 분리\n"
                    "5. 국적을 온라인 통계 지역에 맞게 묶음 · 카드 23개 업종을 7개로 묶음")
        with st.expander("한계 (질문 대비)"):
            st.markdown("- 면세점 '구매 인원'은 중복 포함 → 구매 **횟수**로 해석\n"
                        "- 면세점 매출엔 **되팔이 업자** 몫이 섞임 (2021년: 관광객 93만 명인데 매출 17조)\n"
                        "- 온라인 해외 판매는 관광객만의 구매가 아님 → '귀국 후 재구매'의 **대리 지표**\n"
                        "- 카드는 외국 발행 카드만 (현금·간편결제 제외) · 나라 비교는 8개 지역뿐")
        st.caption("AI 활용: 데이터 수집 보조, 전처리·대시보드 코드 작성에 Claude(Anthropic)를 사용했습니다.")
