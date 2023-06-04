from datetime import datetime
import pandas as pd
from gnews import GNews


class NewsCrawler:
    def __init__(self, logger, start_date, end_date, max_results=100):
        self.logger = logger
        self.news = pd.DataFrame(columns=['title', 'publisher', 'url', 'image', 'published_date', 'text'])
        self.gnews = GNews(language='id', country='ID', start_date=start_date, end_date=end_date,
                           max_results=max_results)

    def crawl_news(self, keywords: list):
        self.logger.debug("Fetching Data from GNews...")
        for keyword in keywords:
            self.logger.info("Keyword: " + keyword)
            crawled_news = self.gnews.get_news(keyword)
            self.logger.debug("Scrape the news...")
            self.news = pd.concat([self.news, self.__scrape_newsdata(crawled_news)], ignore_index=True)
        self.news = self.news.dropna(subset=['title', 'text'])
        self.news = self.news.drop_duplicates(subset='title')
        self.news = self.news.reset_index(drop=True)
        self.logger.info("Found " + str(len(self.news)) + " news:")
        for idx in self.news.index:
            self.logger.info(self.news['title'][idx] + " - " + self.news['url'][idx])
        return self.news

    def __scrape_newsdata(self, crawled_news):
        scraped_news = []
        for news in crawled_news:
            try:
                article = self.gnews.get_full_article(news['url'])
                date = datetime.strptime(news['published date'], '%a, %d %b %Y %H:%M:%S GMT')
                # date = datetime.strftime(date, '%Y-%m-%d')
                data = {
                    'title': article.title,
                    'publisher': news['publisher']['title'],
                    'url': news['url'],
                    'image': article.top_image,
                    'published_date': date,
                    'text': article.text
                }
                scraped_news.append(data)
            except Exception as e:
                self.logger.error("Failed to fetch news \"" + news['title'] + "\":")
                self.logger.error(e)
        scraped_news = self.__filter_word(scraped_news, 'stunt')
        return pd.DataFrame(scraped_news)

    def __filter_word(self, newsdata, filter_word):
        for data in newsdata:
            if data['title'].casefold().find(filter_word) == -1:
                if data['text'].casefold().find(filter_word) == -1:
                    self.logger.warning('"' + data['title'] + '" does not contain word "' + filter_word + '"')
                    newsdata.remove(data)
        return newsdata
