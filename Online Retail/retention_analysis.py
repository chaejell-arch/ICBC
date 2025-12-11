import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os

# 데이터 불러오기
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'Online_Retail.csv')
df = pd.read_csv(file_path, encoding='utf-8')

# 이미지 저장 디렉토리 생성
images_dir = os.path.join(script_dir, 'images')
os.makedirs(images_dir, exist_ok=True)

# 데이터 전처리
# CustomerID가 없는 데이터 제거
df.dropna(subset=['CustomerID'], inplace=True)
# CustomerID를 int형으로 변환
df['CustomerID'] = df['CustomerID'].astype(int)
# InvoiceDate를 datetime 형식으로 변환
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# DAU, MAU 계산
df['Date'] = df['InvoiceDate'].dt.date
dau = df.groupby('Date')['CustomerID'].nunique()
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
mau = df.groupby('YearMonth')['CustomerID'].nunique()

# DAU, MAU 시각화
plt.figure(figsize=(12, 6))
mau.plot(kind='bar')
plt.title('월간 활성 사용자 수 (MAU)')
plt.xlabel('월')
plt.ylabel('사용자 수')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(images_dir, 'mau_bar_chart.png'))
# plt.show() # 로컬 실행 시 주석 해제

print("--- MAU 교차표 ---")
print(mau)
print()


# 시간-요일 교cha표
df['Hour'] = df['InvoiceDate'].dt.hour
df['Weekday'] = df['InvoiceDate'].dt.day_name()
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['Weekday'] = pd.Categorical(df['Weekday'], categories=weekday_order, ordered=True)

# 시간-요일별 구매 빈도 계산
pivot_table = df.pivot_table(index='Hour', columns='Weekday', values='InvoiceNo', aggfunc='count')

# 히트맵 시각화
plt.figure(figsize=(12, 8))
sns.heatmap(pivot_table, cmap='viridis')
plt.title('시간-요일별 구매 빈도')
plt.xlabel('요일')
plt.ylabel('시간')
plt.savefig(os.path.join(images_dir, 'hour_weekday_heatmap.png'))
# plt.show() # 로컬 실행 시 주석 해제

print("--- 시간-요일 교차표 ---")
print(pivot_table)
print()


# 월단위 구매 고객 수 리텐션
def get_cohort(df):
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')
    df['CohortMonth'] = df.groupby('CustomerID')['InvoiceMonth'].transform('min')
    return df

def get_cohort_index(df):
    year_diff = df['InvoiceMonth'].dt.year - df['CohortMonth'].dt.year
    month_diff = df['InvoiceMonth'].dt.month - df['CohortMonth'].dt.month
    return year_diff * 12 + month_diff

df = get_cohort(df)
df['CohortIndex'] = get_cohort_index(df)

cohort_data = df.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
cohort_counts = cohort_data.pivot_table(index='CohortMonth', columns='CohortIndex', values='CustomerID')

# 첫달 코호트를 Acquisition으로 설정
cohort_sizes = cohort_counts.iloc[:, 0]
retention = cohort_counts.divide(cohort_sizes, axis=0)
retention.index = retention.index.strftime('%Y-%m')
retention.rename(columns={0: 'Acquisition'}, inplace=True)


# 리텐션 히트맵 시각화
plt.figure(figsize=(12, 8))
sns.heatmap(retention, annot=True, fmt='.0%', cmap='viridis')
plt.title('월별 구매 고객 리텐션')
plt.xlabel('경과 월')
plt.ylabel('첫 구매 월')
plt.savefig(os.path.join(images_dir, 'monthly_retention_heatmap.png'))
# plt.show() # 로컬 실행 시 주석 해제


print("--- 월별 리텐션 교차표 ---")
print(retention)
print()

# 리포트 생성
report = []
report.append("# Retention Analysis 보고서\n")
report.append("분석 일자: 2025-12-11\n\n")

report.append("## 1. MAU (월간 활성 사용자 수)\n\n")
report.append("![MAU 막대 그래프](images/mau_bar_chart.png)\n\n")
report.append("### MAU 교차표\n\n")
report.append(mau.to_frame('사용자 수').to_markdown() + "\n\n")

report.append("## 2. 시간-요일별 구매 빈도\n\n")
report.append("![시간-요일 히트맵](images/hour_weekday_heatmap.png)\n\n")
report.append("### 시간-요일 교차표\n\n")
report.append(pivot_table.to_markdown() + "\n\n")

report.append("## 3. 월별 구매 고객 리텐션 (Acquisition 기반)\n\n")
report.append("![월별 리텐션 히트맵](images/monthly_retention_heatmap.png)\n\n")
report.append("### 월별 리텐션 교차표\n\n")
report.append("첫 달(Acquisition) 대비 각 월의 고객 유지율을 백분율로 표시합니다.\n\n")
report.append(retention.to_markdown() + "\n\n")

report.append("## 4. 주요 인사이트\n\n")
report.append(f"- 총 분석 기간: {df['InvoiceDate'].min().date()} ~ {df['InvoiceDate'].max().date()}\n")
report.append(f"- 총 고객 수: {df['CustomerID'].nunique():,}명\n")
report.append(f"- 최대 MAU: {mau.max():,}명 ({mau.idxmax()})\n")
report.append(f"- 최소 MAU: {mau.min():,}명 ({mau.idxmin()})\n")
report.append(f"- 첫 코호트(Acquisition) 크기: {cohort_sizes.iloc[0]:.0f}명\n\n")

# 리포트 저장
report_path = os.path.join(script_dir, 'retention_report.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(''.join(report))

print(f"\n✅ 리포트 저장 완료: {report_path}")
