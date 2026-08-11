# 프로젝트 페이지 (gh-pages)

이 브랜치는 GitHub Pages 로 배포되는 정적 사이트입니다.
소스 코드/레이아웃 파일은 `main` 브랜치에 있고, 이 브랜치에는 웹 페이지 파일만 들어갑니다.

- 배포 주소: https://kyonggi-eon.github.io/hw_2026/
- 템플릿: [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template)

## 구조

| 경로 | 설명 |
|------|------|
| `index.html` | 페이지 전체 내용. 여기만 고치면 됩니다 |
| `static/css/` | Bulma + 템플릿 스타일 (건드릴 일 없음) |
| `static/js/` | 캐러셀·복사 버튼 등 스크립트 (건드릴 일 없음) |
| `static/images/` | 스크린샷, 파비콘, 소셜 미리보기 이미지 |
| `static/pdfs/` | 보고서·포스터 PDF |
| `static/videos/` | 발표/데모 영상 |
| `.nojekyll` | GitHub Pages 의 Jekyll 처리를 끔 (지우지 말 것) |

## 수정 방법

```bash
git fetch origin
git switch gh-pages
# index.html 수정, static/ 에 이미지·PDF 추가
git add -A && git commit -m "페이지 업데이트"
git push origin gh-pages
```

푸시하면 1~2분 뒤 사이트에 반영됩니다.

`index.html` 안의 `TODO:` 주석이 아직 채워야 할 부분입니다.
발표 영상·포스터·결과 이미지 섹션은 자료가 없어서 HTML 주석으로 막아뒀습니다.
해당 파일을 `static/` 에 올린 뒤 주석(`<!--` ... `-->`)만 지우면 켜집니다.

## 로컬 미리보기

```bash
python3 -m http.server 8000
# http://localhost:8000 접속
```
