# 필요 기능
# 1. dart api를 이용해 처음 데이터셋 받아오는 기능
#   - 필수 요청정보 : 정식명칭(응답키 : corp_name), 영문명칭(응답키 : corp_eng_name), 고유번호(응답키 : corp_code) <- https://opendart.fss.or.kr/api/corpCode.xml
#      - 업종코드 <- 고유번호(응답키 : induty_code) 를 기반으로 dataset 채우기 <- https://opendart.fss.or.kr/api/company.json
# 2. 특정 기업을 검색시
#   2-1. update내역이 있는지 확인하고 있다면 받아올 것
#   2-2. 이후 RAG -> 요약된 정보 생성



