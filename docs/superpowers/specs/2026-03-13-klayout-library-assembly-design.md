# KLayout 라이브러리 기반 어셈블리 시스템 설계

**날짜:** 2026-03-13
**상태:** 확정

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
│   └── ...
├── tech/
│   ├── layers.lyp                  # 공통 레이어 속성
│   └── block_assignments.json      # 팀원별 좌표 범위 (선택적 참고용)
├── macros/
│   └── register_libraries.lym      # Python autorun-early 매크로 (기존 autoload.lym 대체)
└── docs/
    ├── README.md
    ├── usage.md
    └── coordinate_guide.md
```

**제거:** `macros/autoload.lym` — `register_libraries.lym`으로 완전 대체.

---

## Git 관리

### `.gitignore`
```
# master.oas는 이제 통합 담당자가 커밋하므로 gitignore에서 제거
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
| `feature/<이름>` | 팀원 개인 작업 | 자유롭게 push |
| `main` | 팀 통합 작업 | PR 필수, 자동 검증 통과 |
| `release` | 납품/tapeout 산출물 | 통합 담당자만, master.oas 포함 |

**release 브랜치 보호 규칙:**
- 직접 push 불가 (PR 필수)
- 통합 담당자 리뷰 승인 필요
- master.oas DRC 클린 확인 후 머지

---

## 매크로 동작 (`register_libraries.lym`)

### 설정
```xml
<autorun>true</autorun>
<autorun-early>true</autorun-early>
<interpreter>python</interpreter>
```

`autorun-early: true` — 메인 윈도우가 열리기 전에 실행되어, master.oas 로드 시 라이브러리가 이미 등록된 상태를 보장한다.

### 실행 순서

1. `os.path.realpath(__file__)` 기준으로 저장소 루트 탐색 (`.git` 디렉토리 탐색)
2. `layouts/` 디렉토리의 `*.oas`, `*.gds` 파일 탐색
3. 각 파일에 대해 `pya.Library` 생성 및 등록:
   - 라이브러리 이름 = 파일명(확장자 제외), 예: `"member_A"`
   - `lib.layout().read(filepath)` 로 파일 내용 로드
   - `lib.register()` 로 전역 등록
4. `tech/layers.lyp` 존재 시 경로 기록 (뷰 열릴 때 적용용)
5. 파일 없거나 오류 시 `pya.Application` 로그에 기록

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
layouts_dir = os.path.join(repo_root, "layouts")

for filepath in sorted(glob.glob(os.path.join(layouts_dir, "*.oas")) +
                        glob.glob(os.path.join(layouts_dir, "*.gds"))):
    lib_name = os.path.splitext(os.path.basename(filepath))[0]
    lib = pya.Library()
    lib.name = lib_name
    lib.layout().read(filepath)
    lib.register()
```

---

## 통합 담당자 워크플로우

### 초기 master.oas 생성 (1회)

1. KLayout 시작 → 라이브러리 자동 등록
2. 새 레이아웃 생성 (`File > New Layout`)
3. `Edit > Cell > Place Library Cell` 또는 셀 패널에서 라이브러리 셀 선택 → 위치 지정
4. 필요 시 동일 셀을 여러 번 인스턴스화 (배열, 미러 등 적용 가능)
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
팀원: layouts/member_D.oas 추가 → git push
통합 담당자: git pull → KLayout 재시작 → "member_D" 라이브러리 자동 등록
→ master.oas에서 Place Library Cell로 배치 → 저장 → 커밋
```

---

## 오류 처리

| 상황 | 동작 |
|------|------|
| 저장소 루트 미발견 | 경고 로그 출력 후 매크로 종료 |
| `.oas`/`.gds` 파일 읽기 실패 | 해당 파일 건너뜀, 나머지 등록 계속 |
| 동일 이름 라이브러리 중복 등록 | 기존 라이브러리 덮어씀 (재시작마다 갱신) |
| `layouts/` 디렉토리 없음 | 경고 로그 출력 |

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
