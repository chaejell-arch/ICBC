
import pandas as pd
import os

data_path = os.path.join("Logistics", "국가별_자료수집_현황.xlsx")

print(f"'{data_path}' 파일의 시트 이름 및 컬럼명을 확인합니다.")

try:
    xls = pd.ExcelFile(data_path)
    sheet_names = xls.sheet_names
    print(f"\n시트 이름: {sheet_names}")

    # 첫 번째 시트의 첫 두 행을 읽어서 실제 데이터의 컬럼 개수와 내용을 확인합니다.
    df_preview = pd.read_excel(data_path, sheet_name=sheet_names[0], header=1, nrows=2)
    print("\n첫 번째 시트의 헤더 및 첫 번째 데이터 행 (컬럼 개수 및 내용 확인용):")
    print(df_preview.to_markdown(index=False))

    print(f"\n확인된 컬럼 개수: {len(df_preview.columns)}")
    print("확인된 컬럼 목록:")
    for i, col in enumerate(df_preview.columns):
        print(f"Index {i}: {col}")

except FileNotFoundError:
    print(f"오류: '{data_path}' 파일을 찾을 수 없습니다. 파일 경로와 이름을 다시 확인해주세요.")
except Exception as e:
    print(f"엑셀 파일 읽기 중 오류 발생: {e}")

