# Markdown Editor

PySide6 기반의 현대적인 마크다운 에디터. 실시간 미리보기, 구문 하이라이팅, PDF/HTML 내보내기를 지원합니다.

## 주요 기능

### 편집

- 실시간 프리뷰 및 스크롤 동기화
- 마크다운 구문 하이라이팅
- 찾기/바꾸기 (Ctrl+F / Ctrl+H)
- 자동 들여쓰기 (목록/인용)
- 포맷 토글 (Bold/Italic 적용-해제)
- 현재줄 하이라이트
- 단어/글자 수 표시

### 문서 관리

- 변경 감지 (제목에 `*` 표시)
- 자동저장 (30초)
- 최근 파일 목록
- 창 상태 저장/복원

### 보기

- 에디터/프리뷰/분할 뷰 전환
- 다크/라이트 테마
- 줌 인/아웃
- 전체화면 (F11)
- 아웃라인(목차) 패널

### 내보내기

- PDF (한국어 폰트 지원: 맑은 고딕, Noto Sans KR)
- HTML

### 이미지

- 클립보드 붙여넣기
- URL 자동 다운로드
- 드래그앤드롭

### 고급

- Mermaid 다이어그램
- 테이블/체크리스트 삽입
- 코드 블록 언어 선택

## 설치 및 실행

### 요구 사항

- Python 3.8+
- PySide6 6.2.4
- markdown >= 3.3.0
- Pygments >= 2.10.0

### 설치 및 실행

```bash
pip install -r requirements.txt
python main.py
```

## 빌드 방법 (Windows)

단독 실행 파일(EXE)을 생성하려면 `build.bat` 스크립트를 사용하거나 PyInstaller를 직접 실행할 수 있습니다.

### `build.bat` 사용 (권장)

이 스크립트는 프로젝트 루트에 `venv`라는 이름의 가상 환경이 존재한다고 가정합니다.

1. 가상 환경 생성 및 의존성 설치 (최초 1회):
   ```bash
   python -m venv venv
   call venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. 빌드 스크립트 실행:
   ```bash
   build.bat
   ```

### PyInstaller 직접 실행

PyInstaller가 설치된 환경에서 다음 명령어를 실행합니다.

```bash
pyinstaller --clean MarkdownEditor.spec
```

빌드가 완료되면 `dist/MarkdownEditor.exe` 파일이 생성됩니다.

## 단축키

### 파일

| 단축키 | 기능 |
|--------|------|
| Ctrl+N | 새 파일 |
| Ctrl+O | 열기 |
| Ctrl+S | 저장 |
| Ctrl+Shift+S | 다른 이름으로 저장 |
| Ctrl+Shift+E | PDF 내보내기 |
| Ctrl+Q | 종료 |

### 편집

| 단축키 | 기능 |
|--------|------|
| Ctrl+Z | 실행 취소 |
| Ctrl+Y | 다시 실행 |
| Ctrl+X | 잘라내기 |
| Ctrl+C | 복사 |
| Ctrl+V | 붙여넣기 |
| Ctrl+A | 전체 선택 |
| Ctrl+F | 찾기 |
| Ctrl+H | 바꾸기 |

### 서식

| 단축키 | 기능 |
|--------|------|
| Ctrl+B | 굵게 |
| Ctrl+I | 기울임 |
| Ctrl+Shift+X | 취소선 |
| Ctrl+1 | 제목 1 |
| Ctrl+2 | 제목 2 |
| Ctrl+3 | 제목 3 |
| Ctrl+` | 인라인 코드 |
| Ctrl+Shift+K | 코드 블록 |
| Ctrl+Shift+Q | 인용 |
| Ctrl+Shift+U | 글머리 목록 |
| Ctrl+Shift+L | 번호 목록 |
| Ctrl+Shift+T | 체크리스트 |
| Ctrl+K | 링크 |
| Ctrl+Shift+I | 이미지 |
| Ctrl+Shift+H | 수평선 |

### 보기

| 단축키 | 기능 |
|--------|------|
| Ctrl+Shift+1 | 에디터만 |
| Ctrl+Shift+2 | 프리뷰만 |
| Ctrl+Shift+3 | 분할 뷰 |
| Ctrl+Shift+O | 아웃라인 |
| Ctrl+= | 줌 인 |
| Ctrl+- | 줌 아웃 |
| Ctrl+0 | 줌 초기화 |
| F11 | 전체화면 |

## 프로젝트 구조

```
MarkdownEditor/
├── main.py
├── src/
│   ├── app.py
│   ├── main_window.py
│   ├── outline_widget.py
│   ├── editor/
│   │   ├── editor_widget.py
│   │   ├── toolbar.py
│   │   ├── find_replace.py
│   │   └── syntax_highlighter.py
│   ├── preview/
│   │   └── preview_widget.py
│   ├── export/
│   │   └── pdf_exporter.py
│   ├── styles/
│   │   └── theme.py
│   └── utils/
│       ├── image_handler.py
│       ├── markdown_converter.py
│       └── theme_detector.py
├── tests/
├── resources/
└── images/
```

## 테스트

```bash
pytest tests/ -v
```

현재 139+ 테스트가 포함되어 있습니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
