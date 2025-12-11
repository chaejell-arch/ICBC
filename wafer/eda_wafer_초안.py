import pandas as pd
import os
import io
from contextlib import redirect_stdout
import numpy as np # numpy.ndarray를 확인하기 위해 임포트

def check_wafer_data():
    output_dir = "wafer"
    data_path = os.path.join(output_dir, "LSWMD.pkl")

    print(f"'{data_path}' 파일을 로드하여 기본 정보를 확인합니다.")

    try:
        # .pkl 파일 로드
        df = pd.read_pickle(data_path)
        
        print("\n### 데이터 샘플 (상위 5개) - waferMap 제외")
        # waferMap 컬럼이 np.ndarray와 같은 복잡한 객체일 가능성이 높으므로, 미리 제외하고 출력
        cols_to_display = [col for col in df.columns if col != 'waferMap']
        print(df[cols_to_display].head().to_markdown())

        print("\n### waferMap 컬럼 첫 5개 값의 타입 및 형태 확인")
        if 'waferMap' in df.columns:
            for i, val in enumerate(df['waferMap'].head()):
                print(f"Index {i}: Type - {type(val)}, Shape - {val.shape if isinstance(val, np.ndarray) else 'Not an array'}")
        else:
            print("- 컬럼 'waferMap'을(를) 찾을 수 없습니다.")

        print("\n### 데이터 기본 정보")
        # df.info()의 출력을 캡처하여 출력
        f = io.StringIO()
        with redirect_stdout(f):
            df.info()
        info_output = f.getvalue()
        print(info_output)
        
        print("\n### 데이터 요약 통계")
        print(df.describe(include='all').to_markdown())

        print("\n### 주요 컬럼 고유값 확인")
        # waferMap 컬럼은 고유값 확인 시 오류를 발생시키거나 의미 없는 정보를 줄 수 있으므로 제외
        for col in ['waferId', 'lotName', 'trianTestLabel', 'quality', 'pattern', 'dieSize', 'testResult']:
            if col in df.columns:
                print(f"- {col} 고유값 수: {df[col].nunique()}")
                if df[col].nunique() < 20: # 고유값이 적으면 직접 출력
                    print(f"  고유값: {df[col].unique()}")
            else:
                print(f"- 컬럼 '{col}'을(를) 찾을 수 없습니다.")
        
    except FileNotFoundError:
        print(f"**오류:** '{data_path}' 파일을 찾을 수 없습니다. `wafer` 폴더에 'LSWMD.pkl' 파일을 다운로드했는지 확인해주세요.")
    except Exception as e:
        print(f"데이터 로드 또는 확인 중 오류 발생: {e}")

if __name__ == '__main__':
    check_wafer_data()
