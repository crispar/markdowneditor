# Markdown Editor

PySide6를 기반으로 제작된 현대적인 마크다운(Markdown) 에디터입니다. 실시간 미리보기와 PDF 내보내기 기능을 지원하며, 직관적인 사용자 인터페이스를 제공합니다.

## 주요 기능

*   **실시간 미리보기 (Live Preview)**: 작성 중인 마크다운 내용을 오른쪽 창에서 실시간으로 확인할 수 있습니다.
*   **구문 강조 (Syntax Highlighting)**: 코드 블록에 대한 구문 강조 기능을 제공하여 가독성을 높였습니다 (Pygments 사용).
*   **PDF 내보내기**: 작성한 문서를 PDF 파일로 저장할 수 있습니다. 한국어 폰트('맑은 고딕', 'Noto Sans KR')를 지원하여 한글이 깨지지 않고 올바르게 출력됩니다.
*   **이미지 지원**:
    *   클립보드 이미지 붙여넣기 (`Ctrl+V`) 지원
    *   이미지 URL 붙여넣기 시 자동 다운로드 및 삽입
    *   로컬 이미지 파일 삽입 지원
*   **테마 지원**: 시스템 설정에 따라 다크 모드와 라이트 모드를 자동으로 전환합니다.
*   **편리한 툴바 및 단축키**: 굵게, 기울임, 제목, 코드, 링크, 목록 등 자주 사용하는 서식을 툴바 버튼이나 단축키로 쉽게 적용할 수 있습니다.

## 설치 및 실행 방법

### 요구 사항

*   Python 3.8 이상

### 설치

1. 가상 환경을 생성합니다. (빌드 스크립트가 `venv`라는 이름의 가상 환경을 사용하므로 이름을 `venv`로 설정하는 것을 권장합니다.)

    ```bash
    python -m venv venv
    ```

2. 가상 환경을 활성화합니다.

    *   **Windows**:
        ```bash
        venv\Scripts\activate
        ```
    *   **macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```

3. 필요한 라이브러리를 설치합니다.

    ```bash
    pip install -r requirements.txt
    ```

### 실행

다음 명령어로 에디터를 실행합니다.

```bash
python main.py
```

## 빌드 방법 (Windows)

단독 실행 파일(EXE)을 생성하려면 다음 명령어를 실행하세요. (PyInstaller가 설치되어 있어야 합니다.)

> **주의**: `build.bat` 스크립트는 `venv`라는 이름의 가상 환경이 존재한다고 가정합니다.

```bash
build.bat
```
또는
```bash
pyinstaller MarkdownEditor.spec
```

빌드가 완료되면 `dist/MarkdownEditor.exe` 파일이 생성됩니다.

## 사용 방법

### 단축키

*   **파일**
    *   새 파일: `Ctrl+N`
    *   열기: `Ctrl+O`
    *   저장: `Ctrl+S`
    *   다른 이름으로 저장: `Ctrl+Shift+S`
    *   PDF로 내보내기: `Ctrl+Shift+E`
    *   종료: `Ctrl+Q`
*   **편집**
    *   실행 취소: `Ctrl+Z`
    *   다시 실행: `Ctrl+Y` 또는 `Ctrl+Shift+Z`
    *   잘라내기: `Ctrl+X`
    *   복사: `Ctrl+C`
    *   붙여넣기: `Ctrl+V` (이미지 포함)
    *   전체 선택: `Ctrl+A`

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
