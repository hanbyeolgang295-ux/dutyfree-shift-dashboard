"""
산업데이터시각화 개인 프로젝트 - 전처리
질문: 외국인 관광객은 역대 최대인데, 면세점은 왜 텅 비었나? 그 돈은 어디로 갔나?

입력 (raw/)
  1. raw_목적별_국적별_입국_201501_202610.xls        관광지식정보시스템(법무부 출입국 통계), 월별 국적별 입국자
  2. raw_면세점협회_연도별_2009_2025.csv             한국면세점협회 산업동향, 연도별 내/외국인 매출·구매건수
  3. raw_면세점협회_월별_202510_202610.csv           한국면세점협회 산업동향, 최근 13개월
  4. raw_KOSIS_해외직접판매_지역상품군_2014Q1_2026Q3.csv  국가데이터처 온라인쇼핑동향조사(해외 직접 판매), 분기
  5. raw_데이터랩_외국인카드_업종별_연간_2018_2025.csv  한국관광데이터랩 외국인 카드 관광지출액(업종별, 연간)

출력 (../data/)
  yearly.csv           연도별 핵심 지표 (방한객, 면세점, 온라인 판매, 카드 소비)
  dutyfree_monthly.csv 면세점 최근 13개월
  online_quarterly.csv 온라인 해외판매 분기 x 지역 x 상품군 x 판매경로
  card_industry.csv    외국인 카드 소비 업종별 연간
  region_link.csv      지역별 방한객 증가율 vs 귀국 후 온라인 구매 증가율 (2019 -> 2025)
  visitors_region_q.csv 지역별 분기 방한객 (온라인 판매 지역 구분에 맞춤)
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
RAW = BASE / "raw"
OUT = BASE.parent / "data"
OUT.mkdir(exist_ok=True)

# ------------------------------------------------------------------
# 1. 방한 외국인 (월별, 국적별)
#    - '소계'(모든 입국 목적 합계)를 사용: 면세점은 목적과 상관없이 모든 외국인이 이용하므로
#    - 대륙 소계 행(아시아주·미주·구주·대양주·아프리카주·교포)을 더해 전체 외국인 수를 만든다
#      ('기타'는 교포와 같은 값이 중복 표기돼 제외)
# ------------------------------------------------------------------
e = pd.read_excel(RAW / "raw_목적별_국적별_입국_201501_202610.xls", header=None)
e.columns = ["국적", "목적"] + list(e.iloc[0, 2:])
e = e.iloc[2:]
e["국적"] = e["국적"].ffill().astype(str).str.replace(" ", "")
e["목적"] = e["목적"].astype(str).str.replace(" ", "")
e = e[[c for c in e.columns if c in ("국적", "목적") or str(c).endswith("월")]]   # 맨 끝 '계' 열 제거
ent = e[e["목적"] == "소계"].drop(columns="목적").melt(id_vars="국적", var_name="월", value_name="입국자")
ent["입국자"] = pd.to_numeric(ent["입국자"], errors="coerce").fillna(0)
ent["날짜"] = pd.to_datetime(ent["월"].str.replace("년", "-").str.replace("월", ""), format="%Y-%m")
ent["연"] = ent["날짜"].dt.year
ent["분기"] = ent["날짜"].dt.quarter

CONT = ["아시아주", "미주", "구주", "대양주", "아프리카주", "교포"]
visitors_y = ent[ent["국적"].isin(CONT)].groupby("연")["입국자"].sum()

# 온라인 판매 통계의 지역 구분에 맞춰 국적을 묶는다
ASEAN = ["베트남", "필리핀", "태국", "말레이시아", "싱가포르", "인도네시아", "미얀마"]
EU = ["폴란드", "덴마크", "그리스", "스페인", "루마니아", "벨기에", "독일", "프랑스",
      "네덜란드", "이탈리아", "불가리아", "스웨덴"]
piv = ent.pivot_table(index=["연", "분기"], columns="국적", values="입국자", aggfunc="sum").fillna(0)
reg = pd.DataFrame(index=piv.index)
reg["중국"] = piv["중국"]
reg["일본"] = piv["일본"]
reg["미국"] = piv["미국"]
reg["아세안"] = piv[ASEAN].sum(axis=1)
reg["유럽연합+영국"] = piv[EU + ["영국"]].sum(axis=1)
reg["대양주"] = piv["대양주"]
reg["중동"] = piv["중동"]
reg["중남미"] = piv["미주"] - piv["미국"] - piv["캐나다"]
visitors_rq = reg.reset_index().melt(id_vars=["연", "분기"], var_name="지역", value_name="방한객")
visitors_rq.to_csv(OUT / "visitors_region_q.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------------
# 2. 면세점 (한국면세점협회)
#    구매건수: 협회 주석대로 '중복 구매자 포함' -> 사람 수가 아니라 영수증(구매) 건수로 해석
# ------------------------------------------------------------------
dfy = pd.read_csv(RAW / "raw_면세점협회_연도별_2009_2025.csv").set_index("연도").sort_index()
dfm = pd.read_csv(RAW / "raw_면세점협회_월별_202510_202610.csv").sort_values("기준년월")
dfm["외국인_1건당_만원"] = dfm["외국인_매출액"] / dfm["외국인_구매인원"] / 1e4
dfm["외국인_매출_억원"] = dfm["외국인_매출액"] / 1e8
dfm.to_csv(OUT / "dutyfree_monthly.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------------
# 3. 온라인 해외 직접 판매 (KOSIS) - 분기 값만 사용 (연간 합계 행은 중복이라 제거)
#    판매경로: '면세점'(면세점 온라인몰 등) / '면세점 이외'(일반 온라인몰) 구분은 2017년부터 제공
# ------------------------------------------------------------------
k = pd.read_csv(RAW / "raw_KOSIS_해외직접판매_지역상품군_2014Q1_2026Q3.csv", encoding="cp949").iloc[:, :5]
k.columns = ["지역", "상품군", "경로", "시점", "백만원"]
k = k[k["시점"].str.contains("/")].copy()
k["백만원"] = pd.to_numeric(k["백만원"], errors="coerce")
k["연"] = k["시점"].str[:4].astype(int)
k["분기"] = k["시점"].str.extract(r"\.(\d)/")[0].astype(int)
k["상품군"] = k["상품군"].str.replace(" ", "")
k["경로"] = k["경로"].replace({"계": "전체", "면세점": "면세점 경유", "면세점 이외": "일반 온라인"})
k = k.dropna(subset=["백만원"])
k[["연", "분기", "지역", "상품군", "경로", "백만원"]].to_csv(OUT / "online_quarterly.csv", index=False, encoding="utf-8-sig")
# 대시보드용 축약본: 2017년 이후(경로 구분 시작), 대시보드에서 고를 수 있는 상품군·지역만
APP_ITEMS = ["합계", "화장품", "의류및패션관련상품", "음반·비디오·악기", "음·식료품"]
APP_REGIONS = ["합계", "중국", "일본", "미국", "아세안", "유럽연합+영국", "대양주", "중동", "중남미"]
ka = k[(k["연"] >= 2017) & (k["경로"] != "전체")
       & (((k["지역"] == "합계") & k["상품군"].isin(APP_ITEMS)) | (k["지역"].isin(APP_REGIONS) & (k["상품군"] == "합계")))]
ka[["연", "분기", "지역", "상품군", "경로", "백만원"]].to_csv(OUT / "online_app.csv", index=False, encoding="utf-8-sig")

full_years = k.groupby("연")["분기"].nunique()
full_years = full_years[full_years == 4].index          # 4개 분기가 다 있는 해만 연간 합계
ky = k[k["연"].isin(full_years)].groupby(["연", "지역", "상품군", "경로"])["백만원"].sum()

def online(region, item, route):
    return ky.xs((region, item, route), level=["지역", "상품군", "경로"]) / 1e6   # 조원

# ------------------------------------------------------------------
# 4. 외국인 카드 소비 (한국관광데이터랩, 외국 발행 카드 기준, 천원)
#    업종 묶음: 쇼핑을 '면세점' vs '그 밖의 쇼핑(로드샵·대형쇼핑몰)'으로 나누고, 체험형(뷰티·의료)을 따로 본다
# ------------------------------------------------------------------
c = pd.read_csv(RAW / "raw_데이터랩_외국인카드_업종별_연간_2018_2025.csv")
c.columns = ["연", "지역", "업종", "천원"]
c["조원"] = c["천원"] / 1e9
GROUP = {"면세점": "면세점", "기타관광쇼핑": "로드샵·기념품", "대형쇼핑몰": "백화점·대형쇼핑몰",
         "뷰티": "뷰티(피부·미용)", "의료관광": "의료(성형·피부과 등)",
         "일반외식업": "음식·카페", "제과음료업": "음식·카페",
         "호텔": "숙박", "콘도": "숙박", "기타숙박": "숙박", "캠핑장/펜션": "숙박"}
c["묶음"] = c["업종"].map(GROUP).fillna("기타(교통·레저 등)")
c.loc[c["업종"] == "관광총소비", "묶음"] = "전체"
card = c.groupby(["연", "묶음"], as_index=False)["조원"].sum()
card.to_csv(OUT / "card_industry.csv", index=False, encoding="utf-8-sig")
cp = card.pivot(index="연", columns="묶음", values="조원")

# ------------------------------------------------------------------
# 5. 연도별 핵심 지표 표
# ------------------------------------------------------------------
y = pd.DataFrame(index=range(2015, 2026))
y.index.name = "연"
y["방한객_만명"] = visitors_y.reindex(y.index) / 1e4
y["면세_외국인매출_조"] = dfy["외국인_매출액"].reindex(y.index) / 1e12
y["면세_외국인구매건수_만건"] = dfy["외국인_구매인원"].reindex(y.index) / 1e4
y["1인당_면세지출_만원"] = dfy["외국인_매출액"].reindex(y.index) / visitors_y.reindex(y.index) / 1e4
y["1인당_구매건수"] = dfy["외국인_구매인원"].reindex(y.index) / visitors_y.reindex(y.index)
y["1건당_구매액_만원"] = dfy["외국인_매출액"].reindex(y.index) / dfy["외국인_구매인원"].reindex(y.index) / 1e4
y["온라인_면세경유_조"] = online("합계", "합계", "면세점 경유").reindex(y.index)
y["온라인_일반_조"] = online("합계", "합계", "일반 온라인").reindex(y.index)
y["온라인_일반_화장품_조"] = online("합계", "화장품", "일반 온라인").reindex(y.index)
y["온라인_면세경유_화장품_조"] = online("합계", "화장품", "면세점 경유").reindex(y.index)
for col in ["전체", "면세점", "로드샵·기념품", "백화점·대형쇼핑몰", "뷰티(피부·미용)", "의료(성형·피부과 등)"]:
    y[f"카드_{col}_조"] = cp[col].reindex(y.index)
y["코로나기간"] = y.index.isin([2020, 2021, 2022])
y.round(4).to_csv(OUT / "yearly.csv", encoding="utf-8-sig")

# ------------------------------------------------------------------
# 6. 지역별 연결: 방한객이 많이 늘어난 지역일수록 귀국 후 온라인 구매(일반 온라인)도 많이 늘었나?
#    비교: 2019년 vs 2025년 (코로나 이전 vs 최근 완전한 1년)
# ------------------------------------------------------------------
REGIONS = ["중국", "일본", "미국", "아세안", "유럽연합+영국", "대양주", "중동", "중남미"]
vy = visitors_rq.groupby(["지역", "연"])["방한객"].sum().unstack()
rows = []
for r in REGIONS:
    on = ky.xs((r, "합계", "일반 온라인"), level=["지역", "상품군", "경로"])
    cos = ky.xs((r, "화장품", "일반 온라인"), level=["지역", "상품군", "경로"])
    rows.append({"지역": r,
                 "방한객_2019_만명": vy.loc[r, 2019] / 1e4, "방한객_2025_만명": vy.loc[r, 2025] / 1e4,
                 "온라인_2019_억원": on[2019] / 100, "온라인_2025_억원": on[2025] / 100,
                 "화장품온라인_2019_억원": cos[2019] / 100, "화장품온라인_2025_억원": cos[2025] / 100})
rl = pd.DataFrame(rows)
rl["방한객_증가배수"] = rl["방한객_2025_만명"] / rl["방한객_2019_만명"]
rl["온라인_증가배수"] = rl["온라인_2025_억원"] / rl["온라인_2019_억원"]
rl.round(3).to_csv(OUT / "region_link.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    print(y.round(2).to_string())
    print(rl.round(2).to_string())
