import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import glob

def main():
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data', 'raw_data', 'train')
    output_dir = script_dir
    report_path = os.path.join(output_dir, 'eda_report.md')
    images_dir = output_dir # 이미지도 같은 폴더에 저장

    # 데이터 파일 목록 가져오기
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not all_files:
        print(f"오류: {data_dir} 에서 CSV 파일을 찾을 수 없습니다.")
        return

    # 모든 CSV 파일을 읽어 하나의 데이터프레임으로 병합
    df_list = []
    for f in all_files:
        try:
            temp_df = pd.read_csv(f)
            # 파일명에서 사이클과 타입 정보 추출
            filename = os.path.basename(f)
            cycle, type = filename.split('.')[0].split('_')
            temp_df['Cycle'] = cycle
            temp_df['Type'] = type
            df_list.append(temp_df)
        except Exception as e:
            print(f"파일 읽기 오류 {f}: {e}")
            continue
    
    if not df_list:
        print("오류: CSV 파일들을 읽지 못했습니다.")
        return

    df = pd.concat(df_list, ignore_index=True)

    # 데이터 타입 변환 및 정리
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.rename(columns={'Tavg': 'Temperature'})
    
    # 주요 컬럼 선택
    main_cols = ['DateTime', 'Voltage', 'Current', 'Temperature', 'Cycle', 'Type']
    df = df[main_cols]

    # 마크다운 보고서 생성 시작
    report = ["# 배터리 충방전 데이터 EDA 보고서"]
    report.append("\n_이 보고서는 `data/raw_data/train` 폴더의 모든 CSV 파일을 통합하여 생성되었습니다._")

    # 1. 데이터 개요
    report.append("## 1. 데이터 개요")
    report.append("### 데이터 샘플 (상위 5개)")
    report.append("```\n" + df.head().to_string() + "\n```")
    report.append("\n### 데이터 정보")
    from io import StringIO
    buffer = StringIO()
    df.info(buf=buffer)
    report.append("```\n" + buffer.getvalue() + "\n```")
    report.append("\n### 기술 통계")
    report.append("```\n" + df.describe().to_string() + "\n```")
    report.append("\n### 결측치 확인")
    report.append("```\n" + df.isnull().sum().to_string() + "\n```")

    # 2. 데이터 시각화
    report.append("\n## 2. 데이터 시각화")

    def save_plot(fig, filename):
        path = os.path.join(images_dir, filename)
        fig.savefig(path, bbox_inches='tight')
        plt.close(fig)
        return f"![{filename.split('.')[0]}](./{filename})"

    # 시각화 1: 충전/방전(Type) 분포
    type_counts = df['Type'].value_counts()
    fig, ax = plt.subplots()
    type_counts.plot(kind='bar', ax=ax, rot=0)
    ax.set_title('충전(chg) / 방전(dchg) 데이터 분포')
    ax.set_xlabel('타입')
    ax.set_ylabel('데이터 포인트 수')
    report.append("\n### 2.1. 충전/방전 데이터 분포")
    report.append("전체 데이터에서 충전과 방전 데이터의 비율을 보여줍니다.")
    report.append(save_plot(fig, 'type_distribution.png'))
    report.append("\n#### 교차표")
    report.append("```\n" + type_counts.to_frame().to_string() + "\n```")

    # 시각화 2: 전압(Voltage) 분포 (충전/방전 별)
    fig, ax = plt.subplots()
    df[df['Type'] == 'chg']['Voltage'].hist(ax=ax, bins=50, alpha=0.7, label='충전')
    df[df['Type'] == 'dchg']['Voltage'].hist(ax=ax, bins=50, alpha=0.7, label='방전')
    ax.set_title('충전/방전 시 전압 분포')
    ax.set_xlabel('전압 (V)')
    ax.set_ylabel('빈도')
    ax.legend()
    report.append("\n### 2.2. 전압 분포")
    report.append("충전과 방전 시의 전압 분포를 비교합니다. 충전 시 높은 전압 대역에, 방전 시 낮은 전압 대역에 데이터가 분포하는 경향을 보입니다.")
    report.append(save_plot(fig, 'voltage_distribution_by_type.png'))

    # 시각화 3: 전류(Current) 분포 (충전/방전 별)
    fig, ax = plt.subplots()
    df[df['Type'] == 'chg']['Current'].hist(ax=ax, bins=50, alpha=0.7, label='충전')
    df[df['Type'] == 'dchg']['Current'].hist(ax=ax, bins=50, alpha=0.7, label='방전')
    ax.set_title('충전/방전 시 전류 분포')
    ax.set_xlabel('전류 (A)')
    ax.set_ylabel('빈도')
    ax.legend()
    report.append("\n### 2.3. 전류 분포")
    report.append("충전 전류는 양수 값을, 방전 전류는 음수 값을 가집니다. 각 과정에서 특정 전류 값에 데이터가 집중된 것을 볼 수 있습니다.")
    report.append(save_plot(fig, 'current_distribution_by_type.png'))

    # 시각화 4: 온도(Temperature) 분포
    fig, ax = plt.subplots()
    df['Temperature'].hist(ax=ax, bins=50, color='salmon')
    ax.set_title('배터리 평균 온도 분포')
    ax.set_xlabel('온도 (°C)')
    ax.set_ylabel('빈도')
    report.append("\n### 2.4. 온도 분포")
    report.append("측정된 배터리의 평균 온도(Tavg) 분포를 보여줍니다.")
    report.append(save_plot(fig, 'temperature_distribution.png'))

    # 시각화 5: 특정 사이클(1000)의 시간에 따른 전압/전류/온도
    cycle_1000_df = df[df['Cycle'] == '1000'].sort_values('DateTime')
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    cycle_1000_df.plot(x='DateTime', y='Voltage', ax=axes[0], title='Cycle 1000: 전압')
    cycle_1000_df.plot(x='DateTime', y='Current', ax=axes[1], title='Cycle 1000: 전류')
    cycle_1000_df.plot(x='DateTime', y='Temperature', ax=axes[2], title='Cycle 1000: 온도')
    plt.xlabel('시간')
    report.append("\n### 2.5. 특정 사이클(1000)의 시계열 데이터")
    report.append("첫 번째 사이클(1000)의 시간에 따른 전압, 전류, 온도의 변화를 보여줍니다. 충/방전 과정의 변화 패턴을 확인할 수 있습니다.")
    report.append(save_plot(fig, 'cycle_1000_timeseries.png'))

    # 시각화 6: 사이클 별 평균 전압
    cycle_voltage = df.groupby(['Cycle', 'Type'])['Voltage'].mean().unstack()
    fig, ax = plt.subplots(figsize=(12, 6))
    cycle_voltage.plot(kind='bar', ax=ax, rot=90)
    ax.set_title('사이클 별 평균 전압 (충전/방전)')
    ax.set_xlabel('사이클')
    ax.set_ylabel('평균 전압 (V)')
    report.append("\n### 2.6. 사이클 별 평균 전압")
    report.append("각 사이클의 충전, 방전 과정에서의 평균 전압을 막대 그래프로 비교합니다.")
    report.append(save_plot(fig, 'voltage_by_cycle.png'))
    report.append("\n#### 피벗 테이블")
    report.append("```\n" + cycle_voltage.head().to_string() + "\n```")

    # 시각화 7: 사이클 별 평균 온도
    cycle_temp = df.groupby('Cycle')['Temperature'].mean()
    fig, ax = plt.subplots(figsize=(12, 6))
    cycle_temp.plot(kind='line', ax=ax, style='-o')
    ax.set_title('사이클 별 평균 온도 변화')
    ax.set_xlabel('사이클')
    ax.set_ylabel('평균 온도 (°C)')
    report.append("\n### 2.7. 사이클 별 평균 온도")
    report.append("사이클이 진행됨에 따른 평균 온도의 변화 추이를 보여줍니다.")
    report.append(save_plot(fig, 'temperature_by_cycle.png'))

    # 시각화 8: 전압과 전류의 관계
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df['Voltage'], df['Current'], alpha=0.1)
    ax.set_title('전압과 전류의 관계 (산점도)')
    ax.set_xlabel('전압 (V)')
    ax.set_ylabel('전류 (A)')
    report.append("\n### 2.8. 전압-전류 관계")
    report.append("전압과 전류의 관계를 산점도를 통해 확인합니다. 충전/방전 시 특정 구간에 점들이 밀집되어 있습니다.")
    report.append(save_plot(fig, 'voltage_current_scatter.png'))

    # 시각화 9: 온도와 전압의 관계
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df['Temperature'], df['Voltage'], alpha=0.1)
    ax.set_title('온도와 전압의 관계 (산점도)')
    ax.set_xlabel('온도 (°C)')
    ax.set_ylabel('전압 (V)')
    report.append("\n### 2.9. 온도-전압 관계")
    report.append("온도와 전압의 관계를 산점도를 통해 확인합니다.")
    report.append(save_plot(fig, 'temperature_voltage_scatter.png'))
    
    # 시각화 10: 주요 변수 간 상관관계 히트맵
    corr = df[['Voltage', 'Current', 'Temperature']].corr()
    fig, ax = plt.subplots()
    cax = ax.matshow(corr, cmap='viridis')
    fig.colorbar(cax)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns)
    ax.set_yticklabels(corr.columns)
    ax.set_title('주요 변수 간 상관관계')
    report.append("\n### 2.10. 주요 변수 간 상관관계 히트맵")
    report.append("주요 수치형 변수인 전압, 전류, 온도 간의 상관관계를 히트맵으로 시각화합니다. 전류와 전압 사이에 약간의 음의 상관관계가 보입니다.")
    report.append(save_plot(fig, 'correlation_heatmap.png'))
    report.append("\n#### 상관계수 행렬")
    report.append("```\n" + corr.to_string() + "\n```")

    # 보고서 파일 작성
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))

    print(f"EDA 보고서가 '{report_path}'에 성공적으로 저장되었습니다.")

if __name__ == '__main__':
    main()