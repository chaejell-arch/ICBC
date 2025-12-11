# Gemini CLI 사용 안내

이 파일은 `gemini` CLI 도구를 로컬 개발환경에서 바로 사용할 수 있도록 설치, 확인, VS Code 연동 방법을 정리합니다.

---

## 1) 설치 확인

이미 전역 설치된 경우 다음 명령으로 버전을 확인하세요:

```powershell
gemini --version
```

또는 설치 경로에서 직접 실행할 수도 있습니다:

```powershell
& 'C:\Users\User\AppData\Roaming\npm\gemini.cmd' --version
```

설치가 되어 있지 않다면 다음으로 설치하세요:

```powershell
npm install -g @google/gemini-cli
```

> 참고: PowerShell에서 전역 npm 스크립트(`*.ps1`)가 차단될 수 있습니다. 이 경우 아래 실행 정책을 사용자 범위에서 설정하면 `gemini`를 영구적으로 사용할 수 있습니다:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

---

## 2) 기본 사용법

### 대화형 모드 (권장)
```powershell
gemini
```
대화형 모드에서는 다음 명령들을 사용할 수 있습니다:
- `/memory show` — 저장된 메모리 표시
- `/memory add <content>` — 메모리에 내용 추가
- `/exit` 또는 `quit` — 대화형 모드 종료

### 도움말 보기
```powershell
gemini --help
```

### 버전 확인
```powershell
gemini --version
```

### 한 번만 실행 (비대화형)
```powershell
gemini "당신의 질문"
```

### 대화형 모드로 진입하며 프롬프트 실행
```powershell
gemini -i "당신의 질문"
```

### YOLO 모드 (자동 승인)
```powershell
gemini --yolo "당신의 질문"
```

---

## 3) 메모리 시스템

`gemini`는 메모리 기능으로 사용자의 요구사항, 설정, 선호도를 저장할 수 있습니다.

### 메모리에 저장된 현재 설정
- 사용자는 한국어로 답변받는 것을 선호합니다.
- 데이터 시각화 시 seaborn의 스타일 설정을 사용하지 않습니다.
- matplotlib 기반의 시각화를 할 때는 운영체제 기본 폰트 설정을 합니다.
- 기존에 가상환경 폴더가 있다면 새로 가상환경을 만들지 않습니다. 가상환경은 .venv로 생성합니다.
- 답변은 한국어로만 작성할 것, 코드 주석과 설명도 한국어로만 할 것

### 메모리 확인
```powershell
gemini
> /memory show
```

### 메모리 추가
```powershell
gemini
> /memory add 새로운 요구사항
```

---

## 4) VS Code에서 바로 실행하기

VS Code Task 파일(`.vscode/tasks.json`)의 Task 목록:
- `Gemini: Version` — `gemini --version`
- `Gemini: Help` — `gemini --help`
- `Gemini: Run (with args)` — 실행 인자를 입력받아 `gemini <args>` 실행

VS Code에서 실행 방법:
- `Terminal` → `Run Task...` → 원하는 `Gemini: ...` Task 선택
- 또는 `Ctrl+Shift+P` → `Tasks: Run Task` → 선택

---

## 5) 자주 사용되는 명령

### 세션 관리
```powershell
gemini --list-sessions          # 이전 세션 목록 보기
gemini --resume latest          # 최근 세션 재개
gemini --delete-session 1       # 세션 1 삭제
```

### 확장 관리
```powershell
gemini extensions --list        # 설치된 확장 목록
gemini -l                       # 사용 가능한 확장 나열
```

### MCP 서버 관리
```powershell
gemini mcp --help               # MCP 도움말
```

---

## 6) 문제 해결

### PowerShell에서 `gemini` 명령을 인식하지 못할 경우
1. npm 전역 경로가 PATH에 포함되어 있는지 확인:
   ```powershell
   $env:Path -split ';' | Select-String "npm"
   ```

2. 실행 정책 문제인 경우:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
   ```

3. PowerShell을 재시작하거나 새 터미널 세션 열기

### 메모리가 저장되지 않을 경우
- `c:\FCICB5\.gemini\GEMINI.md` 파일이 존재하는지 확인
- 대화형 모드에서 `/memory show`로 확인
- 필요시 `/memory add` 명령으로 추가

---

## 7) 유용한 팁

- **긴 프롬프트**: 파일에서 읽어 stdin으로 전달:
  ```powershell
  Get-Content prompt.txt | gemini
  ```

- **디버그 모드**:
  ```powershell
  gemini -d "질문"
  ```

- **JSON 출력 형식**:
  ```powershell
  gemini -o json "질문"
  ```

---

더 궁금한 점이 있으면 `gemini --help`를 참고하세요.
