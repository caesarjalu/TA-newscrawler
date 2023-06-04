from firebase_admin import credentials, initialize_app, firestore
from datetime import datetime


class FirestoreHandler:
    def __init__(self, logger):
        try:
            cred = credentials.Certificate("../resource/firebase-secretkey.json")
            initialize_app(cred)
            self.db = firestore.client()
            self.logger = logger
        except Exception as e:
            self.logger.error("Failed to init FirestoreHandler:")
            self.logger.error(e)

    def insert(self, df):
        newsdict = df.to_dict('index')
        year = datetime.strftime(newsdict[0]["published_date"], "%Y")
        try:
            newscount_year_data = self.db.collection("newscount").document(year).get().to_dict()
        except Exception as e:
            self.logger.error("Failed to get newscount:")
            self.logger.error(e)
            return
        self.logger.debug("Inserting " + str(len(newsdict)) + " data into firestore...")
        batch = self.db.batch()
        for data in newsdict.values():
            try:
                batch.set(self.db.collection("newsdata").document(), data)
                for loc in data["location"]:
                    newscount_year_data[loc] += 1
            except Exception as e:
                self.logger.error("Failed to insert news \"" + data['title'] + "\":")
                self.logger.error(e)
        try:
            batch.set(self.db.collection("newscount").document(year), newscount_year_data)
        except Exception as e:
            self.logger.error("Failed to insert newscount:")
            self.logger.error(e)
        try:
            batch.commit()
            self.logger.info("Successfully inserting " + str(len(newsdict)) + " data into firestore")
        except Exception as e:
            self.logger.error("Failed to commit:")
            self.logger.error(e)
