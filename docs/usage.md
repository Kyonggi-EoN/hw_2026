# 설치 및 작업 가이드

## 1회 설치

### Linux / macOS

```bash
ln -s /path/to/repo/macros/register_libraries.lym ~/.klayout/macros/register_libraries.lym
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

# 2. KLayout 실행 → 라이브러리 자동 등록 (register_libraries.lym)

# 3. 본인 담당 파일 작업
#    layouts/자기이름.oas 편집

# 4. 저장 후 커밋 & push
git add layouts/자기이름.oas
git commit -m "feat: 작업 내용 요약"
git push
```

## 통합 담당자 작업 (master.oas 배치)

KLayout에서 `Edit > Cell > Instance...` 로 라이브러리 셀 배치 후 `master.oas`로 저장, release 브랜치 PR.

## Release 절차 (통합 담당자)

```bash
git checkout release
git merge main
git add master.oas
git commit -m "release: vX.X 통합 산출물"
git push
```

## 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| "저장소 루트를 찾을 수 없습니다" | 매크로 경로 설정 오류 | 설치 단계 재확인 |
| `master.oas` 저장 실패 | 쓰기 권한 또는 디스크 공간 | 경고 무시해도 뷰는 정상 |
| 레이어 색상이 다름 | `layers.lyp` 미적용 | `tech/layers.lyp` 존재 확인 |
| 좌표 범위 초과 경고 | 블록 경계 위반 | `docs/coordinate_guide.md` 참고 |
| 라이브러리 목록에 셀이 없음 | 매크로 미등록 또는 LFS 포인터 파일 | Macro Development에서 macros/ 경로 확인, git lfs pull 실행 |
| "파일이 너무 작습니다" 로그 | Git LFS 미설치 | `git lfs install && git lfs pull` |
