import os
import re
import requests
from collections import deque
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

from .html_cleaner import extract_clean_text


class SiteScraper:
    """
    Classe qui gère l'exploration d'un site Web
    et l'extraction du texte de ses pages.
    """
    def __init__(self, start_url, output_folder="pages_scrape"):
        """
        :param start_url: URL de départ (ex: "https://example.com")
        :param output_folder: Dossier de sortie où sauvegarder les fichiers .txt
        """
        self.start_url = start_url
        self.output_folder = output_folder
        self.domain = urlparse(start_url).netloc

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        self.visited = set()

    def scrape_site(self):
        """
        Lance le processus d'exploration (BFS) du site.
        Pour chaque page, on extrait le contenu nettoyé et on le sauvegarde.
        """
        to_visit = deque([self.start_url])
        self.visited.add(self.start_url)

        while to_visit:
            current_url = to_visit.popleft()
            print(f"Scraping: {current_url}")

            html = self._fetch_page(current_url)
            if not html:
                continue

            # Extraire le texte propre via html_cleaner
            page_text = extract_clean_text(html)

            # Sauvegarder dans un fichier
            self._save_page_text(current_url, page_text)

            # Récupérer et empiler les nouveaux liens internes
            new_links = self._get_internal_links(html, current_url)
            for link in new_links:
                if link not in self.visited:
                    self.visited.add(link)
                    to_visit.append(link)

    def _fetch_page(self, url):
        """
        Récupère le contenu HTML d'une page.
        Retourne le HTML ou None en cas d'erreur.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Erreur lors de la requête : {e}")
            return None

    def _get_internal_links(self, html, base_url):
        """
        Retourne une liste d'URLs internes (même domaine).
        """
        soup = BeautifulSoup(html, "html.parser")
        links = []

        for tag_a in soup.find_all("a"):
            href = tag_a.get("href")
            if not href:
                continue

            absolute_url = urljoin(base_url, href)
            parsed_url = urlparse(absolute_url)

            # Nettoyage des paramètres/ancre
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            if self._is_same_domain(clean_url):
                links.append(clean_url)

        return links

    def _is_same_domain(self, url):
        """
        Vérifie que 'url' appartient au même domaine
        que celui de 'self.domain'.
        """
        return urlparse(url).netloc == self.domain

    def _normalize_filename(self, url):
        """
        Transforme l'URL en un nom de fichier valide.
        """
        filename = re.sub(r'^https?://', '', url)
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        return filename

    def _save_page_text(self, url, text_content):
        """
        Sauvegarde le contenu texte dans un fichier .txt
        dérivé de l'URL.
        """
        filename = self._normalize_filename(url) + ".txt"
        file_path = os.path.join(self.output_folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
