## Learn English API
[![Python 3.8](https://img.shields.io/badge/python-v3.8-blue)](https://www.python.org/downloads/release/python-380/)
### 주요 기능
1. 구동사 검색
2. 구동사 퀴즈
3. 구동사 저장 후 공부하기
### 기술
* MongoDB
  * 구동사 저장
    * 어드민 페이지에서 구동사 등록 후 크롤러 스크립트 실행(Python Paramiko)
    * 크롤러를 통해 구동사의 의미와 예제 저장
  * 유저 구동사 좋아요 저장
* Redis
  * 유저 세션 저장
* Docker-compose
  * flask app(gunicorn) - redis - nginx
* Pytest 
  * 각 엔드포인트 테스트(리소스 생성,추가,수정,삭제)
  * 헬퍼 함수 테스트
  * 픽스쳐 - API context(test), TEST DB
* [크롤러 스크립트](https://github.com/daehan0226/learn-english-crawler)
  * aiohttp 를 활용한 코루틴 함수로 데이터 수집 시간 단축