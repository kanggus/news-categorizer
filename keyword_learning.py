from konlpy.tag import Okt
from collections import Counter, defaultdict
import os
import json
import re

def load_articles_by_category(path):
    category_articles = defaultdict(list)
    current_category = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("## "):
                current_category = line.strip().replace("## ", "")
            elif line.strip().startswith("- **") and current_category:
                title = re.sub(r"[\-*•]+", "", line).strip()
                category_articles[current_category].append(title)
    return category_articles

def extract_keywords(texts):
    okt = Okt()
    nouns = []
    for text in texts:
        nouns += okt.nouns(text)
    counter = Counter(nouns)
    return counter.most_common(20)

def update_categories_file(category_keywords):
    if not os.path.exists("categories.txt"):
        return

    with open("categories.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    cat_dict = {}
    for line in lines:
        if ':' in line:
            cat, kws = line.strip().split(":", 1)
            cat_dict[cat] = set(k.strip() for k in kws.split(","))

    for cat, keywords in category_keywords.items():
        if cat not in cat_dict:
            cat_dict[cat] = set()
        cat_dict[cat].update(keywords)

    with open("categories.txt", "w", encoding="utf-8") as f:
        for cat, kws in sorted(cat_dict.items()):
            f.write(f"{cat}: {','.join(sorted(set(kws)))}\n")

    with open("output/자동갱신.log", "a", encoding="utf-8") as log:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for cat, kws in category_keywords.items():
            log.write(f"[{now}] {cat} 카테고리 키워드 반영: {', '.join(kws)}\n")

def learn_keywords():
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    filepath = f"output/{today}-news.md"
    if not os.path.exists(filepath):
        print(f"[!] 오늘 뉴스 파일이 존재하지 않습니다: {filepath}")
        return

    print(f"🔍 {filepath} 에서 카테고리별 키워드 추출 중...")
    articles_by_category = load_articles_by_category(filepath)

    category_keywords = {}
    for cat, articles in articles_by_category.items():
        top_keywords = [word for word, _ in extract_keywords(articles) if len(word) > 1]
        category_keywords[cat] = top_keywords[:10]

    update_categories_file(category_keywords)

    with open(f"output/{today}-keywords.json", "w", encoding="utf-8") as f:
        json.dump(category_keywords, f, ensure_ascii=False, indent=2)

    print(f"✅ 카테고리별 키워드 추천 결과 저장 완료.")
