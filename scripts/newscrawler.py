from datetime import datetime
import pandas as pd

from gnews import GNews


class NewsCrawler:
    def __init__(self):
        self.news = pd.DataFrame()

    def crawl_custom_date(self, keyword, start_date, end_date, max_results=100):
        print("Fetching Data from GNews...")
        gnews = GNews(language='id', country='ID', start_date=start_date, end_date=end_date, max_results=max_results)
        crawled_news = gnews.get_news(keyword)
        self.__scrape_newsdata(crawled_news, gnews)
        print("found", len(self.news), "news")
        return self.news

    def __scrape_newsdata(self, crawled_news, gnews):
        scraped_news = []
        failed_fetch = []
        for i in range(len(crawled_news)):
            try:
                article = gnews.get_full_article(crawled_news[i]['url'])
                date = datetime.strptime(crawled_news[i]['published date'], '%a, %d %b %Y %H:%M:%S GMT')
                date = datetime.strftime(date, '%Y-%m-%d')
                data = {
                    'title': article.title,
                    'publisher': crawled_news[i]['publisher']['title'],
                    'url': crawled_news[i]['url'],
                    'image': article.top_image,
                    'published_date': date,
                    'text': article.text
                }
                scraped_news.append(data)
                self.news = pd.DataFrame(scraped_news)
            except:
                print("Failed to fetch at i =", i, "with news title \"", crawled_news[i]['title'], "\"")
                failed_fetch.append(i)