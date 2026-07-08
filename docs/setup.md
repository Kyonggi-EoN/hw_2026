# 설치 가이드

## Linux / macOS

```bash
ln -s /path/to/repo/macros/register_libraries.lym ~/.klayout/macros/register_libraries.lym
```

## Windows

1. KLayout 실행
2. **Macros > Macro Development**
3. 좌측 패널에서 **Python > Local > Add Location** (우클릭 메뉴)
4. 저장소의 `macros/` 폴더 경로 추가
5. KLayout 재시작

## KLayout 버전 확인

KLayout에서 **Help > About KLayout**을 열어 버전을 확인한다. `Reload Libraries`는 KLayout `0.27.8` 이상의 `Library.refresh()` API를 기준으로 동작한다.

## Reload Libraries 버튼이 보이지 않을 때

KLayout을 켠 직후 메뉴가 아직 준비되지 않은 경우 매크로가 버튼 등록을 재시도한다. 그래도 보이지 않으면 **Macros > Macro Development**에서 `register_libraries.lym`을 한 번 수동 실행한 뒤 **Tools > Reload Libraries**를 확인한다.
