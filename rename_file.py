
import os

output_dir = "Logistics"
old_filename_pattern = "援蹂 ___.xlsx.xls" # dir 명령에서 확인된 깨진 파일명 패턴
new_filename = "국가별_자료수집_현황.xlsx"

old_filepath = os.path.join(output_dir, old_filename_pattern)
new_filepath = os.path.join(output_dir, new_filename)

try:
    if os.path.exists(old_filepath):
        os.rename(old_filepath, new_filepath)
        print(f"'{old_filepath}' 파일을 '{new_filepath}'으로 성공적으로 변경했습니다.")
    else:
        print(f"오류: '{old_filepath}' 파일을 찾을 수 없습니다. 파일명을 다시 확인해주세요.")
except Exception as e:
    print(f"파일명 변경 중 오류 발생: {e}")

