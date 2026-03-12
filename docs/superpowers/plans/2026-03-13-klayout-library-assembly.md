# KLayout 라이브러리 기반 어셈블리 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `autoload.lym`의 geometry 복사 방식을 제거하고, `layouts/*.oas/.gds`를 KLayout pya.Library로 자동 등록하는 Python 매크로(`register_libraries.lym`)로 교체한다.

**Architecture:** KLayout 시작 시 `register_libraries.lym`이 autorun으로 실행되어 `layouts/` 디렉토리의 모든 `.oas`/`.gds` 파일을 `pya.Library`로 등록한다. `master.oas`는 이 라이브러리 셀을 참조하는 플로어플랜으로, 통합 담당자가 직접 관리·커밋한다. `.gitignore`에서 `master.oas`를 제거한다.

**Tech Stack:** KLayout 0.30.7, KLayout Python API (pya), `.lym` XML macro format, Git LFS

**Spec:** `docs/superpowers/specs/2026-03-13-klayout-library-assembly-design.md`

---

## File Map

| 경로 | 동작 | 역할 |
|------|------|------|
| `macros/register_libraries.lym` | 생성 | Python autorun 매크로 (전체 로직) |
| `macros/autoload.lym` | 삭제 | 기존 Ruby merge 매크로 — 완전 대체됨 |
| `.gitignore` | 수정 | `master.oas` 줄 제거 |
| `tests/test_register_libraries.py` | 생성 | 순수 Python 유틸리티 함수 단위 테스트 |

---

## Chunk 1: Git 정리 및 .gitignore 수정

### Task 1: `.gitignore`에서 `master.oas` 제거

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: `.gitignore` 수정**

`.gitignore` 에서 `master.oas` 줄을 제거한다:

```
# 제거할 줄:
master.oas
```

수정 후 `.gitignore` 관련 줄:
```
*.log
*.tmp
*.bak
*.oas.lock
*.pyc
```

- [ ] **Step 2: 변경 확인**

```bash
git check-ignore -v master.oas
```

Expected: 아무 출력 없음 (더 이상 ignore되지 않음)

- [ ] **Step 3: 커밋**

```bash
git add .gitignore
git commit -m "chore: remove master.oas from gitignore — now tracked by integrator"
```

---

## Chunk 2: 순수 Python 유틸리티 단위 테스트

### Task 2: `tests/` 디렉토리 및 단위 테스트 작성

pya 없이 테스트 가능한 순수 Python 함수들을 먼저 테스트로 정의한다.

**Files:**
- Create: `tests/test_register_libraries.py`

- [ ] **Step 1: `tests/` 디렉토리 및 `__init__.py` 생성**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 2: 실패하는 테스트 작성**

`tests/test_register_libraries.py`:

```python
"""
register_libraries.lym의 순수 Python 유틸리티 함수 단위 테스트.
pya 없이 실행 가능한 로직만 테스트한다.
"""
import os
import tempfile
import pytest


# --- 테스트 대상 함수 (매크로와 동일한 로직 복사) ---

def find_repo_root(start):
    path = os.path.dirname(os.path.realpath(start))
    while path != os.path.dirname(path):
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
    return None


def is_lfs_pointer(filepath):
    return os.path.getsize(filepath) < 200


def get_layout_files(layouts_dir):
    """
    layouts_dir에서 .oas와 .gds 파일을 수집한다.
    이름 충돌 시 .oas 우선.
    반환: 절대 경로 리스트 (정렬됨)
    """
    import glob
    oas = sorted(glob.glob(os.path.join(layouts_dir, "*.oas")))
    gds = sorted(glob.glob(os.path.join(layouts_dir, "*.gds")))
    oas_names = {os.path.splitext(os.path.basename(f))[0] for f in oas}
    gds_filtered = [f for f in gds
                    if os.path.splitext(os.path.basename(f))[0] not in oas_names]
    return oas + gds_filtered


# --- 테스트 ---

class TestFindRepoRoot:
    def test_finds_root_from_child_dir(self, tmp_path):
        # .git 디렉토리가 있는 가짜 저장소 생성
        repo = tmp_path / "myrepo"
        repo.mkdir()
        (repo / ".git").mkdir()
        child = repo / "macros"
        child.mkdir()
        fake_file = child / "macro.lym"
        fake_file.write_text("content")

        result = find_repo_root(str(fake_file))
        assert result == str(repo)

    def test_returns_none_when_no_git_dir(self, tmp_path):
        fake_file = tmp_path / "somefile.py"
        fake_file.write_text("content")
        result = find_repo_root(str(fake_file))
        assert result is None

    def test_finds_root_from_deeply_nested_file(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        deep = repo / "a" / "b" / "c"
        deep.mkdir(parents=True)
        fake_file = deep / "file.py"
        fake_file.write_text("x")

        result = find_repo_root(str(fake_file))
        assert result == str(repo)


class TestIsLfsPointer:
    def test_small_file_is_lfs_pointer(self, tmp_path):
        f = tmp_path / "pointer.oas"
        # LFS 포인터는 134바이트 전후
        f.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 12345\n")
        assert is_lfs_pointer(str(f)) is True

    def test_large_file_is_not_lfs_pointer(self, tmp_path):
        f = tmp_path / "real.oas"
        f.write_bytes(b"\x00" * 300)
        assert is_lfs_pointer(str(f)) is False

    def test_boundary_199_bytes_is_pointer(self, tmp_path):
        f = tmp_path / "boundary.oas"
        f.write_bytes(b"\x00" * 199)
        assert is_lfs_pointer(str(f)) is True

    def test_boundary_200_bytes_is_not_pointer(self, tmp_path):
        f = tmp_path / "boundary2.oas"
        f.write_bytes(b"\x00" * 200)
        assert is_lfs_pointer(str(f)) is False


class TestGetLayoutFiles:
    def test_returns_oas_files(self, tmp_path):
        (tmp_path / "a.oas").write_bytes(b"\x00" * 300)
        (tmp_path / "b.oas").write_bytes(b"\x00" * 300)
        result = get_layout_files(str(tmp_path))
        names = [os.path.basename(f) for f in result]
        assert "a.oas" in names
        assert "b.oas" in names

    def test_oas_takes_priority_over_gds_same_name(self, tmp_path):
        (tmp_path / "chip.oas").write_bytes(b"\x00" * 300)
        (tmp_path / "chip.gds").write_bytes(b"\x00" * 300)
        result = get_layout_files(str(tmp_path))
        names = [os.path.basename(f) for f in result]
        assert "chip.oas" in names
        assert "chip.gds" not in names

    def test_gds_included_when_no_oas_collision(self, tmp_path):
        (tmp_path / "a.oas").write_bytes(b"\x00" * 300)
        (tmp_path / "b.gds").write_bytes(b"\x00" * 300)
        result = get_layout_files(str(tmp_path))
        names = [os.path.basename(f) for f in result]
        assert "a.oas" in names
        assert "b.gds" in names

    def test_empty_dir_returns_empty_list(self, tmp_path):
        result = get_layout_files(str(tmp_path))
        assert result == []

    def test_nonexistent_dir_returns_empty_list(self):
        result = get_layout_files("/nonexistent/path/layouts")
        assert result == []
```

- [ ] **Step 3: 테스트 실행 및 통과 확인**

```bash
cd /mnt/c/users/ahris/Documents/klayout_test
python -m pytest tests/test_register_libraries.py -v
```

Expected: 모든 테스트 PASS

- [ ] **Step 5: 커밋**

```bash
git add tests/
git commit -m "test: add unit tests for register_libraries utility functions"
```

---

## Chunk 3: `register_libraries.lym` 생성

### Task 3: Python autorun 매크로 작성

**Files:**
- Create: `macros/register_libraries.lym`

- [ ] **Step 1: `macros/register_libraries.lym` 작성**

```xml
<?xml version="1.0" encoding="utf-8"?>
<klayout-macro>
 <description>KLayout Library Registration — layouts/ 자동 라이브러리 등록</description>
 <autorun>true</autorun>
 <autorun-early>false</autorun-early>
 <interpreter>python</interpreter>
 <text><![CDATA[
import pya
import os
import glob


def find_repo_root(start):
    path = os.path.dirname(os.path.realpath(start))
    while path != os.path.dirname(path):
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
    return None


def is_lfs_pointer(filepath):
    return os.path.getsize(filepath) < 200


def get_layout_files(layouts_dir):
    oas = sorted(glob.glob(os.path.join(layouts_dir, "*.oas")))
    gds = sorted(glob.glob(os.path.join(layouts_dir, "*.gds")))
    oas_names = {os.path.splitext(os.path.basename(f))[0] for f in oas}
    gds_filtered = [f for f in gds
                    if os.path.splitext(os.path.basename(f))[0] not in oas_names]
    return oas + gds_filtered


def register_libraries():
    repo_root = find_repo_root(__file__)
    if repo_root is None:
        pya.Logger.error(
            "register_libraries: 저장소 루트를 찾을 수 없습니다. "
            "docs/usage.md 설치 가이드를 확인하세요."
        )
        return

    layouts_dir = os.path.join(repo_root, "layouts")
    if not os.path.isdir(layouts_dir):
        pya.Logger.warn("register_libraries: layouts/ 디렉토리가 없습니다.")
        return

    all_files = get_layout_files(layouts_dir)
    if not all_files:
        pya.Logger.warn("register_libraries: layouts/ 에 .oas/.gds 파일이 없습니다.")
        return

    for filepath in all_files:
        lib_name = os.path.splitext(os.path.basename(filepath))[0]

        if is_lfs_pointer(filepath):
            pya.Logger.error(
                f"register_libraries: {lib_name} — 파일이 너무 작습니다 ({os.path.getsize(filepath)}바이트). "
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

    lyp_path = os.path.join(repo_root, "tech", "layers.lyp")
    if os.path.isfile(lyp_path):
        pya.Logger.info(
            "register_libraries: tech/layers.lyp 발견 — "
            "Technology 파일 또는 Edit > Layer Properties > Load 로 적용하세요."
        )


register_libraries()
  ]]></text>
</klayout-macro>
```

- [ ] **Step 2: KLayout에서 수동 검증 — 매크로 등록**

KLayout Macro Development에서 `macros/` 경로가 이미 등록되어 있다면 재시작만으로 충분. 아니라면 Local > Add Location으로 등록 후 재시작.

- [ ] **Step 3: KLayout에서 수동 검증 — 로그 확인**

KLayout 재시작 후 Macro Development 콘솔에서 확인:
```
register_libraries: 등록 완료 — test_layout
```
(`layouts/test_layout.oas`가 있는 경우)

- [ ] **Step 4: KLayout에서 수동 검증 — 라이브러리 확인**

새 레이아웃 생성 후 `Edit > Cell > Instance...` (또는 셀 패널) 에서 라이브러리 목록에 `test_layout` 이 나타나는지 확인.

- [ ] **Step 5: 커밋**

```bash
git add macros/register_libraries.lym
git commit -m "feat: add Python library registration macro"
```

---

## Chunk 4: `autoload.lym` 제거 및 문서 업데이트

### Task 4: 기존 Ruby 매크로 제거

**Files:**
- Delete: `macros/autoload.lym`

- [ ] **Step 1: `autoload.lym` 삭제**

```bash
git rm macros/autoload.lym
```

- [ ] **Step 2: KLayout에서 수동 검증**

KLayout 재시작 후 `autoload.lym` 관련 에러 없이 `register_libraries` 로그만 출력되는지 확인.

- [ ] **Step 3: 커밋**

```bash
git commit -m "chore: remove legacy autoload.lym — replaced by register_libraries.lym"
```

---

### Task 5: 문서 업데이트

**Files:**
- Modify: `docs/usage.md`
- Modify: `docs/README.md`

- [ ] **Step 1: `docs/README.md` 수정**

디렉토리 구조 표에서 `autoload.lym` → `register_libraries.lym`으로 교체, `master.oas` 설명 업데이트:

| 경로 | 설명 |
|------|------|
| `layouts/` | 팀원별 담당 블록 `.oas`/`.gds` 파일 (Git LFS) |
| `tech/layers.lyp` | 공통 레이어 속성 |
| `macros/register_libraries.lym` | KLayout 시작 시 자동 실행 — 라이브러리 등록 |
| `master.oas` | 플로어플랜 (통합 담당자 관리, git 커밋) |

- [ ] **Step 2: `docs/usage.md` 수정**

"일상 작업 흐름" 섹션을 아래로 교체:

```markdown
## 일상 작업 흐름

# 1. 최신 변경사항 가져오기
git pull

# 2. KLayout 실행 → 라이브러리 자동 등록 (register_libraries.lym)

# 3. 본인 담당 파일 작업
#    layouts/자기이름.oas 편집

# 4. 저장 후 커밋 & push
git add layouts/자기이름.oas
git commit -m "feat: 작업 내용 요약"
git push

## 통합 담당자 작업 (master.oas 배치)

# KLayout에서 Edit > Cell > Instance... 로 라이브러리 셀 배치
# master.oas 저장 후 release 브랜치 PR
```

"문제 해결" 표에 항목 추가:

| 증상 | 원인 | 해결 |
|------|------|------|
| 라이브러리 목록에 셀이 없음 | 매크로 미등록 또는 LFS 포인터 파일 | Macro Development에서 macros/ 경로 확인, git lfs pull 실행 |
| "파일이 너무 작습니다" 로그 | Git LFS 미설치 | `git lfs install && git lfs pull` |

Linux/macOS 설치 심볼릭 링크 (이전 `autoload.lym` 대신 `register_libraries.lym`):
```bash
ln -s /path/to/repo/macros/register_libraries.lym ~/.klayout/macros/register_libraries.lym
```

- [ ] **Step 3: 커밋**

```bash
git add docs/README.md docs/usage.md
git commit -m "docs: update for library-based assembly workflow"
```

---

## 최종 검증

- [ ] KLayout 재시작 → Macro Development 콘솔에 `등록 완료` 로그 확인
- [ ] `Edit > Cell > Instance...` 에서 `layouts/` 파일명으로 라이브러리 표시 확인
- [ ] 새 레이아웃에서 라이브러리 셀 배치 후 `master.oas`로 저장 가능 확인
- [ ] `git status`에서 `master.oas`가 untracked으로 표시됨 (gitignore 제거 확인)
- [ ] 팀원 `.oas` 수정 후 KLayout 재시작 → 라이브러리 내용 갱신 확인
- [ ] `python -m pytest tests/ -v` → 모든 테스트 PASS 확인
