import pandas as pd
from pathlib import Path
import os

def load_and_optimize_data():
    base_dir = Path("wafer")
    data_dir = base_dir / "data"
    
    pkl_path = data_dir / "LSWMD.pkl"
    parquet_path = data_dir / "LSWMD.parquet"

    # Parquet 파일이 존재하면 로드하고 반환
    if parquet_path.exists():
        print(f"'{parquet_path}' 파일이 존재하여 로드합니다.")
        df = pd.read_parquet(parquet_path)
        return df

    # Parquet 파일이 없으면 PKL 파일 로드 후 Parquet으로 저장
    if pkl_path.exists():
        print(f"'{pkl_path}' 파일을 로드하여 Parquet으로 최적화합니다.")
        df = pd.read_pickle(pkl_path)
        
        # Parquet으로 저장
        # 'waferMap' 컬럼을 제외하고 Parquet으로 저장 (pyarrow 변환 오류 방지)
        df_to_save = df.drop(columns=['waferMap'], errors='ignore')
        
        # pyarrow 변환 오류 방지를 위해 df_to_save의 object 타입 컬럼을 string으로 명시적 변환
        for col in df_to_save.select_dtypes(include='object').columns:
            df_to_save[col] = df_to_save[col].astype(str)

        df_to_save.to_parquet(parquet_path)
        print(f"'{parquet_path}' 파일로 저장 완료했습니다.")
        return df
    else:
        print(f"오류: '{pkl_path}' 파일을 찾을 수 없습니다. 'wafer/data' 폴더에 파일을 위치시켜 주세요.")
        return None

if __name__ == '__main__':
    # 'wafer/data' 폴더가 없으면 생성
    data_folder = Path("wafer/data")
    if not data_folder.exists():
        data_folder.mkdir(parents=True, exist_ok=True)
        print(f"'{data_folder}' 폴더를 생성했습니다.")

    # 'wafer/images' 폴더가 없으면 생성
    images_folder = Path("wafer/images")
    if not images_folder.exists():
        images_folder.mkdir(parents=True, exist_ok=True)
        print(f"'{images_folder}' 폴더를 생성했습니다.")
        
    df = load_and_optimize_data()
    if df is not None:
        print("\n데이터 로드 및 최적화가 완료되었습니다. 데이터프레임 정보:")
        df.info()
