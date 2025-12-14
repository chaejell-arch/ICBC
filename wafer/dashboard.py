import streamlit as st
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

# --- 페이지 설정 ---
st.set_page_config(layout="wide", page_title="Wafer-level Defect Map EDA")

# --- 한글 폰트 설정 (메모리 지시사항 반영) ---
def set_korean_font():
    font_path = ""
    if os.name == 'nt':  # Windows
        font_path = "C:/Windows/Fonts/malgunbd.ttf"
    elif os.name == 'posix': # Mac, Linux
        # 시스템에 맞는 폰트 경로 지정 필요
        # 예: "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
        pass
    
    if font_path and Path(font_path).exists():
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
    else:
        st.warning("맑은 고딕 폰트를 찾을 수 없습니다. 한글이 깨질 수 있습니다.")

set_korean_font()

# --- 데이터 로딩 (캐싱 사용) ---
@st.cache_data
def load_data_parquet():
    parquet_path = Path("wafer/data/LSWMD.parquet")
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    else:
        st.error(f"오류: '{parquet_path}' 파일을 찾을 수 없습니다. 데이터 로딩 단계를 먼저 수행해주세요.")
        return None

@st.cache_data
def load_data_pkl():
    pkl_path = Path("wafer/data/LSWMD.pkl")
    if pkl_path.exists():
        return pd.read_pickle(pkl_path)
    else:
        st.error(f"오류: '{pkl_path}' 파일을 찾을 수 없습니다. 공간 패턴 분석을 수행할 수 없습니다.")
        return None

df_parquet = load_data_parquet()
df_pkl = load_data_pkl() # waferMap 분석용

# --- 사이드바 ---
st.sidebar.title("분석 메뉴")
menu = st.sidebar.radio(
    "원하는 분석을 선택하세요.",
    ("홈", "데이터 구조 분석", "불량 유형 분석", "웨이퍼 단위 분석", "공간 패턴 분석", "통계 요약 및 이상치 탐지")
)

# --- 메인 페이지 ---
st.title("Wafer 불량 유형 탐색적 데이터 분석 (EDA) 대시보드")

if menu == "홈":
    st.header("프로젝트 개요")
    st.markdown("""
    이 대시보드는 **Wafer Scribe Word Map 데이터셋(LSWMD)**에 대한 탐색적 데이터 분석(EDA) 결과를 제공합니다.
    
    - **데이터**: 반도체 제조 공정에서 발생하는 웨이퍼 레벨의 불량 맵 데이터
    - **목표**: 데이터의 구조를 파악하고, 다양한 불량 유형의 분포와 특성을 시각적으로 분석하여 불량 원인에 대한 인사이트를 얻고, 향후 머신러닝 모델 개발의 기반을 마련합니다.
    - **사용법**: 왼쪽의 사이드바 메뉴를 통해 원하는 분석 항목을 선택하여 확인할 수 있습니다.
    
    ---
    
    ### 원본 데이터 구조
    - **dieSize**: 다이(die)의 크기
    - **failureType**: 불량 유형 (타겟 변수)
    - **lotName**: 웨이퍼가 속한 로트의 이름
    - **trianTestLabel**: 학습/테스트 데이터 구분 라벨
    - **waferIndex**: 웨이퍼의 인덱스
    - **waferMap**: 웨이퍼의 불량 패턴을 나타내는 2D 배열 (0: 배경, 1: 정상, 2: 불량)
    """)
    st.image("https://www.researchgate.net/profile/Young-Sik-Moon/publication/224213193/figure/fig1/AS:305553589993472@1449861052194/An-example-of-a-wafer-map-with-various-failure-patterns.png",
             caption="다양한 불량 패턴을 가진 웨이퍼 맵 예시")


elif menu == "데이터 구조 분석":
    st.header("3.1. 데이터 구조 분석")
    if df_parquet is not None:
        st.subheader("전체 데이터 수 및 클래스 정보")
        st.metric("전체 웨이퍼 데이터 수", f"{len(df_parquet):,} 개")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("불량 유형(클래스) 수", f"{df_parquet['failureType'].nunique()} 종류")
            st.write(df_parquet['failureType'].unique().tolist())
        with col2:
            st.metric("학습/테스트 라벨 수", f"{df_parquet['trianTestLabel'].nunique()} 종류")
            st.write(df_parquet['trianTestLabel'].unique().tolist())

        st.subheader("데이터 샘플 (상위 5개)")
        cols_to_display = [col for col in df_parquet.columns if col != 'waferMap']
        st.dataframe(df_parquet[cols_to_display].head())
        
        st.subheader("DataFrame 정보")
        # st.text(df_parquet.info())는 잘 표시 안되므로 다른 방식 사용
        import io
        buffer = io.StringIO()
        df_parquet.info(buf=buffer)
        s = buffer.getvalue()
        st.text(s)

elif menu == "불량 유형 분석":
    st.header("3.2. 불량 유형 분석")
    if df_parquet is not None:
        failure_counts = df_parquet['failureType'].value_counts()
        
        # Plotly로 변경하여 인터랙티브하게 제공
        st.subheader("1. 전체 불량 유형 분포")
        fig = px.bar(failure_counts, x=failure_counts.index, y=failure_counts.values,
                     labels={'x': '불량 유형', 'y': '웨이퍼 수'}, title="전체 불량 유형 분포")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("2. 상위 N개 불량 유형")
        top_n = st.slider("확인할 상위 불량 유형 개수를 선택하세요.", 5, 20, 10)
        top_n_failure = failure_counts.nlargest(top_n)
        fig2 = px.bar(top_n_failure, x=top_n_failure.index, y=top_n_failure.values,
                      labels={'x': '불량 유형', 'y': '웨이퍼 수'}, title=f"상위 {top_n}개 불량 유형")
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("3. 정상 vs. 불량 웨이퍼 비율")
        normal_vs_faulty = df_parquet['failureType'].apply(lambda x: '정상' if x == "[['none']]" else '불량').value_counts()
        fig3 = px.pie(normal_vs_faulty, names=normal_vs_faulty.index, values=normal_vs_faulty.values,
                      title='정상 vs. 불량 웨이퍼 비율', hole=0.3)
        st.plotly_chart(fig3, use_container_width=True)

elif menu == "웨이퍼 단위 분석":
    st.header("3.3. 웨이퍼 단위 분석")
    if df_parquet is not None:
        df_filtered = df_parquet[df_parquet['dieSize'] > 0].copy()
        df_filtered['is_faulty'] = (df_filtered['failureType'] != "[['none']]" ).astype(int)
        faulty_wafers = df_filtered[df_filtered['is_faulty'] == 1]

        st.subheader("불량 웨이퍼의 다이 사이즈(dieSize) 분포")
        fig = px.histogram(faulty_wafers, x='dieSize', nbins=50,
                             title='불량 웨이퍼의 다이 사이즈(dieSize) 분포',
                             labels={'dieSize': '다이 사이즈'})
        st.plotly_chart(fig, use_container_width=True)

elif menu == "공간 패턴 분석":
    st.header("3.4. 공간 패턴 분석 (Wafer Map)")
    if df_pkl is not None:
        df_pkl['failureType_str'] = df_pkl['failureType'].astype(str)
        faulty_df = df_pkl[(df_pkl['failureType_str'] != "[['none']]" ) & (df_pkl['failureType_str'] != '[]')].copy()
        
        st.subheader("1. 대표 불량 웨이퍼맵 시각화")
        st.markdown("`random_state=42`로 고정된 3개의 샘플입니다.")
        
        sample_wafers = faulty_df.sample(3, random_state=42)
        
        cols = st.columns(3)
        for i, (idx, row) in enumerate(sample_wafers.iterrows()):
            with cols[i]:
                fig, ax = plt.subplots()
                ax.imshow(row['waferMap'], cmap='viridis')
                ax.set_title(f"유형: {row['failureType_str']}\n(인덱스: {row['waferIndex']})", fontsize=10)
                ax.set_xticks([])
                ax.set_yticks([])
                st.pyplot(fig)
        
        st.subheader("2. 전체 불량 픽셀 위치 분석")
        
        # 이 부분은 계산에 시간이 걸릴 수 있으므로 캐싱
        @st.cache_data
        def get_faulty_pixels(_faulty_df):
            faulty_pixels_x = []
            faulty_pixels_y = []
            for _, row in _faulty_df.iterrows():
                faulty_coords = np.where(row['waferMap'] == 2)
                faulty_pixels_y.extend(faulty_coords[0])
                faulty_pixels_x.extend(faulty_coords[1])
            return faulty_pixels_x, faulty_pixels_y

        faulty_pixels_x, faulty_pixels_y = get_faulty_pixels(faulty_df)
        
        if faulty_pixels_x:
            col1, col2 = st.columns(2)
            with col1:
                # Plotly Scatter
                fig1 = px.scatter(x=faulty_pixels_x, y=faulty_pixels_y, 
                                  title='전체 불량 픽셀 위치 분포 (Scatter Plot)',
                                  labels={'x': 'X 좌표', 'y': 'Y 좌표'})
                fig1.update_traces(marker=dict(size=2, opacity=0.1))
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                # Plotly 2D Histogram (Heatmap)
                fig2 = px.density_heatmap(x=faulty_pixels_x, y=faulty_pixels_y,
                                          title='전체 불량 픽셀 위치 분포 (2D 히트맵)',
                                          labels={'x': 'X 좌표', 'y': 'Y 좌표'},
                                          nbinsx=50, nbinsy=50)
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("분석할 불량 픽셀이 없습니다.")


elif menu == "통계 요약 및 이상치 탐지":
    st.header("3.5. 통계 요약 및 이상치 탐지")
    if df_parquet is not None:
        numerical_cols = df_parquet.select_dtypes(include=['number']).columns
        
        st.subheader("1. 수치형 변수 기술 통계")
        st.dataframe(df_parquet[numerical_cols].describe())

        st.subheader("2. 이상치 탐지 (Box Plot)")
        selected_col = st.selectbox("변수를 선택하세요:", numerical_cols)
        fig = px.box(df_parquet, y=selected_col, title=f'{selected_col} 변수의 이상치 탐지')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("3. 불량 유형별 수치형 변수 분포")
        df_filtered = df_parquet.copy()
        df_filtered['failureType'] = df_filtered['failureType'].astype(str)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 불량 유형별 평균")
            st.dataframe(df_filtered.groupby('failureType')[numerical_cols].mean())
        with col2:
            st.markdown("#### 불량 유형별 분산")
            st.dataframe(df_filtered.groupby('failureType')[numerical_cols].var())

        selected_col_violin = st.selectbox("분포를 확인할 변수를 선택하세요:", numerical_cols, key='violin')
        fig_violin = px.violin(df_filtered, x='failureType', y=selected_col_violin,
                               title=f'불량 유형별 {selected_col_violin} 분포',
                               box=True, points="all")
        fig_violin.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_violin, use_container_width=True)

st.sidebar.info("""
    **Projet:** Wafer Defect Analysis
    **Data:** LSWMD
    **Developer:** Gemini Agent
""")
