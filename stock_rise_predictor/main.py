import db
import title_evaluator
import deep_evaluator

def main():
    conn = db.create_database()
    title_evaluator.scrape(conn)
    title_evaluator.evaluate_simply(conn)
    deep_evaluator.analyze_top_disclosure(conn)
    conn.close()

if __name__ == "__main__":
    main()