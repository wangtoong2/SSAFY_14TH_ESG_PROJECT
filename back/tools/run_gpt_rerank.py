#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# =========================================================
# 1. 프로젝트 루트(back/)를 PYTHONPATH에 추가
# =========================================================
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# =========================================================
# 2. .env 로드
# =========================================================
env_file = ROOT / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

# =========================================================
# 3. Django 설정
# =========================================================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ESG.settings")

import django
django.setup()

# =========================================================
# 4. 서비스 import (이제 에러 안 남)
# =========================================================
from companies.services import (
    recommend_companies,
    call_gpt_for_recommendations,
)

# =========================================================
# 5. 사용자 선호 설정
# =========================================================
prefs = {
    "desired_industries": ["IT"],
    "desired_size": "중견",
    "location": "서울특별시",
}

# =========================================================
# 6. 로컬 점수 기반 추천
# =========================================================
print("📌 로컬 추천 결과 (Top 5)")
candidates = recommend_companies(prefs, top_n=20)

for c in candidates[:5]:
    print(f"- {c['corp_name']} | score={c['score']}")

# =========================================================
# 7. GPT 재랭킹 (진짜 추천)
# =========================================================
print("\n🤖 GPT 추천 결과 (Top 5)")
result = call_gpt_for_recommendations(
    prefs=prefs,
    candidates=candidates,
    top_n=5,
)

print(json.dumps(result, ensure_ascii=False, indent=2))
