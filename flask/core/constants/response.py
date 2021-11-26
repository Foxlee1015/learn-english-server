status = {
    "SUCCESS": 200,  # GET - DATA OR EMPTY LIST
    "CREATED": 201,  # POST
    "NO_CONTENT": 204,  # DELETE, PUT
    "FAIL": 400,  # GENERAIL FAIL - CLIENT ERROR
    "NO_AUTH": 401,  # LOGIN NEEDED
    "FORBIDDEN": 403,  # ADMIN ONLY
    "NOT_FOUND": 404,  # NOT FOUND BY IDENTIFIER
    "SEVER_ERROR": 500,  # SEVER ERROR
}

message = {
    "kr": {
        "SUCCESS": "성공",  # GET - DATA OR EMPTY LIST
        "CREATED": "생성",  # POST
        "NO_CONTENT": "데이터 없음",  # DELETE, PUT
        "FAIL": "실패",  # GENERAIL FAIL - CLIENT ERROR
        "NO_AUTH": "로그인이 필요합니다.",  # LOGIN NEEDED
        "FORBIDDEN": "접근 권한이 없습니다.",  # ADMIN ONLY
        "NOT_FOUND": "원하시는 데이터를 찾지 못했습니다.",  # NOT FOUND BY IDENTIFIER
        "SEVER_ERROR": "죄송합니다. 다음에 다시 시도해주세요.",  # SEVER ERROR
    },
    "en": {
        "SUCCESS": "Success",  # GET - DATA OR EMPTY LIST
        "CREATED": "Created",  # POST
        "NO_CONTENT": "No content",  # DELETE, PUT
        "FAIL": "Fail",  # GENERAIL FAIL - CLIENT ERROR
        "NO_AUTH": "Please login first",  # LOGIN NEEDED
        "FORBIDDEN": "No permission",  # ADMIN ONLY
        "NOT_FOUND": "Couldn't find what you want",  # NOT FOUND BY IDENTIFIER
        "SEVER_ERROR": "Oops, something went wrong",  # SEVER ERROR
    },
}
