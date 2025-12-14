import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt # waferMap 시각화용 (디버깅)

def prepare_cnn_data():
    pkl_path = Path("wafer/data/LSWMD.pkl")
    cnn_data_path = Path("wafer/data/cnn_data.npz")

    if not pkl_path.exists():
        print(f"오류: '{pkl_path}' 파일을 찾을 수 없습니다. PKL 파일을 먼저 준비해주세요.")
        return None, None, None, None, None

    print(f"'{pkl_path}' 파일을 로드하여 CNN 학습용 데이터를 준비합니다.")
    df_full = pd.read_pickle(pkl_path)

    # waferMap 데이터 추출
    # 각 waferMap 배열의 크기가 다를 수 있으므로, 동일한 크기로 패딩 또는 리사이즈 필요
    # 여기서는 가장 큰 waferMap 크기에 맞춰 0으로 패딩 (임시 방편)
    # 실제 CNN에서는 특정 크기로 리사이즈하는 전처리 단계가 필요함.
    # 현재 EDA 결과에서는 waferMap 크기가 모두 동일한 것으로 가정하고 진행

    # 모든 waferMap이 동일한 크기인지 확인
    if not all(map_data.shape == df_full['waferMap'].iloc[0].shape for map_data in df_full['waferMap']):
        print("경고: waferMap의 크기가 다릅니다. CNN 입력 전 추가 전처리가 필요할 수 있습니다.")
        # 모든 waferMap을 동일한 크기로 리사이즈하는 로직이 필요
        # 예를 들어, 최대 크기를 찾아서 패딩하거나, 특정 크기로 리사이즈
        max_height = max(map_data.shape[0] for map_data in df_full['waferMap'])
        max_width = max(map_data.shape[1] for map_data in df_full['waferMap'])
        
        padded_wafer_maps = []
        for map_data in df_full['waferMap']:
            padded_map = np.pad(map_data, 
                                ((0, max_height - map_data.shape[0]), 
                                 (0, max_width - map_data.shape[1])),
                                'constant', constant_values=0)
            padded_wafer_maps.append(padded_map)
        X_waferMap = np.array(padded_wafer_maps)
    else:
        X_waferMap = np.array(df_full['waferMap'].tolist())
    
    # failureType 추출 및 정수 인코딩
    y_failureType = df_full['failureType'].astype(str) # string으로 변환
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_failureType)

    # trianTestLabel을 사용하여 학습/검증 데이터 분리
    # Parquet 저장 시 trianTestLabel_encoded를 사용했으므로, 여기서는 raw trianTestLabel 사용
    trianTestLabel_encoder = LabelEncoder()
    trianTestLabel_encoded = trianTestLabel_encoder.fit_transform(df_full['trianTestLabel'].astype(str))

    X_train_wafer = X_waferMap[trianTestLabel_encoded == trianTestLabel_encoder.transform(["[['Training']]"])[0]]
    y_train_wafer = y_encoded[trianTestLabel_encoded == trianTestLabel_encoder.transform(["[['Training']]"])[0]]

    X_test_wafer = X_waferMap[trianTestLabel_encoded == trianTestLabel_encoder.transform(["[['Test']]"])[0]]
    y_test_wafer = y_encoded[trianTestLabel_encoded == trianTestLabel_encoder.transform(["[['Test']]"])[0]]

    # waferMap 데이터 전처리: 흑백 이미지화 (0, 1, 2 값을 0, 1로 스케일링 또는 이진화)
    # 현재 값은 0(배경), 1(정상), 2(불량)이므로, 2를 1로, 나머지를 0으로 이진화 (불량 위치만 강조)
    # 또는 0, 1, 2 그대로 사용하거나 (0-255) 스케일링 (0-1)
    # 여기서는 0과 1사이로 스케일링: 0->0, 1->0.5, 2->1
    # CNN 모델에 따라 입력 형태와 값 범위가 달라질 수 있습니다.
    X_train_wafer_processed = (X_train_wafer / 2.0).astype(np.float32)
    X_test_wafer_processed = (X_test_wafer / 2.0).astype(np.float32)
    
    # 채널 차원 추가 (컬러 이미지의 경우 (height, width, channels) 이지만 흑백이면 (height, width, 1))
    X_train_wafer_processed = np.expand_dims(X_train_wafer_processed, axis=-1)
    X_test_wafer_processed = np.expand_dims(X_test_wafer_processed, axis=-1)

    # 데이터 저장
    np.savez_compressed(cnn_data_path, 
                        X_train=X_train_wafer_processed, 
                        y_train=y_train_wafer, 
                        X_test=X_test_wafer_processed, 
                        y_test=y_test_wafer, 
                        classes=label_encoder.classes_)
    print(f"CNN 학습용 데이터가 '{cnn_data_path}'에 저장되었습니다.")

    print("\nCNN 학습용 데이터 준비가 완료되었습니다.")
    print(f"X_train_wafer shape: {X_train_wafer_processed.shape}")
    print(f"y_train_wafer shape: {y_train_wafer.shape}")
    print(f"X_test_wafer shape: {X_test_wafer_processed.shape}")
    print(f"y_test_wafer shape: {y_test_wafer.shape}")
    print(f"failureType 클래스: {label_encoder.classes_}")

    return X_train_wafer_processed, y_train_wafer, X_test_wafer_processed, y_test_wafer, label_encoder.classes_

if __name__ == '__main__':
    X_train, y_train, X_test, y_test, classes = prepare_cnn_data()
    if X_train is not None:
        print("\nCNN 학습용 데이터의 일부를 시각화합니다:")
        # 샘플 이미지 시각화
        fig, axes = plt.subplots(1, 5, figsize=(15, 3))
        for i in range(5):
            axes[i].imshow(X_train[i, :, :, 0], cmap='gray')
            axes[i].set_title(f"Class: {classes[y_train[i]]}")
            axes[i].axis('off')
        plt.tight_layout()
        # plt.show() # Streamlit 환경에서는 plt.show() 대신 이미지로 저장
        plt.savefig(Path("wafer/images") / "cnn_sample_wafermaps.png")
        plt.close()
        print("- 'cnn_sample_wafermaps.png' 저장 완료")
