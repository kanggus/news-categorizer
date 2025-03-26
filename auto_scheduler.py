import schedule
import time
import main
import keyword_learning

def job():
    print("뉴스 수집 및 저장 시작...")
    main.main()
    print("키워드 자동 학습 시작...")
    keyword_learning.learn_keywords()

schedule.every().day.at("06:00").do(job)

print("⏰ 매일 오전 6시에 자동 뉴스 수집이 실행됩니다.")
while True:
    schedule.run_pending()
    time.sleep(60)
