import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import matplotlib.font_manager as fm

# --- 한글 폰트 설정 (메모리 지시사항 반영) ---
# 시스템에 'Malgun Gothic' 폰트가 있는지 확인
if os.name == 'nt':  # Windows 운영체제
    font_path = "C:/Windows/Fonts/malgunbd.ttf"  # 맑은 고딕 볼드체 경로
    if Path(font_path).exists():
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지
    else:
        print("Malgun Gothic 폰트가 시스템에 없습니다. 다른 폰트를 사용하거나 설치해주세요.")
elif os.name == 'posix': # Mac, Linux 등 (예시, 실제 환경에 맞게 조정 필요)
    # Mac인 경우 AppleGothic, Linux인 경우 Nanum Gothic 등 설치 필요
    # 여기서는 예시로 남겨두고, 실제 사용 환경에 맞게 조정해야 함
    # plt.rcParams['font.family'] = 'AppleGothic'
    # plt.rcParams['axes.unicode_minus'] = False
    pass

# --- 데이터 로드 함수 ---
def load_data():
    parquet_path = Path("wafer/data/LSWMD.parquet")
    if parquet_path.exists():
        print(f"'{parquet_path}' 파일이 존재하여 로드합니다.")
        df = pd.read_parquet(parquet_path)
        return df
    else:
        print(f"오류: '{parquet_path}' 파일을 찾을 수 없습니다. 데이터 로딩 단계를 먼저 수행해주세요.")
        return None

# --- 이미지 저장 경로 설정 ---
IMAGE_DIR = Path("wafer/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True) # 폴더 없으면 생성

# --- 시각화 함수 (각 EDA 단계별로 구현 예정) ---

# 3.1. 데이터 구조 분석
def plot_data_structure(df):
    print("\n--- 3.1. 데이터 구조 분석 ---")
    print("\n### 전체 데이터 수, 클래스 수")
    print(f"전체 웨이퍼 데이터 수: {len(df)}")
    if 'failureType' in df.columns:
        print(f"불량 유형(클래스) 수: {df['failureType'].nunique()}")
        print(f"불량 유형: {df['failureType'].unique()}")
    if 'trianTestLabel' in df.columns:
        print(f"학습/테스트 라벨 수: {df['trianTestLabel'].nunique()}")
        print(f"학습/테스트 라벨: {df['trianTestLabel'].unique()}")

    print("\n### 데이터 샘플 (상위 5개)")
    cols_to_display = [col for col in df.columns if col != 'waferMap']
    print(df[cols_to_display].head().to_markdown(index=False))

    # PKL 객체 타입, key 구조 설명은 코드에서 직접 출력하거나 마크다운으로 포함해야 함.
    # 현재 DataFrame으로 로드되었으므로, PKL 자체의 구조는 이 단계에서 직접 볼 수 없음.
    # 이는 data_loader.py에서 pkl 로드 시점의 정보가 필요함.
    # 여기서는 DataFrame 구조에 초점을 맞춤.
    print("\n### DataFrame 정보")
    df.info()

# 3.2. 불량 유형 분석
def plot_failure_type_analysis(df):
    print("\n--- 3.2. 불량 유형 분석 ---")
    if 'failureType' not in df.columns:
        print("'failureType' 컬럼을 찾을 수 없습니다. 불량 유형 분석을 건너뜁니다.")
        return

    # 1. 전체 불량 유형 분포 Bar Chart
    plt.figure(figsize=(10, 6))
    failure_counts = df['failureType'].value_counts()
    sns.barplot(x=failure_counts.index, y=failure_counts.values)
    plt.title('전체 불량 유형 분포')
    plt.xlabel('불량 유형')
    plt.ylabel('웨이퍼 수')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(IMAGE_DIR / "불량_유형_분포.png")
    plt.close()
    print("- '불량_유형_분포.png' 저장 완료")

    # 2. 상위 10개 불량 유형 Pareto Chart (직접 구현 또는 라이브러리 사용)
    # Pareto 차트는 복잡하므로 여기서는 상위 10개 bar chart로 대체
    plt.figure(figsize=(12, 6))
    top_10_failure = failure_counts.nlargest(10)
    sns.barplot(x=top_10_failure.index, y=top_10_failure.values)
    plt.title('상위 10개 불량 유형 (Pareto 대안)')
    plt.xlabel('불량 유형')
    plt.ylabel('웨이퍼 수')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(IMAGE_DIR / "상위_10개_불량_유형.png")
    plt.close()
    print("- '상위_10개_불량_유형.png' 저장 완료")

    # 3. 정상 vs 불량 비율 시각화 (Normal / Anomaly)
    # failureType 컬럼에 'Normal'과 'Anomaly'가 있다고 가정
    # 실제 데이터에서는 'none'이 Normal을 의미할 수 있음
    normal_vs_faulty = df['failureType'].apply(lambda x: '정상' if x == 'none' else '불량').value_counts()
    if '정상' not in normal_vs_faulty.index: # 'none'이 없는 경우
        normal_vs_faulty['정상'] = 0
    if '불량' not in normal_vs_faulty.index: # '불량'이 없는 경우
        normal_vs_faulty['불량'] = 0

    plt.figure(figsize=(8, 8))
    plt.pie(normal_vs_faulty.values, labels=normal_vs_faulty.index, autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightcoral'])
    plt.title('정상 vs 불량 웨이퍼 비율')
    plt.tight_layout()
    plt.savefig(IMAGE_DIR / "정상_vs_불량_비율.png")
    plt.close()
    print("- '정상_vs_불량_비율.png' 저장 완료")

# 3.3. 웨이퍼 단위 분석
def plot_wafer_unit_analysis(df):
    print("\n--- 3.3. 웨이퍼 단위 분석 ---")
    
    # dieSize가 0인 경우를 제외하여 오류 방지
    df_filtered = df[df['dieSize'] > 0].copy()

    # failureType 컬럼의 값을 문자열로 변환하여 일관성 유지
    df_filtered['failureType'] = df_filtered['failureType'].astype(str)
    
    # 불량 여부 컬럼 추가 ("[['none']]"이면 0, 아니면 1)
    df_filtered['is_faulty'] = (df_filtered['failureType'] != "[['none']]").astype(int)

    # 불량 웨이퍼 데이터만 필터링
    faulty_wafers = df_filtered[df_filtered['is_faulty'] == 1]
    
    # 불량 웨이퍼의 dieSize 분포 히스토그램
    plt.figure(figsize=(10, 6))
    sns.histplot(faulty_wafers['dieSize'], bins=50, kde=False)
    plt.title('불량 웨이퍼의 다이 사이즈(dieSize) 분포')
    plt.xlabel('다이 사이즈 (dieSize)')
    plt.ylabel('불량 웨이퍼 수')
    plt.tight_layout()
    plt.savefig(IMAGE_DIR / "불량_웨이퍼_다이사이즈_분포.png")
    plt.close()
    print("- '불량_웨이퍼_다이사이즈_분포.png' 저장 완료")

def load_full_data_for_wafermap():
    pkl_path = Path("wafer/data/LSWMD.pkl")
    if pkl_path.exists():
        print(f"\n'{pkl_path}'에서 waferMap 분석을 위해 전체 데이터를 로드합니다.")
        return pd.read_pickle(pkl_path)
    else:
        print("공간 패턴 분석에 필요한 'LSWMD.pkl' 파일을 찾을 수 없습니다.")
        return None

def plot_spatial_pattern_analysis(df_full):
    print("\n--- 3.4. 공간 패턴 분석 ---")
    if df_full is None:
        print("전체 데이터(PKL) 로드에 실패하여 공간 패턴 분석을 건너뜁니다.")
        return

    # 'none' 또는 '[]'이 아닌 불량 웨이퍼만 필터링
    df_full['failureType_str'] = df_full['failureType'].astype(str)
    faulty_df = df_full[(df_full['failureType_str'] != "[['none']]") & (df_full['failureType_str'] != '[]')].copy()
    
    # 1. 대표 웨이퍼 3개 불량 맵 시각화
    if len(faulty_df) >= 3:
        sample_wafers = faulty_df.sample(3, random_state=42) # 재현성을 위해 random_state 설정
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('대표 불량 웨이퍼맵 시각화', fontsize=16)
        for i, (idx, row) in enumerate(sample_wafers.iterrows()):
            ax = axes[i]
            ax.imshow(row['waferMap'], cmap='viridis')
            ax.set_title(f"불량 유형: {row['failureType_str']}\n(WaferIndex: {row['waferIndex']})")
            ax.set_xticks([])
            ax.set_yticks([])
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap
        plt.savefig(IMAGE_DIR / "대표_불량_웨이퍼맵_시각화.png")
        plt.close()
        print("- '대표_불량_웨이퍼맵_시각화.png' 저장 완료")
    else:
        print("- 시각화할 샘플 불량 웨이퍼가 부족합니다.")

    # 2. 전체 불량 좌표 분석
    faulty_pixels_x = []
    faulty_pixels_y = []
    
    for _, row in faulty_df.iterrows():
        # waferMap에서 값이 2인 픽셀의 인덱스를 찾음 (2가 불량을 의미한다고 가정)
        # waferMap은 0(배경), 1(정상 다이), 2(불량 다이) 값으로 이루어져 있음
        faulty_coords = np.where(row['waferMap'] == 2)
        faulty_pixels_y.extend(faulty_coords[0])
        faulty_pixels_x.extend(faulty_coords[1])
        
    if faulty_pixels_x:
        # 불량 위치 Scatter Plot
        plt.figure(figsize=(8, 8))
        plt.scatter(faulty_pixels_x, faulty_pixels_y, alpha=0.05, s=2)
        plt.title('전체 불량 픽셀 위치 분포 (Scatter Plot)')
        plt.xlabel('X 좌표')
        plt.ylabel('Y 좌표')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(IMAGE_DIR / "전체_불량_픽셀_위치_scatter.png")
        plt.close()
        print("- '전체_불량_픽셀_위치_scatter.png' 저장 완료")

        # 불량 좌표 히트맵
        plt.figure(figsize=(8, 8))
        # bins를 waferMap의 일반적인 크기(예: 250x250)에 맞게 조정
        plt.hist2d(x=faulty_pixels_x, y=faulty_pixels_y, bins=[50, 50], cmap='inferno')
        plt.colorbar(label='불량 픽셀 빈도')
        plt.title('전체 불량 픽셀 위치 분포 (2D 히트맵)')
        plt.xlabel('X 좌표')
        plt.ylabel('Y 좌표')
        plt.tight_layout()
        plt.savefig(IMAGE_DIR / "전체_불량_픽셀_위치_heatmap.png")
        plt.close()
        print("- '전체_불량_픽셀_위치_heatmap.png' 저장 완료")
    else:
        print("- 분석할 불량 픽셀이 없습니다.")

# 3.5. 통계 요약
def plot_statistical_summary(df):
    print("\n--- 3.5. 통계 요약 ---")
    
    # 1. 수치형 변수 기술통계
    print("\n### 수치형 변수 기술 통계")
    numerical_cols = df.select_dtypes(include=['number']).columns
    if not numerical_cols.empty:
        print(df[numerical_cols].describe().to_markdown())
    else:
        print("- 수치형 변수가 없습니다.")

    # 2. 이상치 탐지 시각화 (Box Plot)
    for col in numerical_cols:
        plt.figure(figsize=(8, 6))
        sns.boxplot(y=df[col])
        plt.title(f'{col} 변수의 이상치 탐지 (Box Plot)')
        plt.ylabel(col)
        plt.tight_layout()
        plt.savefig(IMAGE_DIR / f"{col}_이상치_탐지.png")
        plt.close()
        print(f"- '{col}_이상치_탐지.png' 저장 완료")

    # 3. 불량 유형별 평균/분산 비교
    if 'failureType' in df.columns and not numerical_cols.empty:
        df_filtered = df.copy()
        df_filtered['failureType_str'] = df_filtered['failureType'].astype(str)

        print("\n### 불량 유형별 수치형 변수 평균")
        print(df_filtered.groupby('failureType_str')[numerical_cols].mean().to_markdown())

        print("\n### 불량 유형별 수치형 변수 분산")
        print(df_filtered.groupby('failureType_str')[numerical_cols].var().to_markdown())

        for col in numerical_cols:
            plt.figure(figsize=(10, 6))
            sns.violinplot(x='failureType_str', y=col, data=df_filtered)
            plt.title(f'불량 유형별 {col} 분포')
            plt.xlabel('불량 유형')
            plt.ylabel(col)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(IMAGE_DIR / f"불량_유형별_{col}_분포.png")
            plt.close()
            print(f"- '불량_유형별_{col}_분포.png' 저장 완료")
    else:
        print("- 'failureType' 컬럼 또는 수치형 변수가 없어 불량 유형별 비교를 건너뜜니다.")

if __name__ == '__main__':
    df_parquet = load_data()
    if df_parquet is not None:
        plot_data_structure(df_parquet)
        plot_failure_type_analysis(df_parquet)
        plot_wafer_unit_analysis(df_parquet)
        
        df_full = load_full_data_for_wafermap() # waferMap 포함된 전체 데이터 로드
        plot_spatial_pattern_analysis(df_full)
        
        plot_statistical_summary(df_parquet) # 통계 요약은 waferMap이 없는 데이터로도 가능
    else:
        print("데이터 로드에 실패하여 EDA를 수행할 수 없습니다.")
