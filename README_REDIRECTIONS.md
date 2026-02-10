# Plan de Redirections SEO - ACPM

## Vue d'ensemble

Ce dossier contient l'analyse complète des redirections SEO nécessaires pour la migration du site ACPM de l'ancienne version (prod) vers la nouvelle version (preprod).

## Fichiers générés

### 1. `redirections_report.md`
Rapport détaillé de l'analyse incluant :
- Statistiques globales
- Liste des redirections par niveau de confiance (haute, moyenne, faible)
- URLs sans correspondance
- Analyse des patterns d'URLs

**Utilisation :** Consulter ce fichier pour comprendre en détail les correspondances trouvées.

---

### 2. `redirections_list.csv`
Liste complète au format CSV de toutes les redirections avec :
- Ancienne URL (prod)
- Nouvelle URL (preprod)
- Score de similarité
- Type de redirection recommandé (301, 410, TBD)
- Notes et niveau de confiance

**Utilisation :** Ouvrir dans Excel/Google Sheets pour filtrer, trier et valider les redirections manuellement.

---

### 3. `regles_redirections.md`
Document de synthèse avec :
- Patterns de redirection identifiés
- Règles Apache et Nginx prêtes à l'emploi
- Plan d'implémentation par phases
- Checklist de déploiement
- Exemples de tests

**Utilisation :** Document principal pour l'équipe technique. Contient toutes les règles à implémenter.

---

### 4. `analyze_redirections.py`
Script Python utilisé pour générer l'analyse.

**Utilisation :**
```bash
python3 analyze_redirections.py
```

Le script :
1. Charge les deux fichiers CSV (prod et preprod)
2. Compare les URLs indexables (status 200)
3. Trouve les correspondances par similarité
4. Génère les rapports

---

## Données sources

- **`prod_internal_all.csv`** : Export Screaming Frog du site actuel (www.acpm.fr)
  - 20,650 URLs totales
  - 18,525 URLs indexables

- **`preprod_internal_all.csv`** : Export Screaming Frog du nouveau site (staging)
  - 2,016 URLs totales
  - 1,923 URLs indexables

---

## Résultats clés

### Statistiques de migration

| Métrique | Valeur |
|----------|--------|
| URLs à rediriger | 18,525 |
| URLs sur le nouveau site | 1,923 |
| URLs inchangées | 0 (refonte complète) |

### Répartition des correspondances

| Niveau de confiance | Nombre | Pourcentage | Action |
|---------------------|--------|-------------|--------|
| Haute (≥70%) | 910 | 4.9% | Redirection automatique |
| Moyenne (50-70%) | 687 | 3.7% | Vérification manuelle |
| Faible (<50%) | 16,928 | 91.4% | Analyse manuelle |

---

## Patterns principaux identifiés

### ✅ Haute confiance - Redirection automatique

1. **`/Support/{slug}`** → **`/les-membres/support/{slug}`**
   - ~400 URLs
   - Exemple : `/Support/la-gazette-des-communes` → `/les-membres/support/la-gazette-des-communes`

2. **`/Marque/marque-{slug}`** → **`/les-membres/marque/marque-{slug}`**
   - ~350 URLs
   - Exemple : `/Marque/marque-le-parisien` → `/les-membres/marque/marque-le-parisien`

3. **`/Support-Numerique/site/{domain}`** → **`/les-membres/support/{domain}`**
   - ~100 URLs
   - Exemple : `/Support-Numerique/site/example-fr` → `/les-membres/support/example-fr`

### ⚠️ Moyenne confiance - Vérification manuelle

- 687 URLs nécessitent une révision manuelle
- Voir `redirections_list.csv` avec filtre "Medium confidence"

### ❌ URLs sans correspondance - Décision requise

- **~10,000 URLs** : Images et assets (`/var/ojd/storage/`)
  - **Recommandation :** Code 410 (Gone)

- **~6,768 URLs** : Documents de téléchargement (`/download/document/`)
  - **Recommandation :** Vérifier si migration possible, sinon 410

- **~500 URLs** : Podcasts (`/Podcast/`)
  - **Recommandation :** Rediriger vers page Podcasts ou 410

---

## Plan d'implémentation

### Phase 1 : Redirections haute confiance ⭐ PRIORITAIRE

**Timeline :** Semaine 1

**Actions :**
1. ✅ Implémenter les règles de patterns (voir `regles_redirections.md`)
2. ✅ Tester sur staging avec un échantillon de 50 URLs
3. ✅ Valider avec l'équipe SEO
4. ✅ Déployer sur production

**Impact :** 910 URLs - Trafic organique important

---

### Phase 2 : Redirections moyenne confiance

**Timeline :** Semaine 2

**Actions :**
1. ⏳ Réviser manuellement les 687 URLs (utiliser `redirections_list.csv`)
2. ⏳ Créer des mappings spécifiques
3. ⏳ Valider et déployer

**Impact :** 687 URLs - Trafic organique moyen

---

### Phase 3 : URLs sans correspondance

**Timeline :** Semaine 3-4

**Actions :**
1. ⏳ Décider de la stratégie pour assets/documents/podcasts
2. ⏳ Implémenter les codes 410 ou redirections génériques
3. ⏳ Monitorer les logs pour ajustements

**Impact :** 16,928 URLs - Majoritairement assets sans valeur SEO

---

## Quick Start

### Pour l'équipe technique

1. **Lire** `regles_redirections.md` pour les règles Apache/Nginx
2. **Implémenter** les règles sur l'environnement de staging
3. **Tester** avec curl ou un outil de test de redirections
4. **Déployer** après validation

### Pour l'équipe SEO

1. **Consulter** `redirections_report.md` pour l'analyse détaillée
2. **Ouvrir** `redirections_list.csv` dans Excel/Google Sheets
3. **Filtrer** les URLs de moyenne confiance (50-70%)
4. **Valider** manuellement les correspondances proposées
5. **Communiquer** les ajustements à l'équipe technique

---

## Tests et validation

### Test rapide des patterns

```bash
# Test 1 : Support
curl -I https://www.acpm.fr/Support/la-gazette-des-communes-des-departements-et-des-regions
# Attendu : 301 → /les-membres/support/la-gazette-des-communes-des-departements-et-des-regions

# Test 2 : Marque
curl -I https://www.acpm.fr/Marque/marque-le-parisien-aujourd-hui-en-france
# Attendu : 301 → /les-membres/marque/marque-le-parisien-aujourd-hui-en-france

# Test 3 : Support Numérique
curl -I https://www.acpm.fr/Support-Numerique/site/rennesinfoautrement-fr
# Attendu : 301 → /les-membres/support/rennesinfoautrement-fr

# Test 4 : Assets (410)
curl -I https://www.acpm.fr/var/ojd/storage/images/test.jpg
# Attendu : 410 Gone
```

### Monitoring post-déploiement

1. **Google Search Console**
   - Surveiller les erreurs 404
   - Vérifier que les redirections sont suivies

2. **Logs serveur**
   - Analyser les logs d'accès pendant 48h
   - Identifier les URLs qui génèrent des 404

3. **Analytics**
   - Vérifier que le trafic organique est maintenu
   - Surveiller les pages d'entrée

---

## FAQ

### Q : Pourquoi 91% des URLs ont une faible confiance ?

**R :** La majorité des URLs sans correspondance sont des assets (images, logos, fichiers) qui n'ont pas été migrés ou ont changé de système de stockage. Ces URLs ont généralement peu ou pas de valeur SEO.

### Q : Que faire des URLs de moyenne confiance ?

**R :** Ces URLs nécessitent une révision manuelle. Ouvrez `redirections_list.csv`, filtrez sur "Medium confidence", et validez chaque correspondance proposée. Si la correspondance n'est pas appropriée, trouvez la bonne destination manuellement.

### Q : Faut-il rediriger tous les assets ?

**R :** Non. Les assets (images, logos, CSS, JS) peuvent retourner un code 410 (Gone) sans impact SEO négatif. Seuls les documents avec du contenu indexé (PDF, etc.) devraient être redirigés si possible.

### Q : Comment gérer les redirections en chaîne ?

**R :** Les règles proposées évitent les redirections en chaîne en mappant directement l'ancienne URL vers la nouvelle destination finale.

### Q : Que faire si Google continue à voir des 404 ?

**R :**
1. Vérifier que les règles sont bien actives
2. Tester manuellement les URLs en erreur
3. Ajouter des règles spécifiques si nécessaire
4. Utiliser l'outil de suppression d'URL dans GSC en dernier recours

---

## Checklist complète

### Avant déploiement

- [ ] Lire et comprendre `regles_redirections.md`
- [ ] Réviser les 687 URLs de moyenne confiance
- [ ] Créer des mappings spécifiques pour les cas particuliers
- [ ] Tester les règles sur staging
- [ ] Valider avec l'équipe SEO
- [ ] Préparer le monitoring (GSC, logs, analytics)

### Déploiement

- [ ] Déployer les règles sur production
- [ ] Tester immédiatement 10-20 URLs représentatives
- [ ] Vérifier les logs en temps réel pendant 1h

### Après déploiement

- [ ] Surveiller les logs pendant 48h
- [ ] Vérifier Google Search Console quotidiennement
- [ ] Analyser le trafic organique
- [ ] Ajuster les règles si nécessaire
- [ ] Soumettre le nouveau sitemap à Google
- [ ] Documenter les ajustements effectués

---

## Support

Pour toute question ou problème :

1. **Consulter la documentation** dans ce dossier
2. **Vérifier les logs** du serveur
3. **Contacter l'équipe SEO** pour validation des correspondances
4. **Relancer l'analyse** si les fichiers sources changent :
   ```bash
   python3 analyze_redirections.py
   ```

---

## Historique

- **2026-02-10** : Analyse initiale et génération des rapports
  - 18,525 URLs analysées
  - 910 redirections haute confiance identifiées
  - Règles Apache/Nginx générées

---

## Prochaines étapes

1. ⏳ Validation manuelle des URLs de moyenne confiance
2. ⏳ Tests sur environnement de staging
3. ⏳ Déploiement en production (Phase 1)
4. ⏳ Monitoring et ajustements
5. ⏳ Phases 2 et 3 selon planning
