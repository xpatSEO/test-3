# Règles de Redirections SEO - ACPM

## Vue d'ensemble

Ce document décrit les règles de redirection à implémenter pour la migration du site www.acpm.fr (prod) vers le nouveau site (preprod).

### Statistiques de la migration

- **18,525 URLs** à rediriger depuis l'ancien site
- **1,923 URLs** sur le nouveau site
- **0 URLs** inchangées (refonte complète de la structure)

### Répartition des correspondances

- **910 URLs** (4.9%) : Haute confiance (≥70%) - peuvent être redirigées automatiquement
- **687 URLs** (3.7%) : Moyenne confiance (50-70%) - nécessitent une vérification manuelle
- **16,928 URLs** (91.4%) : Faible confiance (<50%) - nécessitent une analyse manuelle

---

## Patterns de redirection identifiés

### 1. Pages Support

**Pattern :** `/Support/{slug}` → `/les-membres/support/{slug}`

**Exemples :**
```
/Support/la-gazette-des-communes-des-departements-et-des-regions
→ /les-membres/support/la-gazette-des-communes-des-departements-et-des-regions

/Support/le-parisien-aujourd-hui-en-france-week-end
→ /les-membres/support/le-parisien-aujourd-hui-en-france-week-end
```

**Nombre d'URLs concernées :** ~400

**Règle Apache :**
```apache
RedirectMatch 301 ^/Support/(.*)$ /les-membres/support/$1
```

**Règle Nginx :**
```nginx
rewrite ^/Support/(.*)$ /les-membres/support/$1 permanent;
```

---

### 2. Pages Marque

**Pattern :** `/Marque/marque-{slug}` → `/les-membres/marque/marque-{slug}`

**Exemples :**
```
/Marque/marque-famille-et-education-magazine-de-l-apel
→ /les-membres/marque/marque-famille-et-education-magazine-de-l-apel

/Marque/marque-le-parisien-aujourd-hui-en-france
→ /les-membres/marque/marque-le-parisien-aujourd-hui-en-france
```

**Nombre d'URLs concernées :** ~350

**Règle Apache :**
```apache
RedirectMatch 301 ^/Marque/(.*)$ /les-membres/marque/$1
```

**Règle Nginx :**
```nginx
rewrite ^/Marque/(.*)$ /les-membres/marque/$1 permanent;
```

---

### 3. Pages Les-membres (anciennes)

**Pattern :** `/Les-membres/{type}` → `/les-membres/membre/{type-lowercase}`

**Exemples :**
```
/Les-membres/Intermediaires-de-Presse
→ /les-membres/membre/intermediaires-de-presse

/Les-membres/Editeurs-numerique
→ /les-membres/membre/editeurs-numeriques
```

**Nombre d'URLs concernées :** ~50

**Règle Apache :**
```apache
RedirectMatch 301 ^/Les-membres/Intermediaires-de-Presse$ /les-membres/membre/intermediaires-de-presse
RedirectMatch 301 ^/Les-membres/Editeurs-numerique$ /les-membres/membre/editeurs-numeriques
# Ajouter d'autres mappings spécifiques si nécessaire
```

---

### 4. Support Numérique

**Pattern :** `/Support-Numerique/site/{domain}` → `/les-membres/support/{domain}`

**Exemples :**
```
/Support-Numerique/site/rennesinfoautrement-fr
→ /les-membres/support/rennesinfoautrement-fr

/Support-Numerique/site/pediatrie-pratique-com
→ /les-membres/support/pediatrie-pratique-com
```

**Nombre d'URLs concernées :** ~100

**Règle Apache :**
```apache
RedirectMatch 301 ^/Support-Numerique/site/(.*)$ /les-membres/support/$1
```

**Règle Nginx :**
```nginx
rewrite ^/Support-Numerique/site/(.*)$ /les-membres/support/$1 permanent;
```

---

### 5. Pages statiques

**Pattern :** `/{page}` → `/page/{page}`

**Exemples :**
```
/Informations-legales → /page/informations-legales
/Mentions-legales → /page/mentions-legales
```

**Règle Apache :**
```apache
RedirectMatch 301 ^/Informations-legales$ /page/informations-legales
RedirectMatch 301 ^/Mentions-legales$ /page/mentions-legales
RedirectMatch 301 ^/Contact$ /page/contact
RedirectMatch 301 ^/Plan-du-site$ /page/plan-du-site
```

---

### 6. Export et fichiers temporaires

**Pattern :** `/Support/export/{slug}/{periode}` → `/les-membres/support/{slug}`

**Exemples :**
```
/Support/export/couplage-groupe-depeche-semaine/2024S1?v=2.1.39
→ /les-membres/support/couplage-groupe-depeche-semaine

/Support/export/couplage-groupe-depeche-semaine/2025S2?v=2.1.39
→ /les-membres/support/couplage-groupe-depeche-semaine
```

**Nombre d'URLs concernées :** ~200

**Règle Apache :**
```apache
RedirectMatch 301 ^/Support/export/([^/]+)/[0-9]{4}S[12](.*)$ /les-membres/support/$1
```

**Règle Nginx :**
```nginx
rewrite ^/Support/export/([^/]+)/[0-9]{4}S[12](.*)$ /les-membres/support/$1 permanent;
```

---

## URLs sans correspondance

### 1. Images et assets (~10,000 URLs)

**Patterns :**
- `/var/ojd/storage/images/**`
- `/var/ojd/storage/files/logos/**`
- `/var/ojd/storage/files/covers/**`

**Action recommandée :** Code 410 (Gone) ou redirection vers la page d'accueil

**Règle Apache :**
```apache
# Retourner 410 (Gone) pour les anciens assets
RedirectMatch 410 ^/var/ojd/storage/images/.*
RedirectMatch 410 ^/var/ojd/storage/files/.*
```

**Règle Nginx :**
```nginx
location ~* ^/var/ojd/storage/(images|files)/ {
    return 410;
}
```

---

### 2. Fichiers de téléchargement (6,768 URLs)

**Patterns :**
- `/download/document/{id}`
- `/content/download/{id}/{id}/version/{version}/file/{filename}`

**Action recommandée :**
- Si les fichiers existent toujours : mapper vers le nouveau système de stockage
- Sinon : Code 410 (Gone)

**Règle Apache :**
```apache
# Retourner 410 (Gone) pour les anciens documents
RedirectMatch 410 ^/download/document/.*
RedirectMatch 410 ^/content/download/.*
```

**Règle Nginx :**
```nginx
location ~* ^/(download|content/download)/ {
    return 410;
}
```

---

### 3. Podcasts (~500 URLs)

**Pattern :** `/Podcast/{slug}/{id}`

**Action recommandée :** Vérifier si les podcasts existent sur le nouveau site, sinon rediriger vers une page "Podcasts" ou 410

**Règle Apache (si pas de correspondance) :**
```apache
RedirectMatch 301 ^/Podcast/.*$ /podcasts
# ou
RedirectMatch 410 ^/Podcast/.*$
```

---

## Plan d'implémentation

### Phase 1 : Redirections haute confiance (prioritaire)

1. Implémenter les règles de patterns (Support, Marque, Support-Numerique)
2. Tester sur un échantillon de 50 URLs
3. Déployer sur l'environnement de staging

**URLs concernées :** ~910 URLs
**Impact SEO :** Fort - ces pages ont du trafic organique

---

### Phase 2 : Redirections moyenne confiance

1. Réviser manuellement les 687 URLs de moyenne confiance
2. Créer des règles spécifiques ou des mappings directs
3. Valider avec l'équipe SEO

**URLs concernées :** ~687 URLs
**Impact SEO :** Moyen

---

### Phase 3 : Traitement des URLs sans correspondance

1. **Assets et images :** Implémenter les codes 410 (Gone)
2. **Documents :** Vérifier si migration possible, sinon 410
3. **Podcasts :** Décider de la stratégie (redirection ou 410)

**URLs concernées :** ~16,928 URLs
**Impact SEO :** Faible à moyen (beaucoup d'assets sans valeur SEO)

---

## Fichier de configuration complet

### Apache (.htaccess)

```apache
# Règles de redirection ACPM - Migration site
# Date : 2026-02-10

# 1. Pages Support
RedirectMatch 301 ^/Support/export/([^/]+)/[0-9]{4}S[12](.*)$ /les-membres/support/$1
RedirectMatch 301 ^/Support/(.*)$ /les-membres/support/$1

# 2. Pages Marque
RedirectMatch 301 ^/Marque/(.*)$ /les-membres/marque/$1

# 3. Support Numérique
RedirectMatch 301 ^/Support-Numerique/site/(.*)$ /les-membres/support/$1

# 4. Pages membres (mappings spécifiques)
RedirectMatch 301 ^/Les-membres/Intermediaires-de-Presse$ /les-membres/membre/intermediaires-de-presse
RedirectMatch 301 ^/Les-membres/Editeurs-numerique$ /les-membres/membre/editeurs-numeriques

# 5. Pages statiques
RedirectMatch 301 ^/Informations-legales$ /page/informations-legales
RedirectMatch 301 ^/Mentions-legales$ /page/mentions-legales
RedirectMatch 301 ^/Contact$ /page/contact
RedirectMatch 301 ^/Plan-du-site$ /page/plan-du-site

# 6. Assets et anciens fichiers (410 Gone)
RedirectMatch 410 ^/var/ojd/storage/images/.*
RedirectMatch 410 ^/var/ojd/storage/files/.*
RedirectMatch 410 ^/download/document/.*
RedirectMatch 410 ^/content/download/.*

# 7. Podcasts (à adapter selon la stratégie)
# RedirectMatch 301 ^/Podcast/.*$ /podcasts
# ou
# RedirectMatch 410 ^/Podcast/.*$
```

---

### Nginx

```nginx
# Règles de redirection ACPM - Migration site
# Date : 2026-02-10

server {
    # ... configuration du serveur ...

    # 1. Pages Support (avec exports)
    rewrite ^/Support/export/([^/]+)/[0-9]{4}S[12](.*)$ /les-membres/support/$1 permanent;
    rewrite ^/Support/(.*)$ /les-membres/support/$1 permanent;

    # 2. Pages Marque
    rewrite ^/Marque/(.*)$ /les-membres/marque/$1 permanent;

    # 3. Support Numérique
    rewrite ^/Support-Numerique/site/(.*)$ /les-membres/support/$1 permanent;

    # 4. Pages membres (mappings spécifiques)
    rewrite ^/Les-membres/Intermediaires-de-Presse$ /les-membres/membre/intermediaires-de-presse permanent;
    rewrite ^/Les-membres/Editeurs-numerique$ /les-membres/membre/editeurs-numeriques permanent;

    # 5. Pages statiques
    rewrite ^/Informations-legales$ /page/informations-legales permanent;
    rewrite ^/Mentions-legales$ /page/mentions-legales permanent;
    rewrite ^/Contact$ /page/contact permanent;
    rewrite ^/Plan-du-site$ /page/plan-du-site permanent;

    # 6. Assets et anciens fichiers (410 Gone)
    location ~* ^/var/ojd/storage/(images|files)/ {
        return 410;
    }

    location ~* ^/(download|content/download)/ {
        return 410;
    }

    # 7. Podcasts (à adapter selon la stratégie)
    # rewrite ^/Podcast/.*$ /podcasts permanent;
    # ou
    # location ~* ^/Podcast/ {
    #     return 410;
    # }
}
```

---

## Validation et tests

### Tests à effectuer avant déploiement

1. **Test des patterns principaux :**
   ```bash
   # Tester avec curl
   curl -I https://www.acpm.fr/Support/la-gazette-des-communes-des-departements-et-des-regions
   # Devrait retourner 301 vers /les-membres/support/...
   ```

2. **Vérifier les codes de statut :**
   - 301 pour les redirections permanentes
   - 410 pour les ressources supprimées

3. **Valider avec Google Search Console :**
   - Soumettre un échantillon d'URLs
   - Vérifier que Google suit les redirections

4. **Monitoring post-déploiement :**
   - Surveiller les erreurs 404
   - Analyser les logs pour identifier les URLs manquées
   - Ajuster les règles si nécessaire

---

## Checklist de déploiement

- [ ] Réviser les 687 URLs de moyenne confiance manuellement
- [ ] Créer des mappings spécifiques pour les cas particuliers
- [ ] Tester les règles de redirection sur staging
- [ ] Valider avec l'équipe SEO
- [ ] Configurer le monitoring des redirections
- [ ] Déployer les règles sur production
- [ ] Surveiller les logs pendant 48h
- [ ] Ajuster les règles si nécessaire
- [ ] Soumettre le nouveau sitemap à Google
- [ ] Mettre à jour les liens internes si applicable

---

## Contact et support

Pour toute question sur ce plan de redirection, contacter l'équipe SEO.

**Fichiers générés par l'analyse :**
- `redirections_report.md` : Rapport détaillé complet
- `redirections_list.csv` : Liste Excel de toutes les redirections
- `analyze_redirections.py` : Script d'analyse Python
