from scraper.site_scraper import SiteScraper

def main():
    user_url = input("Entrez le domaine du site à scraper (ex. https://www.example.com) : ")
    
    if not user_url.startswith("http://") and not user_url.startswith("https://"):
        user_url = "https://" + user_url

    dossier_de_sortie = "pages_scrape"
    scraper = SiteScraper(start_url=user_url, output_folder=dossier_de_sortie)
    scraper.scrape_site()

if __name__ == "__main__":
    main()
