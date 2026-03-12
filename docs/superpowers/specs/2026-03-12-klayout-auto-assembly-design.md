# KLayout 자동 통합 뷰 시스템 설계

**날짜:** 2026-03-12
**상태:** 확정

---

## 개요

20명 이상의 팀원이 각자 담당 블록을 별도 `.oas` 파일로 작업하고, KLayout 시작 시 매크로가 자동으로 모든 파일을 병합해 `master.oas`를 생성한다. 팀원은 항상 최신 전체 레이아웃을 확인할 수 있으며, 검증 후 수동으로 `release` 브랜치에 push한다.

---

## 디렉토리 구조

```
klayout_test/
├── master.oas                  # 전체 통합 뷰 (매크로 자동 생성/갱신, Git LFS)
├── layouts/
│   ├── member_A.oas            # 팀원별 담당 블록 (Git LFS)
│   ├── member_B.oas
│   └── ...
├── tech/
│   └── layers.lyp              # 공통 레이어 속성
├── macros/
│   └── autoload.lym            # KLayout 시작 시 자동 실행 매크로
└── docs/
    ├── README.md               # 프로젝트 구조 개요
    ├── usage.md                # 설치 및 작업 가이드
    └── coordinate_guide.md     # 좌표 규칙 및 블록 할당표
```

---

## 매크로 동작 (`autoload.lym`)

KLayout 시작 시 자동 실행되며 다음 순서로 동작한다:

1. 매크로 파일 위치 기준으로 저장소 루트 경로 계산
2. `layouts/` 디렉토리의 모든 `.oas` 파일 탐색
3. 각 파일을 읽어 셀 데이터 병합
4. `tech/layers.lyp` 레이어 속성 적용
5. 병합 결과를 `master.oas`로 저장 (저장소 최상위)
6. `master.oas`를 뷰에 열어 전체 통합 화면 표시
7. 파일 누락/오류 발생 시 KLayout 메시지 박스로 안내

---

## Git 관리

### `.gitattributes`
- `master.oas`, `layouts/*.oas` — Git LFS (바이너리 대용량 파일)
- `macros/*.lym`, `tech/*.lyp`, `docs/*.md` — 일반 텍스트, LF 줄바꿈

### 브랜치 전략

```
main 브랜치
  └─ 팀원 개인 .oas 작업 및 push
  └─ KLayout 시작 시 master.oas 자동 갱신
  └─ master.oas도 main에 commit/push

release 브랜치
  └─ 검증 완료 후 수동으로 main → release merge 또는 push
  └─ 외부 공유/납품용 최종 산출물
```

---

## 좌표 규칙 (coordinate_guide.md에 상세 기술)

- 전체 칩 플로어플랜을 `docs/coordinate_guide.md`에 정의
- 팀원마다 담당 블록의 **절대좌표 범위**를 사전 할당
- 각자 절대좌표로 작업 → 병합 시 자동으로 올바른 위치에 배치
- 좌표 범위 외 작업 금지 (충돌 방지)

---

## 설치 (팀원 1회 설정)

1. 저장소 clone
2. KLayout 실행 → Tools > Macro Development > 경로에 `macros/` 폴더 추가
3. KLayout 재시작 → 자동 실행 확인

---

## 오류 처리

| 상황 | 동작 |
|------|------|
| `layouts/`에 `.oas` 파일 없음 | 경고 메시지 후 빈 뷰 |
| 특정 파일 읽기 실패 | 해당 파일 건너뛰고 나머지 병합, 파일명 포함 경고 |
| `layers.lyp` 없음 | 레이어 속성 미적용 경고, 병합은 계속 진행 |
| `master.oas` 쓰기 실패 | 오류 메시지 표시, 뷰는 메모리에서만 표시 |

---

## 미결 사항

- 팀원별 담당 블록 좌표 범위 확정 (`coordinate_guide.md` 작성 필요)
- `master.oas`의 `main` 브랜치 commit 주기 결정 (매 시작 시 vs 수동)
