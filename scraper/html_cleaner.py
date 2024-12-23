import re
from bs4 import BeautifulSoup

def extract_clean_text(html):
    """
    Extrait et nettoie le texte d'un document HTML :
    - Supprime <script>, <style>, <noscript>, <form>.
    - Supprime <header> et <footer>.
    - Ajoute des séparateurs avant les balises de titre.
    - Réduit les sauts de ligne successifs à un seul.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Balises à supprimer
    for tag_name in ["script", "style", "noscript", "form"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Se focaliser sur <body> ou fallback sur la racine
    body = soup.find("body")
    if not body:
        body = soup

    # Supprimer <header> et <footer>
    for tag_name in ["header", "footer"]:
        for tag in body.find_all(tag_name):
            tag.decompose()

    # Insérer des séparateurs avant les balises de titre
    first_h1_encountered = False
    for heading in body.find_all(re.compile(r'^h[1-6]$')):
        heading_text = heading.get_text(strip=True)
        if not heading_text:
            continue

        heading.clear()

        if heading.name == "h1" and not first_h1_encountered:
            heading.string = f"****\n{heading_text}\n****"
            first_h1_encountered = True
        else:
            heading.string = f"-----\n{heading_text}\n-----"

    # Extraire le texte
    text = body.get_text(separator="\n")

    # Réduire les multiples retours à la ligne
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = [line for line in lines if line]
    cleaned_text = "\n".join(cleaned_lines)

    return cleaned_text
