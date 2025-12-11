import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import warnings

warnings.filterwarnings('ignore')

# --- 0. 데이터 로드 ---
try:
    df = pd.read_csv('Online Retail/Online_Retail.csv')
except FileNotFoundError:
    print("오류: 'Online Retail/Online_Retail.csv' 파일을 찾을 수 없습니다.")
    exit()


# --- 보고서 생성을 위한 준비 ---
report = []
IMAGE_DIR = 'Online Retail/images'
def add_image(title, filename, description):
    report.append(f"### {title}")
    report.append(f"![{title}](./images/{filename})")
    report.append(description)
    report.append("\n")

def add_table(title, df_table, description=""):
    report.append(f"### {title}")
    if description:
        report.append(description)
    report.append(df_table.to_markdown())
    report.append("\n")

# --- 1. 데이터 전처리 ---
# 결측치 제거
df.dropna(subset=['CustomerID'], inplace=True)
df['Description'].fillna('알 수 없음', inplace=True)

# 데이터 타입 변환
df['CustomerID'] = df['CustomerID'].astype(int)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# 취소 주문 제거
df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]

# 가격과 수량이 0 이하인 데이터 제거
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

# 총 가격 컬럼 생성
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']


# --- EDA 시작 ---
report.append("# Online Retail 데이터 탐색적 데이터 분석(EDA) 보고서\n")

# 1.1 데이터 기본 정보
report.append("## 1. 데이터 기본 정보\n")
report.append("### 데이터 샘플 (상위 5개)")
report.append(df.head().to_markdown())
report.append("\n### 데이터 정보")
# 데이터 정보는 to_markdown 지원 안되므로 문자열로 직접 구성
import io
buffer = io.StringIO()
df.info(buf=buffer)
report.append(f"```\n{buffer.getvalue()}\n```")
report.append("\n### 기술 통계량")
report.append(df.describe().to_markdown())
report.append("\n")


report.append("## 2. 데이터 시각화 및 분석\n")

# --- 시각화 1: 국가별 주문 수 ---
country_orders = df['Country'].value_counts().nlargest(10)
plt.figure(figsize=(12, 6))
country_orders.plot(kind='bar')
plt.title('상위 10개 국가별 주문 수')
plt.xlabel('국가')
plt.ylabel('주문 수')
plt.xticks(rotation=45)
plt.tight_layout()
img_filename = 'top10_country_orders.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('상위 10개 국가별 주문 수', img_filename, "영국(United Kingdom)이 압도적으로 많은 주문 수를 차지합니다.")
add_table('상위 10개 국가별 주문 수 표', country_orders.reset_index())

# --- 시각화 2: 월별 매출 추이 ---
monthly_sales = df.set_index('InvoiceDate').resample('M')['TotalPrice'].sum()
plt.figure(figsize=(12, 6))
monthly_sales.plot(kind='line', marker='o')
plt.title('월별 총 매출 추이')
plt.xlabel('월')
plt.ylabel('총 매출')
plt.grid(True)
plt.tight_layout()
img_filename = 'monthly_sales_trend.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('월별 총 매출 추이', img_filename, "2011년 하반기로 갈수록 매출이 증가하는 추세를 보이며, 특히 11월에 최고치를 기록합니다.")
add_table('월별 총 매출 표', monthly_sales.reset_index())


# --- 시각화 3: 시간대별 주문 수 ---
hourly_orders = df['InvoiceDate'].dt.hour.value_counts().sort_index()
plt.figure(figsize=(12, 6))
hourly_orders.plot(kind='bar')
plt.title('시간대별 주문 수')
plt.xlabel('시간')
plt.ylabel('주문 수')
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.tight_layout()
img_filename = 'hourly_orders.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('시간대별 주문 수', img_filename, "주로 점심 시간대인 12시부터 15시 사이에 주문이 가장 많습니다.")
add_table('시간대별 주문 수 표', hourly_orders.reset_index())

# --- 시각화 4: 요일별 주문 수 ---
df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
# 요일 순서 정렬
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df['DayOfWeek'] = pd.Categorical(df['DayOfWeek'], categories=days, ordered=True)
weekly_orders = df['DayOfWeek'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
weekly_orders.plot(kind='bar')
plt.title('요일별 주문 수')
plt.xlabel('요일')
plt.ylabel('주문 수')
plt.xticks(rotation=0)
plt.tight_layout()
img_filename = 'weekly_orders.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('요일별 주문 수', img_filename, "주중(월-금)에 주문이 집중되어 있으며, 토요일은 거래가 없습니다. 일요일 거래는 매우 적습니다.")
add_table('요일별 주문 수 표', weekly_orders.reset_index())

# --- 시각화 5: 상위 10개 판매 상품 ---
top_10_products = df['Description'].value_counts().nlargest(10)
plt.figure(figsize=(12, 8))
top_10_products.sort_values().plot(kind='barh')
plt.title('상위 10개 판매 상품 (수량 기준)')
plt.xlabel('판매 수량')
plt.ylabel('상품 설명')
plt.tight_layout()
img_filename = 'top_10_products_quantity.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('상위 10개 판매 상품 (수량 기준)', img_filename, "'WHITE HANGING HEART T-LIGHT HOLDER'가 가장 많이 판매된 상품입니다.")
add_table('상위 10개 판매 상품 표', top_10_products.reset_index())


# --- 시각화 6: 상위 10개 매출 상품 ---
top_10_revenue_products = df.groupby('Description')['TotalPrice'].sum().nlargest(10)
plt.figure(figsize=(12, 8))
top_10_revenue_products.sort_values().plot(kind='barh')
plt.title('상위 10개 매출 상품 (금액 기준)')
plt.xlabel('총 매출액')
plt.ylabel('상품 설명')
plt.tight_layout()
img_filename = 'top_10_products_revenue.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('상위 10개 매출 상품 (금액 기준)', img_filename, "'DOTCOM POSTAGE'와 'REGENCY CAKESTAND 3 TIER'가 매출액 기준으로 최상위 상품입니다.")
add_table('상위 10개 매출 상품 표', top_10_revenue_products.reset_index())


# --- 시각화 7: UnitPrice와 Quantity의 관계 (산점도) ---
sample_df = df.sample(n=1000, random_state=42)
plt.figure(figsize=(10, 6))
plt.scatter(sample_df['UnitPrice'], sample_df['Quantity'], alpha=0.5)
plt.title('단가(UnitPrice)와 수량(Quantity)의 관계 (샘플링)')
plt.xlabel('단가 (UnitPrice)')
plt.ylabel('수량 (Quantity)')
plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.tight_layout()
img_filename = 'unitprice_quantity_scatter.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('단가와 수량의 관계', img_filename, "단가가 낮을수록 수량이 많은 경향이 있으나, 전반적으로 약한 음의 상관관계를 보입니다. (로그 스케일 적용)")


# --- 시각화 8: 고객별 총 구매액 분포 ---
customer_spending = df.groupby('CustomerID')['TotalPrice'].sum()
plt.figure(figsize=(10, 6))
plt.hist(customer_spending, bins=50, range=(0, 5000))
plt.title('고객별 총 구매액 분포 (0~5000 파운드)')
plt.xlabel('총 구매액')
plt.ylabel('고객 수')
plt.tight_layout()
img_filename = 'customer_spending_distribution.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('고객별 총 구매액 분포', img_filename, "대부분의 고객이 소액을 지출하며, 고액을 지출하는 고객은 소수입니다. 롱테일 분포를 보입니다.")


# --- 시각화 9: 고객별 주문 빈도 분포 ---
customer_orders = df.groupby('CustomerID')['InvoiceNo'].nunique()
plt.figure(figsize=(10, 6))
plt.hist(customer_orders, bins=30, range=(0, 30))
plt.title('고객별 주문 빈도 분포 (0~30회)')
plt.xlabel('주문 빈도')
plt.ylabel('고객 수')
plt.tight_layout()
img_filename = 'customer_order_frequency.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('고객별 주문 빈도 분포', img_filename, "대부분의 고객은 1~2회 주문하며, 재구매 고객은 상대적으로 적습니다.")


# --- 시각화 10: RFM 분석을 위한 데이터 준비 및 시각화 ---
# Recency: 마지막 구매일로부터 경과 시간
# Frequency: 구매 빈도
# Monetary: 총 구매액
snapshot_date = df['InvoiceDate'].max() + pd.DateOffset(days=1)
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda date: (snapshot_date - date.max()).days,
    'InvoiceNo': 'nunique',
    'TotalPrice': 'sum'
})
rfm.rename(columns={'InvoiceDate': 'Recency', 'InvoiceNo': 'Frequency', 'TotalPrice': 'Monetary'}, inplace=True)

# RFM 점수 계산 (사분위수 기준)
r_labels = range(4, 0, -1)
f_labels = range(1, 5)
m_labels = range(1, 5)
r_quartiles = pd.qcut(rfm['Recency'], 4, labels=r_labels)
f_quartiles = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=f_labels)
m_quartiles = pd.qcut(rfm['Monetary'], 4, labels=m_labels)
rfm = rfm.assign(R=r_quartiles, F=f_quartiles, M=m_quartiles)

# RFM 세그먼트
def rfm_segment(row):
    if row['R'] == 4 and row['F'] >= 3 and row['M'] >= 3:
        return '최우수 고객'
    if row['R'] >= 3 and row['F'] >= 3 and row['M'] >= 3:
        return '충성 고객'
    if row['R'] >= 3 and row['F'] < 3:
        return '잠재적 충성 고객'
    if row['R'] < 3 and row['F'] >= 3:
        return '놓치면 안되는 고객'
    if row['R'] < 3 and row['F'] < 3 and row['M'] >= 3:
        return '고액 지출 고객'
    if row['R'] < 2:
        return '이탈 우려 고객'
    return '일반 고객'

rfm['Segment'] = rfm.apply(rfm_segment, axis=1)

# RFM 세그먼트 시각화
segment_counts = rfm['Segment'].value_counts()
plt.figure(figsize=(12, 7))
segment_counts.sort_values().plot(kind='barh')
plt.title('RFM 기반 고객 세그먼트 분포')
plt.xlabel('고객 수')
plt.tight_layout()
img_filename = 'rfm_segment_distribution.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('RFM 기반 고객 세그먼트 분포', img_filename, "고객을 RFM 기법으로 세분화하여 각 그룹의 비중을 확인했습니다. '일반 고객'과 '이탈 우려 고객'이 가장 큰 비중을 차지합니다.")
add_table('RFM 고객 세그먼트 표', segment_counts.reset_index())


# --- 시각화 11: 월별 ARPU(사용자당 평균 매출) 분석 ---
report.append("## 3. 월별 ARPU(사용자당 평균 매출) 분석\n")
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')

# 월별 매출과 고객 수 계산
monthly_revenue = df.groupby('YearMonth')['TotalPrice'].sum()
monthly_customers = df.groupby('YearMonth')['CustomerID'].nunique()

# 월별 ARPU 계산
monthly_arpu = monthly_revenue / monthly_customers

# 데이터프레임 생성
arpu_df = pd.DataFrame({
    '월': monthly_arpu.index.strftime('%Y-%m'),
    '총매출': monthly_revenue.values,
    '구매고객수': monthly_customers.values,
    'ARPU': monthly_arpu.values
})

# ARPU 선 그래프
plt.figure(figsize=(12, 6))
plt.plot(arpu_df['월'], arpu_df['ARPU'], marker='o', linestyle='-')
plt.title('월별 ARPU(사용자당 평균 매출) 추이')
plt.xlabel('월')
plt.ylabel('ARPU')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
img_filename = 'monthly_arpu_line.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('월별 ARPU 선 그래프', img_filename, "월별 사용자당 평균 매출(ARPU)은 연말에 가까워질수록 증가하는 경향을 보입니다. 이는 연말 쇼핑 시즌의 영향으로 분석됩니다.")

# ARPU 막대 그래프
plt.figure(figsize=(12, 6))
plt.bar(arpu_df['월'], arpu_df['ARPU'])
plt.title('월별 ARPU(사용자당 평균 매출)')
plt.xlabel('월')
plt.ylabel('ARPU')
plt.xticks(rotation=45)
plt.tight_layout()
img_filename = 'monthly_arpu_bar.png'
plt.savefig(f"{IMAGE_DIR}/{img_filename}")
plt.close()
add_image('월별 ARPU 막대 그래프', img_filename, "막대 그래프는 각 월의 ARPU를 직관적으로 비교할 수 있게 해줍니다.")

# ARPU 데이터 테이블
add_table('월별 ARPU 데이터', arpu_df.set_index('월'), "월별 총매출, 구매 고객 수, 그리고 계산된 ARPU 값을 표로 나타냈습니다.")


# --- 보고서 파일 생성 ---
with open('Online Retail/eda_report.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print("EDA 보고서가 'Online Retail/eda_report.md'에 성공적으로 생성되었습니다.")