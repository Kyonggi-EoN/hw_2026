# KLayout Auto Assembly Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** KLayout 시작 시 `layouts/` 안의 모든 팀원 `.oas` 파일을 자동으로 병합해 `master.oas`를 생성하고 통합 뷰를 표시한다.

**Architecture:** `macros/autoload.lym` 하나의 파일에 모든 로직을 담은 KLayout Ruby 매크로. XML `<autorun>true</autorun>` 으로 시작 시 자동 실행. 저장소 루트는 `File.realpath(__FILE__)`로 `.git` 디렉토리를 탐색해 결정. 좌표 경계 할당은 `tech/block_assignments.json`에서 읽음.

**Tech Stack:** KLayout Ruby API (RBA), KLayout `.lym` XML macro format, Git LFS

**Spec:** `docs/superpowers/specs/2026-03-12-klayout-auto-assembly-design.md`

---

## File Map

| 경로 | 동작 | 역할 |
|------|------|------|
| `macros/autoload.lym` | 생성 | 자동 실행 매크로 (전체 로직 포함) |
| `tech/block_assignments.json` | 생성 | 팀원별 좌표 경계 할당 (매크로가 읽음) |
| `docs/README.md` | 생성 | 프로젝트 구조 개요 |
| `docs/usage.md` | 생성 | 팀원 설치 및 작업 가이드 |
| `docs/coordinate_guide.md` | 생성 | 좌표 규칙 및 블록 할당 설명 |
| `.gitignore` | 수정 완료 | `master.oas` 이미 추가됨 |

---

## Chunk 1: 매크로 디렉토리 및 기본 구조

### Task 1: `macros/` 디렉토리 복원 및 `.lym` 기본 골격 생성

**Files:**
- Create: `macros/autoload.lym`

- [ ] **Step 1: `macros/autoload.lym` 기본 골격 생성**

```xml
<?xml version="1.0" encoding="utf-8"?>
<klayout-macro>
 <description>KLayout Auto Assembly — 팀 레이아웃 자동 통합</description>
 <autorun>true</autorun>
 <autorun-early>false</autorun-early>
 <interpreter>ruby</interpreter>
 <script><![CDATA[
module KLayoutAutoAssembly

  # 저장소 루트 탐색: File.realpath로 심볼릭 링크 해소 후 .git 디렉토리 탐색
  def self.find_repo_root(start_path)
    path = File.dirname(File.realpath(start_path))
    until path == File.dirname(path)
      return path if File.directory?(File.join(path, ".git"))
      path = File.dirname(path)
    end
    nil
  end

  def self.run
    repo_root = find_repo_root(__FILE__)
    if repo_root.nil?
      RBA::MessageBox.warning(
        "Auto Assembly",
        "저장소 루트를 찾을 수 없습니다.\ndocs/usage.md 설치 가이드를 확인하세요.",
        RBA::MessageBox::Ok
      )
      return
    end

    RBA::Logger.info("Auto Assembly: 저장소 루트 = #{repo_root}")
  end

end

KLayoutAutoAssembly.run
  ]]></script>
</klayout-macro>
```

- [ ] **Step 2: KLayout에서 수동 검증**

  1. KLayout 실행
  2. Tools > Macro IDE에서 `macros/autoload.lym` 경로 추가
  3. KLayout 재시작
  4. Application Output에 `Auto Assembly: 저장소 루트 = ...` 로그 확인

- [ ] **Step 3: 커밋**

```bash
git add macros/autoload.lym
git commit -m "feat: add autoload macro skeleton with repo root detection"
```

---

## Chunk 2: 레이아웃 로딩 및 병합

### Task 2: `layouts/` 탐색 및 계층적 병합

**Files:**
- Modify: `macros/autoload.lym` — `run` 메서드 확장

- [ ] **Step 1: `layouts/` 탐색 및 병합 로직 추가**

`run` 메서드의 `RBA::Logger.info` 이후에 추가:

```ruby
    layouts_dir = File.join(repo_root, "layouts")
    oas_files = Dir.glob(File.join(layouts_dir, "*.oas")).sort

    if oas_files.empty?
      RBA::MessageBox.warning(
        "Auto Assembly",
        "layouts/ 디렉토리에 .oas 파일이 없습니다.",
        RBA::MessageBox::Ok
      )
      return
    end

    # 마스터 레이아웃 객체 생성
    master_layout = RBA::Layout.new
    master_top = master_layout.create_cell("assembly")

    failed_files = []
    oas_files.each do |oas_path|
      begin
        opt = RBA::LoadLayoutOptions.new
        opt.cell_conflict_resolution =
          RBA::LoadLayoutOptions::CellConflictResolution::RenameCell

        tmp_layout = RBA::Layout.new
        tmp_layout.read(oas_path, opt)

        # tmp_layout의 top cell들을 master_layout으로 복사 후 assembly 셀에 인스턴스 추가
        tmp_layout.each_top_cell do |top_cell_idx|
          cell_name = tmp_layout.cell(top_cell_idx).name
          new_cell = master_layout.create_cell(cell_name)
          new_cell.copy_tree(tmp_layout.cell(top_cell_idx))
          master_top.insert(
            RBA::CellInstArray.new(new_cell.cell_index, RBA::Trans.new)
          )
        end

        RBA::Logger.info("Auto Assembly: 로드 완료 — #{File.basename(oas_path)}")
      rescue => e
        failed_files << File.basename(oas_path)
        RBA::Logger.error("Auto Assembly: 로드 실패 — #{File.basename(oas_path)}: #{e.message}")
      end
    end

    if failed_files.any?
      RBA::MessageBox.warning(
        "Auto Assembly",
        "다음 파일 로드 실패 (나머지는 정상 병합됨):\n#{failed_files.join("\n")}",
        RBA::MessageBox::Ok
      )
    end
```

- [ ] **Step 2: KLayout에서 수동 검증**

  1. `layouts/test_layout.oas`가 있는 상태에서 KLayout 재시작
  2. Application Output에 `로드 완료 — test_layout.oas` 확인
  3. 존재하지 않는 파일명으로 테스트 시 경고 메시지 확인

- [ ] **Step 3: 커밋**

```bash
git add macros/autoload.lym
git commit -m "feat: add layout loading and hierarchical merge logic"
```

---

### Task 3: 레이어 속성 적용 및 `master.oas` 저장, 뷰 표시

**Files:**
- Modify: `macros/autoload.lym` — 병합 루프 이후 추가

- [ ] **Step 1: layers.lyp 적용, master.oas 저장, 뷰 표시 로직 추가**

failed_files 처리 블록 이후에 추가:

```ruby
    # 레이어 속성 적용
    lyp_path = File.join(repo_root, "tech", "layers.lyp")
    view = RBA::LayoutView.current
    if view.nil?
      view = RBA::Application.instance.main_window.create_layout(0)
    end

    # 메모리 레이아웃을 직접 뷰에 표시
    view.show_layout(master_layout, true)

    if File.exist?(lyp_path)
      view.load_layer_props(lyp_path)
      RBA::Logger.info("Auto Assembly: layers.lyp 적용 완료")
    else
      RBA::MessageBox.warning(
        "Auto Assembly",
        "tech/layers.lyp 파일이 없습니다.\n레이어 속성이 적용되지 않았습니다.",
        RBA::MessageBox::Ok
      )
    end

    # master.oas 저장
    master_path = File.join(repo_root, "master.oas")
    begin
      master_layout.write(master_path)
      RBA::Logger.info("Auto Assembly: master.oas 저장 완료 — #{master_path}")
    rescue => e
      RBA::MessageBox.warning(
        "Auto Assembly",
        "master.oas 저장 실패 (뷰는 정상 표시됨):\n#{e.message}",
        RBA::MessageBox::Ok
      )
    end
```

- [ ] **Step 2: KLayout에서 수동 검증**

  1. KLayout 재시작
  2. 통합 뷰가 열리는지 확인
  3. 저장소 최상위에 `master.oas` 파일 생성 확인
  4. `git status`에서 `master.oas`가 untracked으로 나타나지 않는지 확인 (`.gitignore` 적용 확인)

- [ ] **Step 3: 커밋**

```bash
git add macros/autoload.lym
git commit -m "feat: add layer props loading, master.oas save, and view display"
```

---

## Chunk 3: 좌표 경계 검사

### Task 4: `tech/block_assignments.json` 생성

**Files:**
- Create: `tech/block_assignments.json`

- [ ] **Step 1: 좌표 할당 JSON 파일 생성 (템플릿)**

```json
{
  "_comment": "팀원별 담당 블록 좌표 범위 (단위: nm). 실제 플로어플랜에 맞게 수정 필요.",
  "member_A.oas": { "xmin": 0,      "ymin": 0,      "xmax": 100000, "ymax": 100000 },
  "member_B.oas": { "xmin": 100000, "ymin": 0,      "xmax": 200000, "ymax": 100000 },
  "member_C.oas": { "xmin": 0,      "ymin": 100000, "xmax": 100000, "ymax": 200000 }
}
```

- [ ] **Step 2: 커밋**

```bash
git add tech/block_assignments.json
git commit -m "feat: add block coordinate assignment template"
```

---

### Task 5: 매크로에 좌표 경계 검사 로직 추가

**Files:**
- Modify: `macros/autoload.lym` — `run` 메서드 끝에 추가

- [ ] **Step 1: 좌표 경계 검사 메서드 추가**

`module KLayoutAutoAssembly` 안에 `run` 메서드 위에 추가:

```ruby
  def self.check_coordinate_bounds(oas_files, repo_root)
    assignments_path = File.join(repo_root, "tech", "block_assignments.json")
    return unless File.exist?(assignments_path)

    require "json"
    assignments = JSON.parse(File.read(assignments_path))
    violations = []

    oas_files.each do |oas_path|
      filename = File.basename(oas_path)
      bounds = assignments[filename]
      next unless bounds  # 할당 정보 없으면 검사 생략

      tmp = RBA::Layout.new
      tmp.read(oas_path)
      dbu = tmp.dbu  # 데이터베이스 단위 (마이크로미터/단위)

      tmp.each_top_cell do |top_idx|
        bbox = tmp.cell(top_idx).bbox
        # bbox 좌표는 dbu 단위이므로 nm으로 변환 (dbu는 μm 단위)
        xmin_nm = (bbox.left  * dbu * 1000).round
        ymin_nm = (bbox.bottom * dbu * 1000).round
        xmax_nm = (bbox.right  * dbu * 1000).round
        ymax_nm = (bbox.top    * dbu * 1000).round

        out = []
        out << "xmin(#{xmin_nm} < #{bounds['xmin']})" if xmin_nm < bounds["xmin"]
        out << "ymin(#{ymin_nm} < #{bounds['ymin']})" if ymin_nm < bounds["ymin"]
        out << "xmax(#{xmax_nm} > #{bounds['xmax']})" if xmax_nm > bounds["xmax"]
        out << "ymax(#{ymax_nm} > #{bounds['ymax']})" if ymax_nm > bounds["ymax"]

        violations << "#{filename}: #{out.join(', ')}" if out.any?
      end
    end

    if violations.any?
      RBA::MessageBox.warning(
        "Auto Assembly — 좌표 범위 초과",
        "다음 파일이 할당된 좌표 범위를 벗어났습니다:\n\n#{violations.join("\n")}\n\ndocs/coordinate_guide.md를 확인하세요.",
        RBA::MessageBox::Ok
      )
    end
  end
```

- [ ] **Step 2: `run` 메서드 끝에 호출 추가**

`master.oas` 저장 블록 이후에 추가:

```ruby
    # 좌표 경계 검사
    check_coordinate_bounds(oas_files, repo_root)
```

- [ ] **Step 3: KLayout에서 수동 검증**

  1. `tech/block_assignments.json`에서 범위를 의도적으로 좁게 설정
  2. KLayout 재시작
  3. 좌표 범위 초과 경고 메시지 확인
  4. 범위를 넓게 설정 후 재시작 — 경고 없음 확인

- [ ] **Step 4: 커밋**

```bash
git add macros/autoload.lym
git commit -m "feat: add coordinate boundary check with block_assignments.json"
```

---

## Chunk 4: 문서화

### Task 6: `docs/README.md` 생성

**Files:**
- Create: `docs/README.md`

- [ ] **Step 1: README.md 작성**

```markdown
# KLayout 반도체 설계 저장소

## 개요

20명 이상의 팀원이 각자 담당 블록을 별도 `.oas` 파일로 작업하고,
KLayout 시작 시 자동으로 전체 레이아웃을 통합해 확인할 수 있는 협업 환경.

## 디렉토리 구조

| 경로 | 설명 |
|------|------|
| `layouts/` | 팀원별 담당 블록 `.oas` 파일 (Git LFS) |
| `tech/layers.lyp` | 공통 레이어 속성 (색상, 스타일) |
| `tech/block_assignments.json` | 팀원별 좌표 범위 할당표 |
| `macros/autoload.lym` | KLayout 시작 시 자동 실행 매크로 |
| `master.oas` | 전체 통합 뷰 (로컬 자동 생성, git 추적 안 함) |
| `docs/` | 문서 |

## 브랜치 전략

- `main`: 팀원 일상 작업 브랜치
- `release`: 검증 완료 산출물 (통합 담당자만 push)

## 관련 문서

- [설치 및 사용 가이드](usage.md)
- [좌표 규칙](coordinate_guide.md)
```

- [ ] **Step 2: 커밋**

```bash
git add docs/README.md
git commit -m "docs: add project README"
```

---

### Task 7: `docs/usage.md` 생성

**Files:**
- Create: `docs/usage.md`

- [ ] **Step 1: usage.md 작성**

```markdown
# 설치 및 작업 가이드

## 1회 설치

### Linux / macOS

```bash
# KLayout 매크로 디렉토리에 심볼릭 링크
ln -s /path/to/repo/macros/autoload.lym ~/.klayout/macros/autoload.lym
```

### Windows

1. KLayout 실행
2. **Tools > Macro IDE** (또는 Macros > Macro Development)
3. 좌측 패널 하단 **"+"** 버튼 클릭
4. 저장소의 `macros/` 폴더 경로 추가
5. KLayout 재시작

## 일상 작업 흐름

```bash
# 1. 최신 변경사항 가져오기
git pull

# 2. KLayout 실행 → 자동으로 master.oas 생성 및 통합 뷰 표시

# 3. 본인 담당 파일 작업
#    layouts/member_이름.oas 편집

# 4. 저장 후 커밋 & push
git add layouts/member_이름.oas
git commit -m "feat: 작업 내용 요약"
git push
```

## Release 절차 (통합 담당자)

```bash
# main 최신화 확인 후
git checkout release
git merge main
# master.oas 검증 후 추가
git add master.oas
git commit -m "release: vX.X 통합 산출물"
git push
```

## 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| 시작 시 "저장소 루트를 찾을 수 없습니다" | 매크로 경로 설정 오류 | 설치 단계 재확인 |
| `master.oas` 저장 실패 | 쓰기 권한 또는 디스크 공간 | 경고 무시해도 뷰는 정상 |
| 레이어 색상이 다름 | `layers.lyp` 미적용 | `tech/layers.lyp` 존재 확인 |
| 좌표 범위 초과 경고 | 블록 경계 위반 | `docs/coordinate_guide.md` 참고 |
```

- [ ] **Step 2: 커밋**

```bash
git add docs/usage.md
git commit -m "docs: add installation and usage guide"
```

---

### Task 8: `docs/coordinate_guide.md` 생성

**Files:**
- Create: `docs/coordinate_guide.md`

- [ ] **Step 1: coordinate_guide.md 작성**

```markdown
# 좌표 규칙 및 블록 할당

## 기본 원칙

- 모든 팀원은 **절대좌표**로 작업한다 (원점 기준 상대좌표 사용 금지)
- 각자 아래 표에서 할당된 범위 **안에서만** 작업한다
- 범위 외 geometry는 `autoload.lym`이 시작 시 경고한다

## 단위

KLayout DBU (Database Unit)는 프로젝트 기본값인 **0.001 μm = 1 nm** 기준.
좌표 할당표는 **nm 단위**로 기재한다.

## 블록 할당표

| 파일명 | 담당자 | X 범위 (nm) | Y 범위 (nm) | 설명 |
|--------|--------|-------------|-------------|------|
| `member_A.oas` | 홍길동 | 0 ~ 100,000 | 0 ~ 100,000 | 예시 블록 A |
| `member_B.oas` | 김철수 | 100,000 ~ 200,000 | 0 ~ 100,000 | 예시 블록 B |
| `member_C.oas` | 이영희 | 0 ~ 100,000 | 100,000 ~ 200,000 | 예시 블록 C |

> **실제 플로어플랜 확정 후 이 표와 `tech/block_assignments.json`을 함께 업데이트할 것.**

## 좌표 변경 절차

1. 팀 전체 합의
2. 이 문서의 표 수정
3. `tech/block_assignments.json` 수정
4. `main` 브랜치에 커밋 & push
5. 전 팀원 git pull 후 재작업 범위 확인
```

- [ ] **Step 2: 커밋**

```bash
git add docs/coordinate_guide.md
git commit -m "docs: add coordinate assignment guide"
```

---

## 최종 검증

- [ ] KLayout 재시작 → 통합 뷰 자동 표시 확인
- [ ] `master.oas`가 저장소 최상위에 생성되고 `git status`에 나타나지 않음 확인
- [ ] 팀원 파일 추가/수정 후 재시작 → 통합 뷰에 반영 확인
- [ ] `tech/layers.lyp` 없을 때 경고 메시지 확인
- [ ] `tech/block_assignments.json` 범위 초과 시 경고 메시지 확인
