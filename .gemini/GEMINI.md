# Gemini 메모리 - 사용자 요구사항

## 주요 설정

- 사용자는 한국어로 답변받는 것을 선호합니다.
- 데이터 시각화 시 seaborn의 스타일 설정을 사용하지 않습니다.
- matplotlib 기반의 시각화를 할 때는 운영체제 기본 폰트 설정을 합니다.
- 기존에 가상환경 폴더가 있다면 새로 가상환경을 만들지 않습니다. 가상환경은 .venv로 생성합니다.
- 답변은 한국어로만 작성할 것, 코드 주석과 설명도 한국어로만 할 것

## 개발 환경

- 작업 경로: `c:\FCICB5`
- Python 가상환경: `c:\FCICB5\venv` (기존 설정)
- Gemini CLI 버전: 0.19.4 (전역 설치)

## 프로젝트 구성

- `penguin_eda.ipynb` - 펭귄 데이터 탐색적 분석 (한글 폰트: Malgun Gothic, seaborn 스타일 없음)
- `gugudan.py` - 구구단 출력 프로그램
- `.venv/` - Python 가상환경 (pandas, numpy, matplotlib, seaborn, scikit-learn, jupyter 설치됨)
