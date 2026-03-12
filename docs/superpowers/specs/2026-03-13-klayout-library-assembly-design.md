# KLayout 라이브러리 기반 어셈블리 시스템 설계

**날짜:** 2026-03-13
**상태:** 검토 완료

---

## 개요

각 팀원이 담당 블록을 `layouts/` 폴더에 `.oas`/`.gds` 파일로 작업하고, KLayout 시작 시 Python 매크로가 이 파일들을 KLayout 셀 라이브러리로 자동 등록한다. `master.oas`는 라이브러리 셀을 참조(reference)하는 플로어플랜 파일로, 통합 담당자가 직접 배치를 관리한다.

기존 `autoload.lym`의 geometry 복사(merge) 방식을 완전히 대체한다.

---

## 핵심 특성

- **셀 참조 기반:** master.oas는 geometry를 복사하지 않고 라이브러리 셀을 참조한다. 파일 크기가 작고, 동일 셀을 여러 번 인스턴스화하기 용이하다.
- **자동 동기화:** `git pull` 후 KLayout 재시작만 하면 모든 팀원 블록이 최신으로 갱신된다.
- **배선 추가 가능:** master.oas에서 메탈/배선을 직접 추가해도 라이브러리 갱신 시 충돌 없음.
- **레이어 일관성:** `tech/layers.lyp`로 전체 팀이 동일한 레이어 색상/스타일을 유지한다.

---

## 디렉토리 구조

```
klayout_test/
├── master.oas                      # 플로어플랜 (라이브러리 셀 참조, git 커밋)
├── layouts/
│   ├── member_A.oas                # 팀원별 블록 (Git LFS)
│   ├── member_B.oas
│   ├── member_C.gds                # .gds 형식도 지원
│   └── ...
├── tech/
│   ├── layers.lyp                  # 공통 레이어 속성
│   └── block_assignments.json      # 팀원별 좌표 범위 (선택적 참고용)
├── macros/
│   └── register_libraries.lym      # Python autorun 매크로 (기존 autoload.lym 대체)
└── docs/
    ├── README.md
    ├── usage.md
    └── coordinate_guide.md
```

**제거:** `macros/autoload.lym` — `register_libraries.lym`으로 완전 대체.

---

## Git 관리

### `.gitignore` 수정 필수

기존 `.gitignore`에서 `master.oas` 줄을 **제거**한다. 통합 담당자가 master.oas를 직접 커밋해야 하므로 gitignore에 포함되어 있으면 `git add master.oas`가 무시된다.

```diff
- master.oas
```

### `.gitattributes`

| 패턴 | 처리 방식 |
|------|-----------|
| `*.oas` | Git LFS (바이너리) |
| `*.gds` | Git LFS (바이너리) |
| `macros/*.lym` | 텍스트, LF |
| `tech/*.lyp` | 텍스트, LF |
| `docs/*.md` | 텍스트, LF |

### 브랜치 전략 (3단계)

```
feature/<이름>  →  main  →  release
```

| 브랜치 | 역할 | 커밋 규칙 |
|--------|------|----------|
| `feature/<이름>` | 팀원 개인 작업 | 자유롭게 push, `layouts/자기이름.oas`만 수정 |
| `main` | 팀 통합 작업 | PR 필수, Git LFS 정상 여부 확인 |
| `release` | 납품/tapeout 산출물 | 통합 담당자만, master.oas 포함 |

**팀원 PR 흐름:** `feature/<이름>` 브랜치에서 `layouts/자기이름.oas`를 수정하고 main으로 PR을 보낸다. PR 머지 전 Git LFS 포인터가 아닌 실제 바이너리가 push되었는지 확인한다 (Git LFS 미설치 시 포인터 파일만 올라가는 문제 방지).

**release 브랜치 보호 규칙:**
- 직접 push 불가 (PR 필수)
- 통합 담당자 리뷰 승인 필요
- master.oas DRC 클린 확인 후 머지

---

## 매크로 동작 (`register_libraries.lym`)

### 설정

```xml
<autorun>true</autorun>
<autorun-early>false</autorun-early>
<interpreter>python</interpreter>
```

`autorun-early: false`를 사용한다. `pya.Library.register()`는 KLayout 애플리케이션 커널이 완전히 초기화된 후에 안전하게 호출할 수 있다. autorun-early 단계에서는 GUI 및 일부 API가 준비되지 않을 수 있으므로 기존 `autoload.lym`과 동일하게 `false`로 설정한다.

KLayout의 startup 순서상 `autorun` 매크로는 기본 파일 오픈 전에 실행되므로 라이브러리 등록이 먼저 완료된다.

### 실행 순서

1. `os.path.realpath(__file__)` 기준으로 저장소 루트 탐색 (`.git` 디렉토리 탐색)
   - **주의:** KLayout 내장 Python에서 `__file__`은 매크로가 저장소 경로에서 직접 로드될 때만 신뢰할 수 있다. AppData 등 외부 경로에 복사된 경우 `find_repo_root`가 None을 반환하며 매크로가 즉시 종료된다.
2. `layouts/` 디렉토리 존재 확인 — 없으면 경고 로그 후 종료
3. `*.oas` 파일 탐색 후 `*.gds` 파일 탐색 (이름 충돌 시 `.oas` 우선)
4. 각 파일에 대해 `pya.Library` 생성 및 등록:
   - 라이브러리 이름 = 파일명(확장자 제외), 예: `"member_A"`
   - `lib.layout().read(filepath)` 로 파일 내용 로드
   - `lib.register()` 로 전역 등록
   - 읽기 실패 시 해당 파일 건너뜀, 나머지 계속
5. `tech/layers.lyp` 존재 시 통합 담당자에게 적용 안내 로그 출력

### layers.lyp 적용 방법

`register_libraries.lym`은 뷰를 직접 열지 않으므로 `view.load_layer_props()`를 직접 호출할 수 없다. 레이어 속성 적용은 다음 중 하나로 처리한다:

- **권장:** KLayout의 Technology 파일(`tech/*.lyt`)에 `layers.lyp` 경로를 등록한다. master.oas를 해당 기술로 연결하면 열릴 때 자동 적용된다.
- **대안:** 통합 담당자가 master.oas를 연 후 `Edit > Layer Properties > Load`로 수동 적용한다.

### 의사 코드

```python
import pya, os, glob

def find_repo_root(start):
    path = os.path.dirname(os.path.realpath(start))
    while path != os.path.dirname(path):
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
    return None

repo_root = find_repo_root(__file__)
if repo_root is None:
    pya.Logger.error("register_libraries: 저장소 루트를 찾을 수 없습니다. docs/usage.md를 확인하세요.")
    # 종료 (이후 코드 실행 안 함)
else:
    layouts_dir = os.path.join(repo_root, "layouts")

    if not os.path.isdir(layouts_dir):
        pya.Logger.warn("register_libraries: layouts/ 디렉토리가 없습니다.")
    else:
        # .oas 우선, .gds는 동일 이름이 없을 때만 등록
        oas_files = glob.glob(os.path.join(layouts_dir, "*.oas"))
        gds_files = glob.glob(os.path.join(layouts_dir, "*.gds"))
        oas_names = {os.path.splitext(os.path.basename(f))[0] for f in oas_files}

        all_files = sorted(oas_files) + sorted(
            f for f in gds_files
            if os.path.splitext(os.path.basename(f))[0] not in oas_names
        )

        for filepath in all_files:
            lib_name = os.path.splitext(os.path.basename(filepath))[0]
            # Git LFS 포인터 감지: 실제 .oas/.gds는 항상 200바이트 초과
            if os.path.getsize(filepath) < 200:
                pya.Logger.error(
                    f"register_libraries: {lib_name} — 파일이 너무 작습니다. "
                    "Git LFS가 설치되지 않았거나 git pull이 완료되지 않았을 수 있습니다."
                )
                continue
            try:
                lib = pya.Library()
                lib.name = lib_name
                lib.layout().read(filepath)
                lib.register()
                pya.Logger.info(f"register_libraries: 등록 완료 — {lib_name}")
            except Exception as e:
                pya.Logger.error(f"register_libraries: 등록 실패 — {lib_name}: {e}")
```

---

## 통합 담당자 워크플로우

### 초기 master.oas 생성 (1회)

1. KLayout 시작 → 라이브러리 자동 등록
2. 새 레이아웃 생성 (`File > New Layout`)
3. 셀 인스턴스 배치: `Edit > Cell > Instance...` 다이얼로그에서 라이브러리 선택 → 셀 선택 → 위치 지정 (KLayout 버전마다 메뉴 경로가 다를 수 있음)
4. 필요 시 동일 셀을 여러 번 인스턴스화 (배열, 미러, 회전 등)
5. 배선/메탈 직접 추가 가능 (라이브러리 갱신과 독립)
6. `master.oas`로 저장 → `git commit` → `release` 브랜치 PR

### 일상 동기화 (git pull 이후)

```
git pull
→ KLayout 시작
→ register_libraries.lym 자동 실행 → 최신 .oas/.gds로 라이브러리 갱신
→ master.oas 열기 → 배치 유지 + 셀 내용 최신화
```

### 새 팀원 블록 추가 시

```
팀원: layouts/member_D.oas 추가 → feature 브랜치 → main PR
통합 담당자: git pull → KLayout 재시작 → "member_D" 라이브러리 자동 등록
→ master.oas에서 셀 인스턴스 배치 → 저장 → release 브랜치 PR
```

---

## 오류 처리

| 상황 | 동작 |
|------|------|
| 저장소 루트 미발견 (`__file__` 경로 문제) | 에러 로그 출력 후 매크로 종료 |
| `layouts/` 디렉토리 없음 | 경고 로그 출력 후 매크로 종료 |
| `.oas`/`.gds` 파일 읽기 실패 | 해당 파일 건너뜀, 나머지 등록 계속, 에러 로그 출력 |
| Git LFS 포인터 파일 (파일 크기 < 200바이트) | 읽기 전 크기 체크로 감지 → "Git LFS 미설치 또는 pull 미완료" 안내 후 건너뜀 |
| `.oas`와 `.gds` 이름 충돌 | `.oas` 우선 등록, `.gds` 건너뜀 |

---

## 기존 시스템과의 차이

| 항목 | 기존 (autoload.lym) | 신규 (register_libraries.lym) |
|------|--------------------|-----------------------------|
| 방식 | geometry 복사(merge) | 셀 참조(reference) |
| 언어 | Ruby | Python |
| master.oas | 자동 생성, gitignore | 통합 담당자 관리, git 커밋 |
| 배치 제어 | 고정 좌표 또는 원점 | 통합 담당자 자유 배치 |
| 동기화 | 재시작 시 재병합 | 재시작 시 라이브러리 갱신 |
| 배선 추가 | 덮어씌워짐 | master.oas에서 유지됨 |
| 셀 재사용 | 불가 | 동일 셀 다중 인스턴스화 가능 |
| layers.lyp | 자동 적용 | Technology 파일 또는 수동 적용 |
