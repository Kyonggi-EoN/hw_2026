# KLayout 자동 통합 뷰 시스템 설계

**날짜:** 2026-03-12
**상태:** 확정

---

## 개요

20명 이상의 팀원이 각자 담당 블록을 별도 `.oas` 파일로 작업하고, KLayout 시작 시 매크로가 자동으로 모든 파일을 병합해 통합 뷰를 생성한다. `master.oas`는 로컬에서만 생성되며 `main` 브랜치에는 커밋하지 않는다. 검증 후 지정된 통합 담당자가 `release` 브랜치에만 `master.oas`를 커밋/push한다.

---

## 디렉토리 구조

```
klayout_test/
├── master.oas                  # 통합 뷰 (로컬 전용, .gitignore 처리)
├── layouts/
│   ├── member_A.oas            # 팀원별 담당 블록 (Git LFS)
│   ├── member_B.oas
│   └── ...
├── tech/
│   └── layers.lyp              # 공통 레이어 속성
├── macros/
│   ├── .gitkeep                # 디렉토리 추적용
│   └── autoload.lym            # KLayout 시작 시 자동 실행 매크로
└── docs/
    ├── README.md               # 프로젝트 구조 개요
    ├── usage.md                # 설치 및 작업 가이드
    └── coordinate_guide.md     # 좌표 규칙 및 블록 할당표
```

---

## Git 관리

### `.gitignore` 추가 항목
```
master.oas
```
`master.oas`는 매크로가 로컬에서 자동 생성하므로 `main` 브랜치에서는 추적하지 않는다.

### `.gitattributes`
| 패턴 | 처리 방식 |
|------|-----------|
| `layouts/*.oas` | Git LFS (바이너리) |
| `macros/*.lym` | 텍스트, LF |
| `tech/*.lyp` | 텍스트, LF |
| `tech/*.lyt` | 텍스트, LF |
| `docs/*.md` | 텍스트, LF |

### 브랜치 전략

```
main 브랜치 (팀원 작업)
  └─ layouts/member_X.oas 작업 및 push
  └─ master.oas는 로컬에서만 생성, 커밋 안 함

release 브랜치 (보호된 브랜치, 통합 담당자만 접근)
  └─ 통합 담당자가 검증 완료 후 master.oas 포함하여 push
  └─ 외부 공유/납품용 최종 산출물
```

**release 브랜치 보호 규칙:**
- 직접 push 불가 (Pull Request 필수)
- 통합 담당자 1인 이상 리뷰 승인 필요
- 검증 기준: DRC 클린, 모든 팀원 파일 존재, 좌표 충돌 없음

---

## 매크로 동작 (`autoload.lym`)

### 자동 실행 설정

`autoload.lym` 파일의 XML 헤더에 `<autorun>true</autorun>` 설정이 필요하다:

```xml
<?xml version="1.0" encoding="utf-8"?>
<klayout-macro>
  <description>KLayout Auto Assembly</description>
  <autorun>true</autorun>
  <autorun-early>false</autorun-early>
  <interpreter>ruby</interpreter>
  <script>
    # ... Ruby 코드
  </script>
</klayout-macro>
```

### 루트 경로 계산

`File.realpath`로 심볼릭 링크를 해소한 뒤 `.git` 디렉토리를 찾아 저장소 루트를 결정한다:

```ruby
def find_repo_root(start_path)
  path = File.dirname(File.realpath(start_path))
  until path == File.dirname(path)
    return path if File.directory?(File.join(path, ".git"))
    path = File.dirname(path)
  end
  nil
end

repo_root = find_repo_root(__FILE__)
```

`File.realpath`를 사용하므로 심볼릭 링크 환경(`~/.klayout/macros/`에 링크된 경우)에서도 실제 저장소 경로를 올바르게 찾는다.

### 실행 순서

1. `File.realpath(__FILE__)` 기준으로 저장소 루트 경로 계산
2. `layouts/` 디렉토리의 모든 `.oas` 파일 탐색
3. 빈 `master` Layout 객체 생성
4. 각 파일을 계층적 병합으로 읽기 (아래 셀 병합 전략 참고)
5. `tech/layers.lyp` 레이어 속성 적용
6. 메모리의 Layout 객체를 `LayoutView#show_layout`으로 직접 표시 (불필요한 디스크 왕복 없음)
7. 병합 결과를 `master.oas`로 저장 (저장소 최상위) — 쓰기 실패 시 경고만 표시, 뷰는 유지
8. 좌표 경계 검사 실행
9. 파일 누락/오류 발생 시 KLayout 메시지 박스로 안내

### 셀 병합 전략

KLayout Ruby API의 `Layout#read`와 `LoadLayoutOptions`를 사용한 **계층적 병합**을 적용한다:

- 각 팀원의 `.oas` 파일을 서브셀로 참조 (geometry 복사 아님)
- 셀 이름 충돌 시: `CellConflictResolution::RenameCell` — 충돌 셀에 파일명 접두사 추가
- 최종 `master.oas`에는 각 팀원 파일의 top cell을 인스턴스로 포함하는 하나의 최상위 셀(`assembly`) 생성

```ruby
opt = RBA::LoadLayoutOptions.new
opt.cell_conflict_resolution =
  RBA::LoadLayoutOptions::CellConflictResolution::RenameCell
master_layout.read(member_file_path, opt)
```

---

## 좌표 규칙 (`coordinate_guide.md`에 상세 기술)

- 전체 칩 플로어플랜을 `docs/coordinate_guide.md`에 정의
- 팀원마다 담당 블록의 **절대좌표 범위**를 사전 할당
- 각자 절대좌표로 작업 → 병합 시 자동으로 올바른 위치에 배치
- 좌표 범위 외 작업 금지 (충돌 방지)

### 자동 좌표 경계 검사

매크로가 병합 후 각 팀원 파일의 geometry가 할당된 좌표 범위 안에 있는지 검사한다. 범위 초과 시 해당 파일명과 초과 영역을 경고 메시지로 표시한다. 좌표 할당표는 `docs/coordinate_guide.md`에서 읽는다.

---

## 설치 (팀원 1회 설정)

**방법 A — 심볼릭 링크 (Linux/macOS):**
```bash
ln -s /path/to/repo/macros/autoload.lym ~/.klayout/macros/autoload.lym
```

**방법 B — KLayout Macro 경로 등록 (Windows):**
1. KLayout 실행 → Tools > Macro IDE (또는 Macros > Macro Development)
2. 좌측 패널 하단 "+" 버튼으로 저장소의 `macros/` 폴더 경로 추가
3. KLayout 재시작

두 방법 모두 `autoload.lym` 안의 `<autorun>true</autorun>` 설정이 동작의 전제 조건이다.

---

## 오류 처리

| 상황 | 동작 |
|------|------|
| 저장소 루트 미발견 | 오류 메시지 표시 후 종료 (usage.md 참고 안내) |
| `layouts/`에 `.oas` 파일 없음 | 경고 메시지 후 빈 뷰 |
| 특정 파일 읽기 실패 | 해당 파일 건너뛰고 나머지 병합, 파일명 포함 경고 |
| `layers.lyp` 없음 | 레이어 속성 미적용 경고, 병합은 계속 진행 |
| `master.oas` 쓰기 실패 | 경고 메시지 표시, 뷰는 메모리에서 유지 |
| 좌표 범위 초과 감지 | 해당 팀원 파일명과 초과 영역 경고, 병합은 계속 진행 |
