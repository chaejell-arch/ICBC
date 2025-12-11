
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os

def create_eda_report():
    """
    국가별 자료수집 현황 데이터셋에 대한 EDA를 수행하고,
    분석 과정과 결과를 담은 마크다운 보고서를 생성합니다.
    """
    # --- 0. 기본 설정 ---
    current_working_directory = os.getcwd() # 현재 작업 디렉터리 가져오기
    output_dir = os.path.join(current_working_directory, "Logistics")
    image_dir = os.path.join(output_dir, "images")


    report_parts = []
    report_path = os.path.join(output_dir, "eda_report.md")
    data_path = os.path.join(output_dir, "국가별_자료수집_현황.xlsx")

    report_parts.append("# 국가별 자료수집 현황 EDA 보고서")
    report_parts.append("이 보고서는 국립중앙도서관의 국가별 자료수집 현황 데이터를 분석하고 시각화한 결과를 담고 있습니다.")

    # --- 1. 데이터 로드 ---
    report_parts.append("## 1. 데이터 로드 및 기본 정보 확인")
    try:
        # 엑셀 파일의 두 번째 줄부터 데이터가 시작되므로 header=1로 설정
        df = pd.read_excel(data_path, header=1)
        report_parts.append("### 데이터 샘플 (상위 5개)")
        report_parts.append(df.head().to_markdown(index=False))
    except FileNotFoundError:
        report_parts.append(f"**오류:** '{data_path}' 파일을 찾을 수 없습니다. `Logistics` 폴더에 데이터 파일을 다운로드했는지 확인해주세요.")
        # 오류 발생 시 보고서 파일 생성 후 종료
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("".join(report_parts))
        print(f"보고서가 '{report_path}'에 일부 저장되었습니다. 데이터 파일을 확인해주세요.")
        return

    report_parts.append("### 데이터 기본 정보")
    # df.info()는 파일 출력으로 리디렉션하기 어려우므로, 주요 정보만 요약
    info_summary = pd.DataFrame({
        'Column': df.columns,
        'Non-Null Count': df.count().values,
        'Dtype': df.dtypes.values
    })
    report_parts.append(info_summary.to_markdown(index=False))
    
    report_parts.append("### 데이터 요약 통계")
    report_parts.append(df.describe(include='all').to_markdown())

    # --- 2. 데이터 전처리 ---
    report_parts.append("## 2. 데이터 전처리")
    report_parts.append("데이터 분석에 용이하도록 '발행년' 컬럼의 데이터 타입을 숫자로 변환하고, 결측치를 처리합니다.")
    # check_excel_columns.py 에서 확인된 8개 컬럼과 유추한 의미를 바탕으로 컬럼명 재정의
    df.columns = ['국가/지역', '총물동량', '내수물동량', '수출물동량', '수입물동량', '수출_증감율', '수입_증감율', '단위']
    
    # '국가/지역' 컬럼을 문자열로 변환하고, 첫 번째 행 ('총계')은 제거하지 않습니다.
    # '기간' 컬럼은 더 이상 존재하지 않으므로, '국가/지역'을 기준으로 분석을 진행합니다.
    df['국가/지역'] = df['국가/지역'].astype(str)

    # 물동량 및 증감율 관련 컬럼들을 숫자형으로 변환 (오류 발생 시 NaN으로 처리)
    numeric_cols = ['총물동량', '내수물동량', '수출물동량', '수입물동량', '수출_증감율', '수입_증감율']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    report_parts.append("물동량 및 증감율 관련 컬럼들을 숫자형으로 변환하고 결측치를 처리했습니다.")
    
    # 분석에 필요한 결측치 제거
    df.dropna(subset=['국가/지역', '총물동량', '수출물동량', '수입물동량'], inplace=True)


    # --- 3. 데이터 분석 및 시각화 ---
    report_parts.append("## 3. 데이터 분석 및 시각화")

    # 시각화 함수 정의
    def save_plot(title, filename, has_table=False, table_df=None):
        plt.title(title, fontsize=16)
        plt.grid(True, axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        path = os.path.join(image_dir, filename)
        plt.savefig(path)
        plt.close()
        report_parts.append(f"![{title}]({os.path.join('images', filename)})")
        if has_table and table_df is not None:
            report_parts.append("\n**해당 시각화에 대한 요약표:**")
            report_parts.append(table_df.to_markdown(index=False))

    # '총계' 행을 식별합니다. 일반적으로 데이터의 첫 번째 행에 위치하며, '국가/지역' 컬럼값이 '총계'일 것입니다.
    df_total = df[df['국가/지역'].str.contains('총계|합계', na=False)].copy()
    if df_total.empty and not df.empty:
        df_total = df.iloc[[0]].copy() # '총계' 또는 '합계'가 명시적으로 없으면 첫 번째 행을 총계로 가정

    df_countries = df[~df['국가/지역'].str.contains('총계|합계', na=False)].copy()
    if df_countries.empty and not df.empty:
        df_total = df.iloc[[0]].copy()
        df_countries = df.iloc[1:].copy()
    
    # 요청된 특정 국가/지역 필터링
    target_countries = ['미국', '한국', '중국', '일본', '러시아']
    df_target_countries = df_countries[df_countries['국가/지역'].isin(target_countries)].copy()

    if df_target_countries.empty:
        report_parts.append("경고: 요청하신 국가(미국, 한국, 중국, 일본, 러시아)에 해당하는 데이터가 충분하지 않습니다. 일반적인 국가별 분석을 진행합니다.")
        df_target_countries = df_countries # 요청 국가 데이터가 없으면 전체 국가로 분석
        is_target_country_analysis = False
    else:
        is_target_country_analysis = True

    analysis_scope = "요청 국가 (미국, 한국, 중국, 일본, 러시아)" if is_target_country_analysis else "전체 국가"

    # 1. 특정 국가/지역 총물동량 (막대 그래프)
    report_parts.append(f"### 3.1. {analysis_scope} 총물동량")
    if not df_target_countries.empty:
        total_volume_by_country = df_target_countries[['국가/지역', '총물동량']].sort_values(by='총물동량', ascending=False)
        plt.figure(figsize=(12, 8))
        plt.barh(total_volume_by_country['국가/지역'], total_volume_by_country['총물동량'], color='skyblue')
        plt.xlabel('총물동량', fontsize=12)
        plt.ylabel('국가/지역', fontsize=12)
        save_plot(f"{analysis_scope} 총물동량", "plot_1_target_total_volume.png", True, total_volume_by_country)
    else:
        report_parts.append(f"{analysis_scope}의 총물동량 데이터를 찾을 수 없습니다.")

    # 2. 특정 국가/지역 수출 물동량
    report_parts.append(f"### 3.2. {analysis_scope} 수출 물동량")
    if not df_target_countries.empty:
        export_volume_by_country = df_target_countries[['국가/지역', '수출물동량']].sort_values(by='수출물동량', ascending=False)
        plt.figure(figsize=(12, 8))
        plt.barh(export_volume_by_country['국가/지역'], export_volume_by_country['수출물동량'], color='lightgreen')
        plt.xlabel('수출 물동량', fontsize=12)
        plt.ylabel('국가/지역', fontsize=12)
        save_plot(f"{analysis_scope} 수출 물동량", "plot_2_target_export_volume.png", True, export_volume_by_country)
    else:
        report_parts.append(f"{analysis_scope}의 수출 물동량 데이터를 찾을 수 없습니다.")

    # 3. 특정 국가/지역 수입 물동량
    report_parts.append(f"### 3.3. {analysis_scope} 수입 물동량")
    if not df_target_countries.empty:
        import_volume_by_country = df_target_countries[['국가/지역', '수입물동량']].sort_values(by='수입물동량', ascending=False)
        plt.figure(figsize=(12, 8))
        plt.barh(import_volume_by_country['국가/지역'], import_volume_by_country['수입물동량'], color='salmon')
        plt.xlabel('수입 물동량', fontsize=12)
        plt.ylabel('국가/지역', fontsize=12)
        save_plot(f"{analysis_scope} 수입 물동량", "plot_3_target_import_volume.png", True, import_volume_by_country)
    else:
        report_parts.append(f"{analysis_scope}의 수입 물동량 데이터를 찾을 수 없습니다.")

    # 4. 전체 총물동량 대비 수출/수입 물동량 비중 (총계 행 사용)
    if not df_total.empty:
        report_parts.append("### 3.4. 전체 총물동량 대비 수출/수입 물동량 비중")
        total_export = df_total['수출물동량'].sum()
        total_import = df_total['수입물동량'].sum()
        labels = ['수출 물동량', '수입 물동량']
        sizes = [total_export, total_import]
        colors = ['lightgreen', 'salmon']
        
        if sum(sizes) > 0: # 0으로 나누는 오류 방지
            plt.figure(figsize=(8, 8))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
            save_plot("전체 총물동량 대비 수출/수입 물동량 비중", "plot_4_export_import_ratio_pie.png", True, pd.DataFrame({'구분': labels, '물동량': sizes}))
        else:
            report_parts.append("수출입 물동량 데이터가 없어 비중을 계산할 수 없습니다.")
    else:
        report_parts.append("총계 데이터를 찾을 수 없어 수출/수입 물동량 비중을 계산할 수 없습니다.")

    # 5. 특정 국가/지역별 수출입 물동량 비교 (누적 막대 그래프)
    report_parts.append(f"### 3.5. {analysis_scope} 수출입 물동량 비교")
    if not df_target_countries.empty:
        export_import_by_country = df_target_countries[['국가/지역', '수출물동량', '수입물동량']].set_index('국가/지역')
        plt.figure(figsize=(14, 8))
        export_import_by_country.plot(kind='bar', stacked=True, figsize=(14, 8), color=['lightgreen', 'salmon'])
        plt.xlabel('국가/지역', fontsize=12)
        plt.ylabel('물동량', fontsize=12)
        save_plot(f"{analysis_scope} 수출입 물동량 비교", "plot_5_target_export_import_stacked.png", True, export_import_by_country.reset_index())
    else:
        report_parts.append(f"{analysis_scope}의 수출입 물동량 데이터를 찾을 수 없습니다.")

    # 6. 총물동량과 수출 물동량의 상관관계
    report_parts.append("### 3.6. 총물동량과 수출 물동량의 상관관계")
    if not df_countries.empty:
        plt.figure(figsize=(10, 8))
        plt.scatter(df_countries['총물동량'], df_countries['수출물동량'], alpha=0.6, color='darkblue')
        plt.xlabel('총물동량', fontsize=12)
        plt.ylabel('수출 물동량', fontsize=12)
        save_plot("총물동량과 수출 물동량의 상관관계", "plot_6_total_export_correlation.png")
        report_parts.append(f"총물동량과 수출 물동량의 상관계수: {df_countries['총물동량'].corr(df_countries['수출물동량']):.2f}")
    else:
        report_parts.append("총물동량과 수출 물동량 상관관계 분석을 위한 데이터가 부족합니다.")

    # 7. 총물동량과 수입 물동량의 상관관계
    report_parts.append("### 3.7. 총물동량과 수입 물동량의 상관관계")
    if not df_countries.empty:
        plt.figure(figsize=(10, 8))
        plt.scatter(df_countries['총물동량'], df_countries['수입물동량'], alpha=0.6, color='darkgreen')
        plt.xlabel('총물동량', fontsize=12)
        plt.ylabel('수입 물동량', fontsize=12)
        save_plot("총물동량과 수입 물동량의 상관관계", "plot_7_total_import_correlation.png")
        report_parts.append(f"총물동량과 수입 물동량의 상관계수: {df_countries['총물동량'].corr(df_countries['수입물동량']):.2f}")
    else:
        report_parts.append("총물동량과 수입 물동량 상관관계 분석을 위한 데이터가 부족합니다.")

    # 8. 특정 국가/지역 내수물동량
    report_parts.append(f"### 3.8. {analysis_scope} 내수물동량")
    if not df_target_countries.empty:
        domestic_volume_by_country = df_target_countries[['국가/지역', '내수물동량']].sort_values(by='내수물동량', ascending=False)
        plt.figure(figsize=(12, 8))
        plt.barh(domestic_volume_by_country['국가/지역'], domestic_volume_by_country['내수물동량'], color='orange')
        plt.xlabel('내수 물동량', fontsize=12)
        plt.ylabel('국가/지역', fontsize=12)
        save_plot(f"{analysis_scope} 내수물동량", "plot_8_target_domestic_volume.png", True, domestic_volume_by_country)
    else:
        report_parts.append(f"{analysis_scope}의 내수물동량 데이터를 찾을 수 없습니다.")
    
    # 9. 특정 국가/지역 수출 증감율
    report_parts.append(f"### 3.9. {analysis_scope} 수출 증감율")
    if not df_target_countries.empty:
        export_growth_by_country = df_target_countries[['국가/지역', '수출_증감율']].sort_values(by='수출_증감율', ascending=False)
        plt.figure(figsize=(12, 8))
        plt.barh(export_growth_by_country['국가/지역'], export_growth_by_country['수출_증감율'], color='blueviolet')
        plt.xlabel('수출 증감율', fontsize=12)
        plt.ylabel('국가/지역', fontsize=12)
        save_plot(f"{analysis_scope} 수출 증감율", "plot_9_target_export_growth.png", True, export_growth_by_country)
    else:
        report_parts.append(f"{analysis_scope}의 수출 증감율 데이터를 찾을 수 없습니다.")

    # 10. 특정 국가/지역 수입 증감율
    report_parts.append(f"### 3.10. {analysis_scope} 수입 증감율")
    if not df_target_countries.empty:
        import_growth_by_country = df_target_countries[['국가/지역', '수입_증감율']].sort_values(by='수입_증감율', ascending=False)
        plt.figure(figsize=(12, 8))
        plt.barh(import_growth_by_country['국가/지역'], import_growth_by_country['수입_증감율'], color='mediumpurple')
        plt.xlabel('수입 증감율', fontsize=12)
        plt.ylabel('국가/지역', fontsize=12)
        save_plot(f"{analysis_scope} 수입 증감율", "plot_10_target_import_growth.png", True, import_growth_by_country)
    else:
        report_parts.append(f"{analysis_scope}의 수입 증감율 데이터를 찾을 수 없습니다.")

    report_parts.append("### 3.11. 총계 데이터 요약")
    if not df_total.empty:
        report_parts.append("전체 물동량 합계 요약:")
        report_parts.append(df_total[numeric_cols].sum().to_frame(name='총계').to_markdown())
    else:
        report_parts.append("총계 데이터를 찾을 수 없습니다.")


    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("".join(report_parts))
    
    print(f"EDA 보고서 및 관련 이미지 파일들이 '{output_dir}' 폴더에 성공적으로 생성되었습니다.")
    print(f"최종 보고서: '{report_path}'")

if __name__ == '__main__':
    create_eda_report()
