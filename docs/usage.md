# 설치 및 작업 가이드

## 1회 설치

### Linux / macOS

```bash
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
git pull                           # 최신 변경사항 가져오기
# KLayout 실행 → 자동으로 master.oas 생성 및 통합 뷰 표시
# layouts/member_이름.oas 편집
git add layouts/member_이름.oas
git commit -m "feat: 작업 내용 요약"
git push
```

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
