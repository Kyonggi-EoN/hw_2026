# KLayout 반도체 설계 저장소

## 개요

20명 이상의 팀원이 각자 담당 블록을 별도 `.oas`/`.gds` 파일로 작업한다.
KLayout 시작 시 매크로가 각 파일을 셀 라이브러리로 자동 등록하고,
통합 담당자가 `master.oas`에서 블록을 배치·배선해 최종 tapeout 파일을 관리한다.

## 디렉토리 구조

| 경로 | 설명 |
|------|------|
| `layouts/` | 팀원별 담당 블록 `.oas`/`.gds` 파일 (Git LFS) |
| `tech/layers.lyp` | 공통 레이어 속성 (색상, 스타일) |
| `macros/register_libraries.lym` | KLayout 시작 시 자동 실행 — 셀 라이브러리 등록 |
| `master.oas` | 플로어플랜 — 라이브러리 셀 참조, 배선 포함 (통합 담당자 관리) |
| `docs/` | 문서 |

## 브랜치 전략

| 브랜치 | 역할 |
|--------|------|
| `feature/<이름>` | 팀원 개인 작업 |
| `main` | 팀 통합 — PR 필수 |
| `release` | tapeout 산출물 — 통합 담당자만, `master.oas` 포함 |

## 관련 문서

- [설치 및 사용 가이드](usage.md)
