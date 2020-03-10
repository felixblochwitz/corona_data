import corona

new_data = corona.scraper()
corona.update_db(new_data)
