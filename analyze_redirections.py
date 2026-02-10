#!/usr/bin/env python3
"""
Script d'analyse des redirections SEO
Compare les URLs du site actuel (prod) avec le nouveau site (preprod)
pour identifier les patterns de réécriture et générer un plan de redirections
"""

import csv
import re
from urllib.parse import urlparse
from collections import defaultdict
from difflib import SequenceMatcher


def clean_url(url):
    """Extrait le path d'une URL en enlevant le domaine"""
    parsed = urlparse(url)
    path = parsed.path
    if parsed.query:
        path += '?' + parsed.query
    return path


def load_urls_from_csv(filename):
    """Charge les URLs d'un fichier CSV avec leur statut"""
    urls = {}
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            address = row.get('Address', '')
            status = row.get('Status Code', '')
            indexability = row.get('Indexability', '')

            if address:
                path = clean_url(address)
                urls[path] = {
                    'address': address,
                    'status': status,
                    'indexability': indexability
                }
    return urls


def find_similar_url(old_path, new_urls, threshold=0.6):
    """Trouve l'URL la plus similaire dans le nouveau site (optimisé)"""
    best_match = None
    best_ratio = 0

    # Heuristiques pour limiter les comparaisons
    old_parts = old_path.lower().split('/')
    candidates = []

    # Chercher d'abord les URLs avec des parties communes
    for new_path in new_urls.keys():
        new_parts = new_path.lower().split('/')
        # Si au moins une partie est commune, c'est un candidat
        if any(part in new_parts for part in old_parts if part and len(part) > 3):
            candidates.append(new_path)

    # Si pas de candidats, prendre un échantillon aléatoire
    if not candidates:
        candidates = list(new_urls.keys())[:100]  # Limiter à 100 comparaisons max

    # Comparer avec les candidats
    for new_path in candidates:
        ratio = SequenceMatcher(None, old_path.lower(), new_path.lower()).ratio()
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = new_path

    return best_match, best_ratio


def extract_url_pattern(url):
    """Extrait un pattern générique d'une URL"""
    # Remplace les nombres par {id}
    pattern = re.sub(r'\d+', '{id}', url)
    # Remplace les slugs par {slug}
    pattern = re.sub(r'/[a-z0-9-]+/', '/{slug}/', pattern)
    return pattern


def group_by_pattern(url_list):
    """Groupe les URLs par pattern similaire"""
    patterns = defaultdict(list)
    for url in url_list:
        pattern = extract_url_pattern(url)
        patterns[pattern].append(url)
    return patterns


def analyze_redirections(prod_file, preprod_file):
    """Analyse principale des redirections"""
    print("Chargement des fichiers CSV...")
    prod_urls = load_urls_from_csv(prod_file)
    preprod_urls = load_urls_from_csv(preprod_file)

    print(f"URLs prod: {len(prod_urls)}")
    print(f"URLs preprod: {len(preprod_urls)}")

    # Filtrer les URLs indexables avec status 200
    prod_valid = {k: v for k, v in prod_urls.items()
                  if v['status'] == '200' and v['indexability'] == 'Indexable'}
    preprod_valid = {k: v for k, v in preprod_urls.items()
                     if v['status'] == '200' and v['indexability'] == 'Indexable'}

    print(f"\nURLs indexables (200) prod: {len(prod_valid)}")
    print(f"URLs indexables (200) preprod: {len(preprod_valid)}")

    # URLs qui disparaissent
    missing_urls = set(prod_valid.keys()) - set(preprod_valid.keys())
    # URLs qui apparaissent
    new_urls = set(preprod_valid.keys()) - set(prod_valid.keys())
    # URLs identiques
    unchanged_urls = set(prod_valid.keys()) & set(preprod_valid.keys())

    print(f"\nURLs disparues: {len(missing_urls)}")
    print(f"URLs nouvelles: {len(new_urls)}")
    print(f"URLs inchangées: {len(unchanged_urls)}")

    # Trouver les correspondances
    print("\nRecherche des correspondances...")
    redirections = []
    total = len(missing_urls)
    for i, old_path in enumerate(missing_urls, 1):
        if i % 100 == 0 or i == total:
            print(f"  Progression: {i}/{total} ({i*100//total}%)")
        new_path, similarity = find_similar_url(old_path, preprod_valid)
        redirections.append({
            'old': old_path,
            'new': new_path if new_path else 'NO_MATCH',
            'similarity': similarity,
            'old_full': prod_valid[old_path]['address'],
            'new_full': preprod_valid[new_path]['address'] if new_path else ''
        })

    # Trier par similarité décroissante
    redirections.sort(key=lambda x: x['similarity'], reverse=True)

    return {
        'redirections': redirections,
        'missing_urls': missing_urls,
        'new_urls': new_urls,
        'unchanged_urls': unchanged_urls,
        'prod_valid': prod_valid,
        'preprod_valid': preprod_valid
    }


def generate_report(results, output_file='redirections_report.md'):
    """Génère un rapport markdown des redirections"""
    redirections = results['redirections']

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Plan de Redirections SEO\n\n")
        f.write("## Statistiques\n\n")
        f.write(f"- **URLs disparues (nécessitent redirection):** {len(results['missing_urls'])}\n")
        f.write(f"- **URLs nouvelles:** {len(results['new_urls'])}\n")
        f.write(f"- **URLs inchangées:** {len(results['unchanged_urls'])}\n\n")

        # Redirections avec bon match
        high_matches = [r for r in redirections if r['similarity'] >= 0.7]
        medium_matches = [r for r in redirections if 0.5 <= r['similarity'] < 0.7]
        low_matches = [r for r in redirections if r['similarity'] < 0.5]

        f.write("## Correspondances par niveau de confiance\n\n")
        f.write(f"- **Haute confiance (≥70%):** {len(high_matches)}\n")
        f.write(f"- **Moyenne confiance (50-70%):** {len(medium_matches)}\n")
        f.write(f"- **Faible confiance (<50%):** {len(low_matches)}\n\n")

        # Redirections haute confiance
        if high_matches:
            f.write("## Redirections haute confiance (≥70%)\n\n")
            f.write("Ces URLs ont une forte correspondance et peuvent être redirigées automatiquement.\n\n")
            f.write("| Ancienne URL | Nouvelle URL | Similarité |\n")
            f.write("|-------------|-------------|------------|\n")
            for r in high_matches[:50]:  # Limiter à 50 pour la lisibilité
                f.write(f"| `{r['old']}` | `{r['new']}` | {r['similarity']:.1%} |\n")
            if len(high_matches) > 50:
                f.write(f"\n*... et {len(high_matches) - 50} autres redirections haute confiance*\n")
            f.write("\n")

        # Redirections moyenne confiance
        if medium_matches:
            f.write("## Redirections moyenne confiance (50-70%)\n\n")
            f.write("Ces URLs nécessitent une vérification manuelle.\n\n")
            f.write("| Ancienne URL | Nouvelle URL | Similarité |\n")
            f.write("|-------------|-------------|------------|\n")
            for r in medium_matches[:30]:
                f.write(f"| `{r['old']}` | `{r['new']}` | {r['similarity']:.1%} |\n")
            if len(medium_matches) > 30:
                f.write(f"\n*... et {len(medium_matches) - 30} autres redirections moyenne confiance*\n")
            f.write("\n")

        # URLs sans correspondance
        no_match = [r for r in redirections if r['new'] == 'NO_MATCH']
        if no_match:
            f.write("## URLs sans correspondance\n\n")
            f.write(f"Ces {len(no_match)} URLs n'ont pas de correspondance évidente. ")
            f.write("Il faudra déterminer manuellement la destination (redirection vers la page d'accueil, page similaire, ou erreur 410).\n\n")
            f.write("| Ancienne URL |\n")
            f.write("|-------------|\n")
            for r in no_match[:50]:
                f.write(f"| `{r['old']}` |\n")
            if len(no_match) > 50:
                f.write(f"\n*... et {len(no_match) - 50} autres URLs sans correspondance*\n")
            f.write("\n")

        # Analyse des patterns
        f.write("## Analyse des Patterns\n\n")
        f.write("### Patterns d'URLs disparues\n\n")
        missing_patterns = group_by_pattern(list(results['missing_urls']))
        common_missing = sorted(missing_patterns.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for pattern, urls in common_missing:
            f.write(f"- **{pattern}** ({len(urls)} URLs)\n")
        f.write("\n")

        f.write("### Patterns d'URLs nouvelles\n\n")
        new_patterns = group_by_pattern(list(results['new_urls']))
        common_new = sorted(new_patterns.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for pattern, urls in common_new:
            f.write(f"- **{pattern}** ({len(urls)} URLs)\n")
        f.write("\n")

    print(f"\nRapport généré: {output_file}")


def generate_csv_redirections(results, output_file='redirections_list.csv'):
    """Génère un fichier CSV avec toutes les redirections"""
    redirections = results['redirections']

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Old URL', 'New URL', 'Similarity', 'Redirect Type', 'Notes'])

        for r in redirections:
            redirect_type = '301'  # Permanent redirect par défaut
            notes = ''

            if r['similarity'] >= 0.7:
                notes = 'High confidence'
            elif r['similarity'] >= 0.5:
                notes = 'Medium confidence - manual check required'
                redirect_type = '301 (verify)'
            else:
                notes = 'Low confidence - manual review required'
                redirect_type = 'TBD'

            if r['new'] == 'NO_MATCH':
                notes = 'No match found - redirect to homepage or 410?'
                redirect_type = 'TBD'

            writer.writerow([
                r['old_full'],
                r['new_full'],
                f"{r['similarity']:.1%}",
                redirect_type,
                notes
            ])

    print(f"Fichier CSV généré: {output_file}")


if __name__ == '__main__':
    print("=" * 80)
    print("ANALYSE DES REDIRECTIONS SEO")
    print("=" * 80)
    print()

    results = analyze_redirections('prod_internal_all.csv', 'preprod_internal_all.csv')

    print("\n" + "=" * 80)
    print("GÉNÉRATION DES RAPPORTS")
    print("=" * 80)

    generate_report(results, 'redirections_report.md')
    generate_csv_redirections(results, 'redirections_list.csv')

    print("\n" + "=" * 80)
    print("ANALYSE TERMINÉE")
    print("=" * 80)
    print("\nFichiers générés:")
    print("- redirections_report.md : Rapport détaillé en markdown")
    print("- redirections_list.csv : Liste complète des redirections au format CSV")
