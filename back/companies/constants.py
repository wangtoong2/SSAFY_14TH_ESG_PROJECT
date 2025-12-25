KSIC_SECTION_MAP = {
    # A. 농업, 임업 및 어업 (01~03)
    "01": "농업, 임업 및 어업",

    # B. 광업 (05~09)
    "05": "광업",  # ※ 엄밀히는 05~09 전체가 광업

    # C. 제조업 (10~34)
    "10": "제조업",

    # D. 전기, 가스, 증기 및 공기조절 공급업 (35)
    "35": "전기, 가스, 증기 및 공기조절 공급업",

    # F. 건설업 (41~42)
    "41": "건설업",

    # G. 도매 및 소매업 (45~47)
    "45": "도매 및 소매업",

    # H. 운수 및 창고업 (49~52)
    "49": "운수 및 창고업",

    # I. 숙박 및 음식점업 (55~56)
    "55": "숙박 및 음식점업",

    # J. 정보통신업
    "58": "출판, 영상, 방송통신 및 정보서비스업",
    "62": "소프트웨어 개발 및 공급업",
    "63": "정보서비스업",

    # K. 금융 및 보험업 (64~66)
    "64": "금융 및 보험업",
    "66": "금융 및 보험 관련 서비스업",

    # L. 부동산업 (68)
    "68": "부동산업",

    # M. 전문, 과학 및 기술 서비스업 (70~74)
    "70": "전문, 과학 및 기술 서비스업",
    "72": "연구개발업",
    "73": "광고 및 시장조사",
    "74": "기타 전문, 과학 및 기술 서비스업",
}


# Two-digit KSIC section ranges (major industry sections)
# Source concept: KSIC sections are grouped by leading 2 digits.
KSIC_SECTION_RANGES = [
    (1, 3, "농업, 임업 및 어업"),
    (5, 9, "광업"),
    (10, 34, "제조업"),
    (35, 35, "전기, 가스, 증기 및 공기조절 공급업"),
    (41, 42, "건설업"),
    (45, 47, "도매 및 소매업"),
    (49, 52, "운수 및 창고업"),
    (55, 56, "숙박 및 음식점업"),
    (58, 63, "정보통신업"),
    (64, 66, "금융 및 보험업"),
    (68, 68, "부동산업"),
    (70, 74, "전문, 과학 및 기술 서비스업"),
]


def classify_ksic_section(industry_code):
    """Return a human-readable KSIC major section name from an industry code.

    Accepts strings like "25931", "42", 5811, etc.
    Uses the first two digits (with zero-padding if needed).
    Returns None when it cannot be classified.
    """

    if industry_code is None:
        return None

    s = str(industry_code).strip()
    if not s:
        return None

    digits = ''.join(ch for ch in s if ch.isdigit())
    if not digits:
        return None

    if len(digits) == 1:
        prefix = '0' + digits
    else:
        prefix = digits[:2]

    # quick direct map (for specific prefixes)
    if prefix in KSIC_SECTION_MAP:
        return KSIC_SECTION_MAP[prefix]

    try:
        code2 = int(prefix)
    except Exception:
        return None

    for start, end, label in KSIC_SECTION_RANGES:
        if start <= code2 <= end:
            return label
    return None
