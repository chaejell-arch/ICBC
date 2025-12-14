
import pandas as pd
import datetime

def test_data_processing():
    """
    Tests the data loading and processing logic from the dashboard script.
    """
    print("--- 1. 데이터 로드 및 기본 전처리 시작 ---")
    try:
        df = pd.read_csv('Online Retail/Online_Retail.csv')
        df.dropna(subset=['CustomerID'], inplace=True)
        df['Description'].fillna('알 수 없음', inplace=True)
        df['CustomerID'] = df['CustomerID'].astype(int)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
        df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
        df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
        print("--- 데이터 로드 및 기본 전처리 성공 ---")
    except Exception as e:
        print(f"오류: 데이터 로드 또는 기본 전처리 중 실패: {e}")
        return

    print("\n--- 2. RFM 분석 로직 테스트 시작 ---")
    try:
        snapshot_date = df['InvoiceDate'].max() + datetime.timedelta(days=1)
        rfm = df.groupby('CustomerID').agg({
            'InvoiceDate': lambda date: (snapshot_date - date.max()).days,
            'InvoiceNo': 'nunique',
            'TotalPrice': 'sum'
        })
        rfm.rename(columns={'InvoiceDate': 'Recency', 'InvoiceNo': 'Frequency', 'TotalPrice': 'Monetary'}, inplace=True)
        
        print("RFM 집계 성공. qcut 실행 전...")

        # qcut 실행 및 오류 확인
        print("Recency(R) 점수 계산 중...")
        r_labels = range(4, 0, -1)
        # Handle potential non-unique bin edges in Recency
        try:
            r_quartiles = pd.qcut(rfm['Recency'], 4, labels=r_labels)
        except ValueError:
            print("Recency에서 중복된 경계값 발견. rank(method='first')로 처리합니다.")
            r_quartiles = pd.qcut(rfm['Recency'].rank(method='first'), 4, labels=r_labels)

        print("Frequency(F) 점수 계산 중...")
        f_labels = range(1, 5)
        # Frequency is discrete, rank(method='first') is a good practice
        f_quartiles = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=f_labels)
        
        print("Monetary(M) 점수 계산 중...")
        m_labels = range(1, 5)
        # Handle potential non-unique bin edges in Monetary
        try:
            m_quartiles = pd.qcut(rfm['Monetary'], 4, labels=m_labels)
        except ValueError:
            print("Monetary에서 중복된 경계값 발견. rank(method='first')로 처리합니다.")
            m_quartiles = pd.qcut(rfm['Monetary'].rank(method='first'), 4, labels=m_labels)
        
        rfm = rfm.assign(R=r_quartiles, F=f_quartiles, M=m_quartiles)
        print("RFM 점수 계산 성공.")
        
        print("--- RFM 분석 로직 테스트 성공 ---")
        
    except Exception as e:
        print(f"오류: RFM 분석 중 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_processing()
