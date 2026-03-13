# 통합 담당자 작업 가이드

## master.oas 기본 사용법

1. KLayout 시작 → 라이브러리 자동 등록
2. `master.oas` 열기 (또는 최초 생성: `File > New Layout`)
3. **셀 배치:** `Edit > Cell > Instance...` → Library 선택 → 셀 선택 → 위치 클릭
4. **동일 셀 재사용:** 같은 라이브러리 셀을 여러 번 배치 가능 (미러, 회전 포함)
5. **배선/메탈 추가:** 라이브러리 셀 사이 배선을 master.oas에 직접 그릴 수 있음. git pull 후 재시작해도 사라지지 않음.
6. 저장: `File > Save As > master.oas`

## 팀원 업데이트 반영

```bash
git pull
# 방법 A (권장): KLayout 재시작 없이
#   Tools > Reload Libraries → 완료 다이얼로그 확인
#   master.oas에 즉시 반영됨

# 방법 B: KLayout 재시작
#   재시작 후 master.oas 열기 → 배치 위치 유지 + 셀 내용 최신화
```

## 라이브러리 셀 수정이 필요할 때

라이브러리로 등록된 셀은 master.oas에서 직접 편집할 수 없다 (read-only 참조). 목적에 따라 아래 세 가지 방법을 택한다.

### 방법 1: 원본 파일 수정 후 Reload (권장)
담당 팀원에게 수정 요청 → PR 머지 → `git pull` → `Tools > Reload Libraries`

직접 수정이 필요하다면:
1. `layouts/파일명.gds`를 KLayout에서 직접 열어 편집
2. 저장 후 `git commit/push`
3. `Tools > Reload Libraries`로 master.oas에 반영

### 방법 2: Flatten (라이브러리 링크 해제)
라이브러리 인스턴스를 선택 후 **Edit > Cell > Flatten Cell** (`Ctrl+F`)

- 셀 내용이 master.oas 안으로 복사되어 자유롭게 편집 가능
- **주의:** 이후 `Reload Libraries`로 해당 셀이 업데이트되지 않음 (링크 끊김)
- 임시 확인·실험 목적에만 사용할 것

### 방법 3: 라이브러리 셀 위에 레이어 추가
라이브러리 인스턴스는 그대로 두고, master.oas에 새 셀/레이어를 추가해 덮어쓰는 방식.

- 원본 라이브러리 링크 유지 → Reload 시 팀원 업데이트도 계속 반영됨
- 배선·메탈·마커 등 통합 전용 요소 추가에 적합
- 가장 충돌이 적은 방식

---

## release 커밋

```bash
git checkout release
git merge main
git add master.oas
git commit -m "release: vX.X tapeout"
git push
```

---

## 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| KLayout 시작 시 라이브러리 없음 | 매크로 미등록 | Macro Development에서 `macros/` 경로 추가 후 재시작 |
| 셀 배치 후 내용이 비어 있음 | LFS 포인터 파일 | `git lfs pull` 실행 |
| 레이어 색상이 다름 | `tech/layers.lyp` 미적용 | `Edit > Layer Properties > Load` → `tech/layers.lyp` 선택 |
