import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

def preprocess_data():
    parquet_path = Path("wafer/data/LSWMD.parquet")
    processed_parquet_path = Path("wafer/data/processed_data.parquet")

    if not parquet_path.exists():
        print(f"오류: '{parquet_path}' 파일을 찾을 수 없습니다. 데이터 로딩 단계를 먼저 수행해주세요.")
        return None, None, None, None, None

    print(f"'{parquet_path}' 파일을 로드하여 전처리를 시작합니다.")
    df = pd.read_parquet(parquet_path)

    # 1. 결측치 처리 (LSWMD.parquet에는 결측치가 없는 상태로 가정)
    # 필요한 경우 여기에 SimpleImputer 등을 추가할 수 있습니다.
    
    # 2. 이상치 처리 (EDA에서 시각화했지만, 여기서는 제거 또는 capping 로직은 추가하지 않음)
    # 실제 모델 학습 시 필요에 따라 이상치 처리 로직을 여기에 추가할 수 있습니다.
    
    # 3. 범주형 변수 인코딩
    # 'failureType'은 타겟 변수이므로 Label Encoding
    # 'trianTestLabel'도 Training/Test 구분용이므로 Label Encoding
    # 'lotName'은 고유값이 많아 인코딩 시 희소성 문제가 생길 수 있으므로, 일단 제외

    # 타겟 변수 (y)와 피처 (X) 분리
    X = df.drop(columns=['failureType', 'lotName']) # lotName은 일단 제외
    y = df['failureType']

    # 'trianTestLabel' 인코딩 (Training:0, Test:1 또는 그 반대)
    # df_parquet에 저장될 때 이미 string으로 변환되었음.
    label_encoder_traintest = LabelEncoder()
    X['trianTestLabel_encoded'] = label_encoder_traintest.fit_transform(X['trianTestLabel'])
    X = X.drop(columns=['trianTestLabel'])

    # 'failureType' 인코딩 (타겟 변수)
    label_encoder_failure = LabelEncoder()
    y_encoded = label_encoder_failure.fit_transform(y)
    
    # 수치형 변수 스케일링
    numerical_features = ['dieSize', 'waferIndex']
    
    # MinMaxScaler 사용 (0-1 범위)
    scaler = MinMaxScaler()
    X[numerical_features] = scaler.fit_transform(X[numerical_features])

    # 학습/검증 데이터 분리 (trianTestLabel 사용)
    # label_encoder_traintest.transform(["[['Training']]"])[0] 결과는 단일 값이므로 [0]으로 접근
    training_label_encoded = label_encoder_traintest.transform(["[['Training']]"])[0]
    test_label_encoded = label_encoder_traintest.transform(["[['Test']]"])[0]


    X_train = X[X['trianTestLabel_encoded'] == training_label_encoded].drop(columns=['trianTestLabel_encoded'])
    y_train = y_encoded[X['trianTestLabel_encoded'] == training_label_encoded]

    X_test = X[X['trianTestLabel_encoded'] == test_label_encoded].drop(columns=['trianTestLabel_encoded'])
    y_test = y_encoded[X['trianTestLabel_encoded'] == test_label_encoded]
    
    # 전처리된 데이터 저장
    # X_full_processed = X.copy()
    # X_full_processed['failureType_encoded'] = y_encoded
    # X_full_processed.to_parquet(processed_parquet_path, index=False)
    # print(f"전처리된 전체 데이터가 '{processed_parquet_path}'에 저장되었습니다.")

    print("\n데이터 전처리가 완료되었습니다.")
    print(f"학습 데이터 X_train shape: {X_train.shape}")
    print(f"학습 데이터 y_train shape: {y_train.shape}")
    print(f"검증 데이터 X_test shape: {X_test.shape}")
    print(f"검증 데이터 y_test shape: {y_test.shape}")

    # LabelEncoder 객체 자체와 클래스 이름을 반환하여 대시보드에서 사용
    return X_train, y_train, X_test, y_test, label_encoder_failure

if __name__ == '__main__':
    X_train, y_train, X_test, y_test, label_encoder_failure = preprocess_data()
    if X_train is not None:
        print("\n전처리된 데이터의 일부를 표시합니다:")
        print("X_train head:")
        print(X_train.head().to_markdown(index=False))
        print("\ny_train head:")
        print(y_train[:5])
        print(f"\nfailureType 클래스: {label_encoder_failure.classes_}")
