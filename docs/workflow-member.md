# 팀원 작업 가이드

## 브랜치 만들기 (최초 1회)

```bash
git checkout main
git pull
git checkout -b feature/자기이름   # 예: feature/홍길동
git push -u origin feature/자기이름
```

## 일상 작업 흐름

```bash
# 1. 본인 feature 브랜치로 이동
git checkout feature/자기이름

# 2. main 최신 변경사항 반영
git pull origin main

# 3. KLayout 실행 → 라이브러리 자동 등록 (register_libraries.lym)

# 4. 본인 담당 파일만 편집
#    layouts/자기이름.oas 또는 layouts/자기이름.gds
#    ※ 다른 팀원 파일은 절대 수정하지 않을 것 (충돌 원인)

# 5. 커밋 & push (본인 feature 브랜치로)
git add layouts/자기이름.oas
git commit -m "feat: 작업 내용 요약"
git push origin feature/자기이름
```

## main으로 PR 보내기

GitHub에서 `feature/자기이름` → `main` PR 생성 후 통합 담당자 리뷰 요청.

## 충돌(conflict) 발생 시

`git pull origin main` 도중 충돌이 나는 경우:

1. `git status`로 충돌 파일 확인
2. 충돌 파일이 **본인 담당 파일**인 경우 → 본인 버전 선택:
   ```bash
   git checkout --ours layouts/자기이름.oas
   git add layouts/자기이름.oas
   git commit -m "merge: resolve conflict, keep my version"
   ```
3. 충돌 파일이 **다른 팀원 파일**인 경우 → 상대방 버전 선택:
   ```bash
   git checkout --theirs layouts/상대방이름.oas
   git add layouts/상대방이름.oas
   git commit -m "merge: resolve conflict, keep upstream version"
   ```

`--ours` / `--theirs` 중 하나를 고르면 git이 자동으로 충돌을 해소한다.
`.oas`/`.gds`는 바이너리 파일이라 텍스트 편집으로 직접 해결이 불가능하므로 반드시 이 방식으로 처리한다.

**충돌을 애초에 피하려면:** 본인 담당 파일(`layouts/자기이름.*`)만 수정하고, 다른 팀원 파일은 건드리지 않는다.

---

## 라이브러리 갱신 (KLayout 재시작 없이)

팀원이 파일을 업데이트해서 `git pull`을 받았다면, KLayout을 껐다 켜지 않아도 된다.

```bash
git pull
# KLayout에서:
# Tools > Reload Libraries 클릭
# → 완료 다이얼로그 확인
# → master.oas에 자동 반영
```

> **주의:** `Reload Libraries` 전에 반드시 `git pull`을 먼저 실행해야 최신 파일이 반영된다.

---

## 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| KLayout 시작 시 라이브러리 없음 | 매크로 미등록 | Macro Development에서 `macros/` 경로 추가 후 재시작 |
| `"파일이 너무 작습니다"` 로그 | Git LFS 미설치 | `git lfs install && git lfs pull` |
| 레이어 색상이 다름 | `tech/layers.lyp` 미적용 | `Edit > Layer Properties > Load` → `tech/layers.lyp` 선택 |
| Reload 후에도 변경사항 없음 | git pull 미실행 | `git pull` 먼저 실행 후 다시 Reload |
