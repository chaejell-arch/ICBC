# Streamlit 대시보드 GitHub 배포 및 Streamlit Cloud 연동 가이드

이 가이드는 현재 개발된 Streamlit 대시보드를 GitHub에 업로드하고, Streamlit Cloud를 통해 배포하는 방법을 설명합니다.

## 6.1 GitHub에 프로젝트 업로드

1.  **Git 초기화 및 파일 추가**: 프로젝트 폴더(`C:\FCICB5`)에서 터미널을 열고 다음 명령어를 실행하여 Git을 초기화하고 모든 파일을 스테이징합니다.
    ```bash
    git init
    git add .
    ```
2.  **첫 커밋 생성**: 변경사항을 로컬 저장소에 커밋합니다.
    ```bash
    git commit -m "feat: Initial commit of Online Retail EDA Dashboard"
    ```
3.  **GitHub 리포지토리 생성**: GitHub 웹사이트(github.com)에 접속하여 새 리포지토리를 생성합니다. (예: `online-retail-dashboard`) 이 때, `README.md`, `.gitignore` 등은 추가하지 마세요.
4.  **원격 리포지토리 연결**: GitHub에서 생성된 리포지토리의 URL을 복사하여 로컬 저장소와 연결합니다.
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    git branch -M main
    ```
    (`YOUR_USERNAME`과 `YOUR_REPOSITORY_NAME`을 본인의 GitHub 사용자명과 리포지토리 이름으로 대체하세요.)
5.  **GitHub에 푸시**: 로컬 코드를 GitHub 리포지토리로 푸시합니다.
    ```bash
    git push -u origin main
    ```

## 6.2 `requirements.txt` 파일 생성

Streamlit Cloud는 애플리케이션 실행에 필요한 모든 Python 라이브러리를 `requirements.txt` 파일에서 읽어 설치합니다. 따라서 이 파일이 반드시 필요합니다.

1.  **가상 환경 활성화**: 현재 Streamlit 및 필요한 라이브러리들이 설치된 가상 환경을 활성화합니다.
    ```bash
    # Windows PowerShell
    .venv\Scripts\Activate.ps1
    # 또는 Windows Command Prompt (cmd)
    .venv\Scripts\activate
    ```
2.  **`requirements.txt` 생성**: 가상 환경이 활성화된 상태에서 다음 명령어를 실행하여 현재 환경의 모든 패키지 목록을 `requirements.txt` 파일로 내보냅니다.
    ```bash
    pip freeze > requirements.txt
    ```
    *주의*: 이 파일은 프로젝트의 루트(`C:\FCICB5`)에 생성되어야 합니다.
3.  **`requirements.txt`를 GitHub에 푸시**:
    ```bash
    git add requirements.txt
    git commit -m "feat: Add requirements.txt for deployment"
    git push origin main
    ```

## 6.3 Streamlit Cloud를 통해 배포

1.  **Streamlit Cloud 접속**: 웹 브라우저에서 [share.streamlit.io](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
2.  **새 앱 배포**: 로그인 후, 오른쪽 상단의 "New app" 버튼을 클릭합니다.
3.  **리포지토리 선택**:
    *   **Repository**: GitHub에서 생성한 리포지토리(예: `YOUR_USERNAME/YOUR_REPOSITORY_NAME`)를 선택합니다.
    *   **Branch**: `main` 브랜치를 선택합니다.
    *   **Main file path**: Streamlit 애플리케이션 파일의 경로를 입력합니다. 이 프로젝트의 경우 `Online Retail/dashboard.py` 입니다.
4.  **고급 설정 (선택 사항)**:
    *   "Advanced settings"를 클릭하여 Python 버전을 지정하거나, 환경 변수 등을 설정할 수 있습니다. 일반적으로는 기본 설정을 사용해도 무방합니다.
5.  **배포**: "Deploy!" 버튼을 클릭합니다.
6.  **앱 확인**: Streamlit Cloud가 의존성 설치 및 앱 빌드를 완료하면, 대시보드가 자동으로 실행되고 웹 링크가 제공됩니다. 이 링크를 통해 어디서든 대시보드에 접속할 수 있습니다.
