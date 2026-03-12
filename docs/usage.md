# 설치 및 작업 가이드

## 1회 설치

### Linux / macOS

```bash
ln -s /path/to/repo/macros/register_libraries.lym ~/.klayout/macros/register_libraries.lym
```

### Windows

1. KLayout 실행
2. **Macros > Macro Development**
3. 좌측 패널에서 **Local > Add Location** (우클릭 메뉴)
4. 저장소의 `macros/` 폴더 경로 추가
5. KLayout 재시작

## 팀원 일상 작업

```bash
# 1. 최신 변경사항 가져오기
git pull

# 2. KLayout 실행 → 라이브러리 자동 등록

# 3. 본인 담당 파일 편집
#    layouts/자기이름.oas

# 4. 커밋 & push
git add layouts/자기이름.oas
git commit -m "feat: 작업 내용 요약"
git push
```

## 통합 담당자 작업 (master.oas)

### master.oas 기본 사용법

1. KLayout 시작 → 라이브러리 자동 등록
2. `master.oas` 열기 (또는 최초 생성: `File > New Layout`)
3. **셀 배치:** `Edit > Cell > Instance...` → Library 선택 → 셀 선택 → 위치 클릭
4. **동일 셀 재사용:** 같은 라이브러리 셀을 여러 번 배치 가능 (미러, 회전 포함)
5. **배선/메탈 추가:** 라이브러리 셀 사이 배선을 master.oas에 직접 그릴 수 있음. git pull 후 재시작해도 사라지지 않음.
6. 저장: `File > Save As > master.oas`

### 팀원 업데이트 반영

```bash
git pull
# KLayout 재시작 → 라이브러리 자동 갱신
# master.oas 열기 → 배치 위치 유지 + 셀 내용 최신화
```

### release 커밋

```bash
git checkout release
git merge main
git add master.oas
git commit -m "release: vX.X tapeout"
git push
```

## 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| KLayout 시작 시 라이브러리 없음 | 매크로 미등록 | Macro Development에서 `macros/` 경로 추가 후 재시작 |
| "파일이 너무 작습니다" 로그 | Git LFS 미설치 | `git lfs install && git lfs pull` |
| 셀 배치 후 내용이 비어 있음 | LFS 포인터 파일 | `git lfs pull` 실행 |
| 레이어 색상이 다름 | `layers.lyp` 미적용 | `Edit > Layer Properties > Load` → `tech/layers.lyp` 선택 |
