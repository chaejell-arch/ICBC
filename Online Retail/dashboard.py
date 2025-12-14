
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import StringIO

# --- 페이지 설정 ---
st.set_page_config(
    page_title="온라인 소매 데이터 분석 대시보드",
    page_icon="🛒",
    layout="wide",
)

# --- 1. 데이터 로드 및 전처리 (캐싱 적용) ---
@st.cache_data
def load_and_preprocess_data():
    """
    엑셀 또는 CSV 파일을 로드하고 명세서에 따라 전처리한 후, 데이터프레임을 반환합니다.
    - InvoiceDate와 StockCode를 문자열로 읽어 PyArrow 오류를 원천 방지합니다.
    - 계산을 위한 datetime 컬럼 'InvoiceDate_dt'를 별도로 생성합니다.
    """
    path_xlsx = 'Online_Retail.xlsx'
    path_csv = 'Online_Retail.csv'
    df = None
    
    # 데이터 타입을 명시하여 로드
    dtype_spec = {'InvoiceDate': str, 'StockCode': str}

    try:
        df = pd.read_excel(path_xlsx, dtype=dtype_spec)
    except FileNotFoundError:
        st.info(f"정보: '{path_xlsx}' 파일을 찾을 수 없습니다. '{path_csv}' 파일을 읽어옵니다.")
        try:
            df = pd.read_csv(path_csv, encoding='latin1', dtype=dtype_spec)
        except FileNotFoundError:
            st.error(f"오류: '{path_xlsx}'와 '{path_csv}' 파일을 모두 찾을 수 없습니다. 'Online Retail' 폴더에 데이터 파일을 위치시켜 주세요.")
            st.stop()
    except Exception as e:
        st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {e}")
        st.stop()

    # CustomerID 결측치 제거
    df.dropna(subset=['CustomerID'], inplace=True)
    
    # 중복된 행 제거
    df.drop_duplicates(inplace=True)
    
    # CustomerID 정수형으로 변환
    df['CustomerID'] = df['CustomerID'].astype(int)
    
    # 계산을 위한 datetime 객체 생성
    df['InvoiceDate_dt'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    
    # 수량(Quantity)과 단가(UnitPrice) 0 초과인 데이터만 필터링
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # TotalPrice 파생 변수 생성
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # 분석에 필요한 시간 관련 컬럼 추가 (datetime 객체 사용)
    df['YearMonth'] = df['InvoiceDate_dt'].dt.to_period('M').astype(str)
    df['Hour'] = df['InvoiceDate_dt'].dt.hour
    df['DayOfWeek'] = df['InvoiceDate_dt'].dt.day_name()
    
    return df

# 데이터 로드
df_source = load_and_preprocess_data()

# --- 2. 대시보드 레이아웃 ---
st.title("🛒 온라인 소매 데이터 분석 대시보드")

# 사이드바 메뉴
st.sidebar.title("메뉴")
menu = st.sidebar.radio(
    "분석 페이지를 선택하세요:",
    ("메인", "매출 분석", "고객 및 상품 분석", "사용자 행동 분석")
)

# 사이드바 필터
st.sidebar.title("데이터 필터")
selected_country = st.sidebar.selectbox(
    '국가 선택',
    options=['All'] + sorted(df_source['Country'].unique().tolist()) if df_source is not None else []
)

# 필터링된 데이터 생성
if df_source is not None:
    if selected_country == 'All':
        df_filtered = df_source.copy()
    else:
        df_filtered = df_source[df_source['Country'] == selected_country].copy()
else:
    df_filtered = pd.DataFrame()


# --- 페이지 렌더링 ---
if menu == "메인":
    st.header("대시보드 개요 및 데이터 검색")
    st.markdown(
        """
        이 페이지는 **온라인 리테일 거래 데이터셋**의 전반적인 개요를 제공합니다. 데이터 샘플, 주요 통계 정보, 그리고 데이터의 구조를 확인할 수 있습니다. 또한, 특정 **상품 설명이나 송장 번호**를 통해 원하는 **거래 기록**을 쉽게 검색할 수 있는 기능을 제공하여 데이터 탐색을 돕습니다.
        """
    )
    
    # 데이터 개요 탭
    tab1, tab2, tab3, tab4 = st.tabs(["데이터 샘플", "기본 정보", "기술 통계량", "분석 검증"])
    with tab1:
        st.subheader("데이터 샘플 (상위 10개)")
        if not df_filtered.empty:
            st.dataframe(df_filtered.drop(columns=['InvoiceDate_dt']).head(10))
    with tab2:
        st.subheader("기본 정보")
        if not df_filtered.empty:
            buffer = StringIO()
            df_filtered.info(buf=buffer)
            st.text(buffer.getvalue())
    with tab3:
        st.subheader("기술 통계량")
        if not df_filtered.empty:
            st.dataframe(df_filtered.drop(columns=['InvoiceDate_dt']).describe())
        
    with tab4:
        st.subheader("데이터 무결성 및 주요 계산 검증")
        st.markdown("""
        AI 분석 과정에서 발생할 수 있는 오류를 최소화하기 위해, 핵심 데이터 무결성 및 계산의 정확성을 검증합니다.
        여기서는 전처리된 데이터의 일관성과 주요 파생 변수의 유효성을 확인합니다.
        """)

        if not df_filtered.empty:
            # 1. TotalPrice 계산 검증
            # 부동 소수점 비교의 한계로 인해 근사치 비교 사용
            total_price_check = (abs(df_filtered['TotalPrice'] - (df_filtered['Quantity'] * df_filtered['UnitPrice'])) < 1e-6).all()
            if total_price_check:
                st.success("✅ 'TotalPrice' 컬럼 계산이 'Quantity * UnitPrice'와 일치합니다. (허용 오차 1e-6)")
            else:
                st.error("❌ 'TotalPrice' 컬럼에 계산 오류가 있습니다. (Quantity * UnitPrice와 불일치)")

            # 2. 음수/0 값 검증 (Quantity, UnitPrice) - 전처리 단계에서 제거되었어야 함
            negative_qty_check = (df_filtered['Quantity'] <= 0).any()
            negative_price_check = (df_filtered['UnitPrice'] <= 0).any()

            if not negative_qty_check:
                st.success("✅ 'Quantity' 컬럼에 0 이하의 값이 없습니다.")
            else:
                st.warning("⚠️ 'Quantity' 컬럼에 0 이하의 값이 발견되었습니다.")
                st.dataframe(df_filtered[df_filtered['Quantity'] <= 0])

            if not negative_price_check:
                st.success("✅ 'UnitPrice' 컬럼에 0 이하의 값이 없습니다.")
            else:
                st.warning("⚠️ 'UnitPrice' 컬럼에 0 이하의 값이 발견되었습니다.")
                st.dataframe(df_filtered[df_filtered['UnitPrice'] <= 0])

            # 3. CustomerID 결측치 검증 - 전처리 단계에서 제거되었어야 함
            customer_id_null_check = df_filtered['CustomerID'].isnull().any()
            if not customer_id_null_check:
                st.success("✅ 'CustomerID' 컬럼에 결측치가 없습니다.")
            else:
                st.error("❌ 'CustomerID' 컬럼에 결측치가 발견되었습니다.")
                st.dataframe(df_filtered[df_filtered['CustomerID'].isnull()])
        else:
            st.info("데이터가 비어있어 검증을 수행할 수 없습니다.")
        
    # 데이터 검색 기능
    st.subheader("데이터 검색")
    search_term = st.text_input("상품 설명(Description) 또는 송장 번호(InvoiceNo)로 검색:")
    if search_term and not df_filtered.empty:
        search_result_desc = df_filtered[df_filtered['Description'].str.contains(search_term, case=False, na=False)]
        search_result_invoice = df_filtered[df_filtered['InvoiceNo'].astype(str).str.contains(search_term, case=False, na=False)]
        search_result = pd.concat([search_result_desc, search_result_invoice]).drop_duplicates()
        st.write(f"'{search_term}'에 대한 검색 결과: {len(search_result)}개")
        st.dataframe(search_result.drop(columns=['InvoiceDate_dt']))


elif menu == "매출 분석":
    st.header("매출 분석")
    st.markdown(
        """
        이 페이지에서는 **온라인 상점의 매출 트렌드와 패턴**을 심층적으로 분석합니다.
        월별 총 매출 추이, 주요 국가별 매출 기여도, 그리고 **시간대별 및 요일별 고객 주문** 변화 등 다양한 관점에서 **온라인 판매 성과**를 탐색합니다.
        """
    )
    
    if not df_filtered.empty:
        tab1, tab2 = st.tabs(["월별/국가별 매출 분석", "시간/요일별 주문 분석"])
        
        with tab1:
            st.subheader("월별 총 매출")
            monthly_sales = df_filtered.groupby('YearMonth')['TotalPrice'].sum().reset_index()
            fig1 = px.line(monthly_sales, x='YearMonth', y='TotalPrice', title="월별 총 매출 추이", markers=True)
            st.plotly_chart(fig1, use_container_width=True)
            with st.expander("데이터 보기"):
                st.dataframe(monthly_sales)

            st.subheader("상위 10개국 매출")
            if selected_country == 'All':
                top_10_countries = df_source.groupby('Country')['TotalPrice'].sum().nlargest(10).reset_index()
                fig2 = px.bar(top_10_countries, x='Country', y='TotalPrice', title="상위 10개국 매출")
                st.plotly_chart(fig2, use_container_width=True)
                with st.expander("데이터 보기"):
                    st.dataframe(top_10_countries)
            else:
                st.info(f"'{selected_country}' 국가의 데이터만 표시되고 있습니다. 전체 국가를 보려면 필터에서 'All'을 선택하세요.")

        with tab2:
            st.subheader("시간대별 주문 건수")
            hourly_orders = df_filtered['Hour'].value_counts().sort_index().reset_index()
            hourly_orders.columns = ['Hour', 'Count']
            fig3 = px.bar(hourly_orders, x='Hour', y='Count', title="시간대별 주문 건수")
            st.plotly_chart(fig3, use_container_width=True)
            with st.expander("데이터 보기"):
                st.dataframe(hourly_orders)

            st.subheader("요일별 주문 건수")
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            df_filtered['DayOfWeek'] = pd.Categorical(df_filtered['DayOfWeek'], categories=days_order, ordered=True)
            weekly_orders = df_filtered['DayOfWeek'].value_counts().sort_index().reset_index()
            weekly_orders.columns = ['DayOfWeek', 'Count']
            fig4 = px.bar(weekly_orders, x='DayOfWeek', y='Count', title="요일별 주문 건수")
            st.plotly_chart(fig4, use_container_width=True)
            with st.expander("데이터 보기"):
                st.dataframe(weekly_orders)
    else:
        st.warning("선택된 필터에 해당하는 데이터가 없습니다.")


elif menu == "고객 및 상품 분석":
    st.header("고객 및 상품 분석")
    st.markdown(
        """
        이 페이지는 **온라인 고객의 구매 행동**과 **상품의 판매 성과**를 집중적으로 분석합니다.
        가장 많이 팔린 **상위 상품**, **고객별 총 구매액** 순위 등 **온라인 비즈니스**에서 중요한 지표들을 시각화하여 고객과 상품 전략 수립에 필요한 인사이트를 제공합니다.
        """
    )

    if not df_filtered.empty:
        tab1, tab2 = st.tabs(["상품 분석", "고객 분석"])

        with tab1:
            st.subheader("상위 10개 상품 판매량")
            top_10_products = df_filtered.groupby('Description')['Quantity'].sum().nlargest(10).sort_values(ascending=True).reset_index()
            fig5 = px.bar(top_10_products, y='Description', x='Quantity', orientation='h', title="상위 10개 상품 판매량")
            st.plotly_chart(fig5, use_container_width=True)
            with st.expander("데이터 보기"):
                st.dataframe(top_10_products)

        with tab2:
            st.subheader("상위 10명 고객 구매액")
            top_10_customers = df_filtered.groupby('CustomerID')['TotalPrice'].sum().nlargest(10).sort_values(ascending=False).reset_index()
            top_10_customers['CustomerID'] = top_10_customers['CustomerID'].astype(str)
            fig6 = px.bar(top_10_customers, x='CustomerID', y='TotalPrice', title="상위 10명 고객 구매액")
            st.plotly_chart(fig6, use_container_width=True)
            with st.expander("데이터 보기"):
                st.dataframe(top_10_customers)
    else:
        st.warning("선택된 필터에 해당하는 데이터가 없습니다.")


elif menu == "사용자 행동 분석":
    st.header("사용자 행동 분석 (ARPU, DAU/MAU, 리텐션)")
    st.markdown(
        """
        이 페이지에서는 **온라인 고객**의 핵심 행동 지표인 ARPU(사용자당 평균 매출), DAU/MAU(일간/월간 활성 사용자),
        그리고 **고객 리텐션(재구매율)**을 상세하게 분석합니다. 이 지표들을 통해 **고객 유지 전략** 및 **장기적인 수익성** 개선을 위한 중요한 인사이트를 얻을 수 있습니다.
        """
    )
    
    if not df_filtered.empty:
        tab1, tab2, tab3 = st.tabs(["월별 ARPU", "DAU vs MAU", "고객 리텐션"])

        with tab1:
            st.subheader("월별 사용자당 평균 매출 (ARPU)")
            monthly_revenue = df_filtered.groupby('YearMonth')['TotalPrice'].sum()
            monthly_users = df_filtered.groupby('YearMonth')['CustomerID'].nunique()
            # 0으로 나누는 경우 방지
            monthly_users = monthly_users.replace(0, np.nan)
            arpu = (monthly_revenue / monthly_users).reset_index()
            arpu.columns = ['YearMonth', 'ARPU']
            
            fig7 = go.Figure()
            fig7.add_trace(go.Scatter(x=arpu['YearMonth'], y=arpu['ARPU'], mode='lines+markers', name='ARPU'))
            fig7.add_trace(go.Bar(x=arpu['YearMonth'], y=arpu['ARPU'], name='ARPU (Bar)', opacity=0.5))
            fig7.update_layout(
                title="월별 ARPU(사용자당 평균 매출, 단위: £)",
                yaxis_title="ARPU (£)"
            )
            st.plotly_chart(fig7, use_container_width=True)
            with st.expander("ARPU 데이터 보기"):
                st.dataframe(arpu)

        with tab2:
            st.subheader("일간/월간 활성 사용자 (DAU vs MAU)")
            dau = df_filtered.groupby(df_filtered['InvoiceDate_dt'].dt.date)['CustomerID'].nunique().mean()
            mau = df_filtered.groupby('YearMonth')['CustomerID'].nunique().mean()
            
            st.metric(label="평균 DAU (일간 활성 사용자)", value=f"{dau:.2f}")
            st.metric(label="평균 MAU (월간 활성 사용자)", value=f"{mau:.2f}")

            fig8 = go.Figure(go.Bar(x=['평균 DAU', '평균 MAU'], y=[dau, mau], text=[f"{dau:.2f}", f"{mau:.2f}"], textposition='auto'))
            fig8.update_layout(title="평균 DAU vs MAU")
            st.plotly_chart(fig8, use_container_width=True)

        with tab3:
            st.subheader("월단위 고객 리텐션")
            df_retention = df_filtered.copy()
            df_retention['InvoiceMonth'] = df_retention['InvoiceDate_dt'].dt.to_period('M')
            df_retention['AcquisitionMonth'] = df_retention.groupby('CustomerID')['InvoiceMonth'].transform('min')

            def get_month_diff(row):
                return (row['InvoiceMonth'] - row['AcquisitionMonth']).n

            df_retention['CohortIndex'] = df_retention.apply(get_month_diff, axis=1)
            
            cohort_data = df_retention.groupby(['AcquisitionMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
            cohort_count = cohort_data.pivot_table(index='AcquisitionMonth', columns='CohortIndex', values='CustomerID')
            
            cohort_size = cohort_count.iloc[:, 0]
            retention = cohort_count.divide(cohort_size, axis=0) * 100
            retention.index = retention.index.strftime('%Y-%m')
            
            # 첫 번째 열 이름 'Acquisition'으로 변경
            retention.rename(columns={0: 'Acquisition'}, inplace=True)
            
            fig9 = go.Figure(data=go.Heatmap(
                z=retention.T,
                x=retention.index,
                y=[f"Month {i}" for i in retention.columns],
                colorscale='Viridis',
                text=retention.T.applymap(lambda x: f'{x:.1f}%' if not pd.isna(x) else ''),
                texttemplate="%{text}",
                hoverongaps=False
            ))
            fig9.update_layout(title='월단위 고객 리텐션 (%)',
                               xaxis_title='신규 고객 확보 월',
                               yaxis_title='경과 월')
            st.plotly_chart(fig9, use_container_width=True)
            with st.expander("리텐션 데이터 보기 (%)"):
                st.dataframe(retention.style.format("{:.1f}%", na_rep=""))
    else:
        st.warning("선택된 필터에 해당하는 데이터가 없습니다.")

if df_source is None:
    st.warning("데이터를 로드하지 못해 대시보드를 표시할 수 없습니다.")
