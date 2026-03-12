# KLayout 반도체 설계 저장소

## 개요

20명 이상의 팀원이 각자 담당 블록을 별도 `.oas` 파일로 작업하고,
KLayout 시작 시 자동으로 전체 레이아웃을 통합해 확인할 수 있는 협업 환경.

## 디렉토리 구조

| 경로 | 설명 |
|------|------|
| `layouts/` | 팀원별 담당 블록 `.oas` 파일 (Git LFS) |
| `tech/layers.lyp` | 공통 레이어 속성 (색상, 스타일) |
| `tech/block_assignments.json` | 팀원별 좌표 범위 할당표 (매크로 참조) |
| `macros/autoload.lym` | KLayout 시작 시 자동 실행 매크로 |
| `master.oas` | 전체 통합 뷰 (로컬 자동 생성, git 추적 안 함) |
| `docs/` | 문서 |

## 브랜치 전략

- `main`: 팀원 일상 작업 브랜치
- `release`: 검증 완료 산출물 (통합 담당자만 push)

## 관련 문서

- [설치 및 사용 가이드](usage.md)
- [좌표 규칙](coordinate_guide.md)
