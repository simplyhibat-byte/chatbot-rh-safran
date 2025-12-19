#  Chatbot RH Safran - POC

##  Description

Proof of Concept (POC) d'un chatbot RH intelligent développé dans le cadre du hackathon **Think to Deploy** pour Safran. Ce chatbot permet aux collaborateurs d'obtenir rapidement des réponses personnalisées à leurs questions RH selon leur profil (CDI, CDD, Stagiaire, etc.).

##  Objectifs

- **Automatiser** les réponses aux questions RH fréquentes
- **Personnaliser** les réponses selon le profil utilisateur
- **Réduire** la charge de travail du service RH
- **Améliorer** l'expérience collaborateur avec des réponses instantanées

##  Technologies Utilisées

- **Python 3.12**
- **Streamlit** - Interface web interactive
- **Pandas** - Manipulation des données
- **NLP basique** - Traitement du langage naturel (nettoyage, similarité)

##  Structure du Projet

```
chatbot-rh-safran/
│
├── app.py                 # Code principal du chatbot
├── RH_infos.csv          # Base de connaissances RH
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

##  Installation et Lancement

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/simply.hibat-byte/chatbot-rh-safran.git
cd chatbot-rh-safran
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python -m venv venv

# Sur Windows
venv\Scripts\activate

# Sur Mac/Linux
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Lancer l'application**
```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

##  Utilisation

1. **Sélectionnez votre profil** dans le menu déroulant (CDI, CDD, Stagiaire, etc.)
2. **Posez votre question** dans la zone de texte (ex: "Combien de jours de congés ai-je ?")
3. **Cliquez sur "Rechercher la réponse"**
4. Le chatbot trouve la réponse la plus pertinente selon votre profil

##  Fonctionnement Technique

### Architecture du POC

```
Utilisateur → Interface Streamlit → Moteur NLP → Base CSV → Réponse
```

### Processus de matching

1. **Filtrage par profil** : Sélection des questions/réponses correspondant au profil
2. **Nettoyage du texte** : 
   - Conversion en minuscules
   - Suppression de la ponctuation
   - Élimination des stopwords français
3. **Calcul de similarité** : Comptage des mots communs entre la question utilisateur et les questions de la base
4. **Sélection de la meilleure réponse** : Réponse avec le score de similarité le plus élevé
5. **Seuil de confiance** : Si le score est trop faible, escalade vers un humain

### Exemple de flux

```python
Question utilisateur : "combien de jours de congés pour un stagiaire"
↓ Nettoyage
Mots clés : ["combien", "jours", "congés", "stagiaire"]
↓ Filtrage profil = "Stagiaire"
↓ Matching avec questions base
Question trouvée : "Ai-je droit à des congés payés en tant que stagiaire ?"
Score : 3 mots communs
↓ Réponse
"Les stagiaires ont droit à 2,5 jours de congés par mois..."
```

##  Données (RH_infos.csv)

Structure du fichier CSV :

| Colonne | Type | Description |
|---------|------|-------------|
| question_id | int | Identifiant unique |
| profil | string | Type de contrat (CDI, CDD, Stagiaire...) |
| domaine | string | Domaine RH (Congés, Paie, Transport...) |
| question | string | Question type |
| reponse | string | Réponse officielle |

##  Domaines RH Couverts

- ✅ Congés et absences
- ✅ Avantages sociaux
- ✅ Transport
- ✅ Pointage et horaires
- ✅ Paie et droits

##  Évolutions Futures (Phase 2)

### Améliorations techniques
- [ ] Utilisation d'**embeddings** (Sentence Transformers) pour une meilleure compréhension sémantique
- [ ] Classification d'**intentions** avec machine learning
- [ ] **Historique de conversation** avec mémoire contextuelle
- [ ] Support **multilingue** (Français, Arabe/Darija)

### Intégrations
- [ ] Connexion aux systèmes **SAP**
- [ ] Intégration **Microsoft Teams**
- [ ] **Authentification SSO** (LDAP)
- [ ] API REST pour intégration dans d'autres applications

### Sécurité & Conformité
- [ ] **Anonymisation** des logs
- [ ] Conformité **RGPD**
- [ ] **Chiffrement** des données sensibles
- [ ] Gestion des **rôles et permissions**

##  KPIs à Suivre

| KPI | Description | Cible |
|-----|-------------|-------|
| Taux de compréhension | Questions correctement classées | > 85% |
| Taux de réponse correcte | Réponses validées par RH | > 90% |
| Taux d'escalade | Questions transférées à RH | < 15% |
| Temps de réponse | Délai moyen de réponse | < 2s |
| Satisfaction utilisateur | Note CSAT | > 4/5 |

## 👥 Contributeurs

- **EL HEFIANE Hibat Allah** - Développement du POC

## 📄 Licence

Ce projet est développé dans le cadre du hackathon Think to Deploy pour Safran.

## 📞 Contact

Pour toute question concernant ce POC :
- Email : hibatallah.elhefiane17@gmail.com
- LinkedIn : [Hibat allah El-hefiane]

---


**Note** : Ce POC est une démonstration simplifiée. La version production nécessitera des fonctionnalités de sécurité, d'authentification et d'intégration complètes conformes aux exigences Safran.
