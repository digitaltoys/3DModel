# 민결 토끼 키링 — 얇은 3D 프린트 모델

제공된 이미지를 참고해 SolidCraft MCP v0.22.0으로 재구성한 단일 몸체 모델입니다. 이미지의 조형을 단순화했으며 원본과 완전히 동일한 곡면 복제는 아닙니다.

- 실제 외형: 약 45 × 54.9mm (귀와 고리 포함)
- 받침 2mm, 전체 최대 두께 3mm
- 고리 구멍: 약 3.3mm, 주변 벽 두께 약 2.6mm
- 민결 / MINGYEOL 양각, 눈·코·입 음각, 평평한 뒷면

## 파일

- `mingyeol-bunny-thin.stl`: 일반 슬라이서용, 단위 mm
- `mingyeol-bunny-thin.3mf`: 3MF 모델 (프린터별 슬라이싱 설정 미포함)
- `mingyeol-bunny-thin.solidcraft`: 편집 가능한 SolidCraft 원본
- `mingyeol-bunny-thin.step`: 다른 CAD에서 편집할 수 있는 STEP
- `preview-top.png`, `preview-iso.png`: SolidCraft 실제 렌더
- `print-validation.json`: STL 검증 결과

## 권장 출력

평평한 뒷면을 베드에 놓고 장식이 위로 향하게 출력합니다. PLA 또는 PETG, 0.4mm 노즐, 0.12~0.16mm 레이어, 벽 3줄, 인필 100%를 시작점으로 권장합니다. 서포트는 필요하지 않습니다. 작은 영문 글씨는 0.2mm 노즐에서 더 선명하게 출력됩니다. 단색으로 출력할 수 있으며 참고 이미지처럼 여러 색을 사용하려면 슬라이서에서 면별 색칠 또는 출력 후 도색이 필요합니다.

STL의 닫힌 표면, 일관된 면 방향, 연결된 몸체 1개를 확인했습니다. 실제 프린터 출력과 고리 내구성은 아직 검증하지 않았습니다.

## 재생성

Python 가상 환경에 `shapely fonttools`를 설치하고 `build_keychain.py`를 실행합니다. SolidCraft 실행 파일 및 허용 경로는 `sc_client.py`에 정의되어 있습니다. 한국어 글꼴은 시스템 Noto Sans CJK Black을 사용합니다.
