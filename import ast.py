import ast
import pprint
import webbrowser
from scholarly import scholarly
import urllib

#@software_version{cholewiak2021scholarly,
#  author  = {Cholewiak, Steven A. and Ipeirotis, Panos and Silva, Victor and Kannawadi, Arun},
#  title   = {{SCHOLARLY: Simple access to Google Scholar authors and citation using Python}},
#  year    = {2021},
#  doi     = {10.5281/zenodo.5764801},
#  license = {Unlicense},
#  url = {https://github.com/scholarly-python-package/scholarly},
#  version = {1.5.1}
#}


#############################################################################
#############################################################################
#########                                                           #########
#########   Recherche sur les auterurs                              #########
#########   Informations profils, publications, citations           #########
#########                                                           #########
#############################################################################
#############################################################################

# Retrieve the author's data, fill-in, and print
# Get an iterator for the author results
#search_query = scholarly.search_author('Guillaume Cleuziou')

'''
+--------------------------------------------+
|         Result with Jimmy Nicolle          |
+--------------------------------------------+

James AR Nicoll
Jim Nichol
Nicole M. James
James Tempest
Nicole S Wright
Dr. James R Nicol
Jimmy Nicolle <--- /!/
Shannon N Conley
Nicole Bates
Jaelen Nicole Myers
Nikki James

Difficle de trouver le bon Jimmy Nicolle

Code pour le trouver :

for author in search_query:
    if author['name'] == 'Jimmy Nicolle':
        scholarly.pprint(author)

'''

# Retrieve the first result from the iterator
#first_author_result = next(search_query)
#scholarly.pprint(first_author_result)

'''
+---------------------------------------------------------------+
|                                                               |
|                           RESULT                              | 
|               with Guillaume Cleuziou name                    |
|                                                               |
+---------------------------------------------------------------+ 

b"{'affiliation': 'LIFO - University of Orl\xc3\xa9ans, FRANCE',
   'citedby': 879,
   'email_domain': '@univ-orleans.fr',
   'filled': False,
   'interests': ['Data Mining', 'Machine Learning', 'Knowledge Discovery'],\n 
   'name': 'Guillaume Cleuziou',\n 
   'scholar_id': '5ox2mg8AAAAJ',\n 
   'source': 'SEARCH_AUTHOR_SNIPPETS',\n 
   'url_picture': 'https://scholar.google.com/citations?view_op=medium_photo&user=5ox2mg8AAAAJ'
}"

'''

# Retrieve all the details for the author
#author = scholarly.fill(first_author_result)
#scholarly.pprint(author)

# Take a closer look at the first publication
#first_publication = author['publications'][0]
#first_publication_filled = scholarly.fill(first_publication)
#scholarly.pprint(first_publication_filled)

'''
+---------------------------------------------------------------+
|                                                               |
|                           RESULT                              | 
|               with Guillaume Cleuziou name                    |
|                                                               |
+---------------------------------------------------------------+ 
b"{
'author_pub_id': '5ox2mg8AAAAJ:W7OEmFMy1HYC',
'bib': {'abstract': 'This paper deals with clustering for multi-view data, i.e. objects described by several sets of variables or proximity matrices. 
                         Many important domains or 'applications such as information retrieval, biology, chemistry and marketing are concerned by this 
                         problematic. The aim of this data mining research field is to search for clustering patterns that perform a consensus between the patterns 
                         from different views. This requires to merge information from each view by performing a fusion process that identifies the 
                         agreement between the views and solves the conflicts. Various fusion strategies can be applied, occurring either before, after or during 
                         the clustering process. We draw our inspiration from the existing algorithms based on a centralized strategy. We propose a fuzzy 
                         clustering approach that generalizes the three fusion strategies and outperforms the main existing multi-view clustering algorithm both on 
                         synthetic and \xe2\x80\xa6',         
          'author': 'Guillaume Cleuziou and Matthieu Exbrayat and Lionel Martin and Jacques-Henri Sublemontier',
          'citation': '2009 Ninth IEEE International Conference on Data Mining, 752-757, 2009',
          'conference': '2009 Ninth IEEE International Conference on Data Mining',
          'pages': '752-757',
          'pub_year': 2009,
          'publisher': 'IEEE',
          'title': 'CoFKM: A centralized method for multiple-view clustering'
          },
'citedby_url': '/scholar?hl=en&cites=14200367826851694539',
'cites_id': ['14200367826851694539'],
'cites_per_year': {2010: 1,
                    2011: 3,
                    2012: 5,
                    2013: 4,
                    2014: 6,
                    2015: 5,
                    2016: 10,                  
                    2017: 16,
                    2018: 17,
                    2019: 21,               
                    2020: 18,
                    2021: 14,
                    2022: 19,
                    2023: 7,
                    2024: 12
     },
'filled': True,
'num_citations': 159,
'pub_url': 'https://ieeexplore.ieee.org/abstract/document/5360306/',
'source': 'AUTHOR_PUBLICATION_ENTRY',
'url_related_articles': '/scholar?oi=bibs&hl=en&q=related:y4dhP03XEcUJ:scholar.google.com/'
}"
'''

# Print the titles of the author's publications
#publication_titles = [pub['bib']['title'] for pub in author['publications']]
#print(publication_titles)

'''
+---------------------------------------------------------------+
|                                                               |
|                           RESULT                              | 
|               with Guillaume Cleuziou name                    |
|                                                               |
+---------------------------------------------------------------+ 

['CoFKM: A centralized method for multiple-view clustering', 
 'An extended version of the k-means method for overlapping clustering', 
 'PoBOC: an overlapping clustering algorithm. application to rule-based classification and textual data.', 
 "Une méthode de classification non-supervisée pour l'apprentissage de règles et la recherche d'information", 
 'Overview of overlapping partitional clustering methods', 
 'Query log driven web search results clustering', 
 'Two variants of the okm for overlapping clustering', 
 'OKM: une extension des k-moyennes pour la recherche de classes recouvrantes.', 
 'Post-retrieval clustering using third-order similarity measures', 
 'Catégorisation de textes en domaines et genres: complémentarité des indexations lexicale et morphosyntaxique', 
 'Fully unsupervised graph-based discovery of general-specific noun relationships from web corpora frequency counts', 
 'Kernel methods for point symmetry-based clustering', 'A generalization of k-means for overlapping clustering', 
 'Qassit at semeval-2016 task 13: On the integration of semantic vectors in pretopological spaces for lexical taxonomy acquisition', 
 'Biology based alignments of paraphrases for sentence compression', 
 'Automatic knowledge representation using a graph-based algorithm for language-independent lexical chaining', 
 'Osom: A method for building overlapping topological maps', 
 'Mapping general-specific noun relationships to wordnet hypernym/hyponym relations', 
 'Learning pretopological spaces for lexical taxonomy acquisition', 
 ...,
 '9ème Atelier sur la Fouille de Données Complexes Complexité liée aux données multiples et massives'
 ]

'''

# Which papers cited that publication?
#citations = [citation['bib']['title'] for citation in scholarly.citedby(first_publication_filled)]
#print(citations)

'''
+---------------------------------------------------------------+
|                                                               |
|                           RESULT                              | 
|               with Guillaume Cleuziou name                    |
|                                                               |
+---------------------------------------------------------------+ 

['A survey on multiview clustering', 
 'A survey on multi-view clustering', 
 'Multi-view clustering: A survey', 
 'Multi-view subspace clustering with intactness-aware similarity', 
 'Collaborative fuzzy clustering from multiple weighted views', 
 'Recognition of epileptic EEG signals using a novel multiview TSK fuzzy system', 
 'Enhanced fuzzy clustering for incomplete instance with evidence combination', 
 'A novel distributed multitask fuzzy clustering algorithm for automatic MR brain image segmentation', 
 'A Novel Brain MRI Image Segmentation Method Using an Improved Multi-View Fuzzy c-Means Clustering Algorithm', 
 'Collaborative feature-weighted multi-view fuzzy c-means clustering', 'Adaptive weighted multi-view evidential clustering with feature preference', 
 'Collaborative clustering: Why, when, what and how', 
 'TW-Co-MFC: Two-level weighted collaborative fuzzy clustering based on maximum entropy for multi-view data', 
 'TW-Co-k-means: Two-level weighted collaborative k-means for multi-view clustering', 
 'Self-weighted multi-view fuzzy clustering', 
 'A co-training strategy for multiple view clustering in process mining', 
 'Unsupervised multiview fuzzy c-means clustering algorithm', 
 'Adaptive weighted multi-view evidential clustering', 
 'Multi-view maximum entropy clustering by jointly leveraging inter-view collaborations and intra-view-weighted attributes', 
 'A unified collaborative multikernel fuzzy clustering for multiview data', 
 'Fuzzy clustering for multiview data by combining latent information', 
 'Multi-view fuzzy clustering with minimax optimization for effective clustering of data from multiple sources', 
 'Robust self-tuning multi-view clustering', 
 ..., 
 "L'Université Paris–Saclay"
] 
'''

#############################################################################
#############################################################################
#########                                                           #########
#########                        FIN                                #########
#########                                                           #########
#########                                                           #########
#############################################################################
#############################################################################


#############################################################################
#############################################################################
#########                                                           #########
#########   Recherche sur les publications                          #########
#########   Informations profils, publications, citations           #########
#########                                                           #########
#############################################################################
#############################################################################

from scholarly import scholarly
import collections.abc

# Effectuer la recherche
search_query4 = scholarly.search_pubs("10.1103/PhysRevB.5.4709")
print(f"Type de search_query4 : {type(search_query4)}")

# Vérifier si search_query4 est un itérateur ou un générateur
if isinstance(search_query4, collections.abc.Iterator):
    # Cas où search_query4 est un itérateur
    try:
        for i, result in enumerate(search_query4):
            print(f"Résultat {i+1} trouvé avec un itérateur :\n")
            # Afficher toutes les clés et valeurs pour chaque résultat
            def find_keys(d, keys=None):
                if keys is None:
                    keys = set()  # Utilise un ensemble pour éviter les doublons
                for key, value in d.items():
                    keys.add(key)  # Ajouter la clé à l'ensemble
                    if isinstance(value, dict):  # Si la valeur est un dictionnaire
                        find_keys(value, keys)  # Appeler récursivement pour ce sous-dictionnaire
                return keys

            all_keys = find_keys(result)
            for key in all_keys:
                value = result.get(key, 'Clé non trouvée')
                print(f"{key} : {value}\n")
            break  # Sortir après le premier résultat pour éviter une surcharge de sortie
    except StopIteration:
        print("Aucun résultat trouvé dans l'itérateur.")

elif hasattr(search_query4, '__next__'):
    # Cas où search_query4 est un générateur
    try:
        result = search_query4.__next__()
        print("Résultat trouvé avec un générateur :\n")
    except StopIteration:
        print("Aucun résultat trouvé dans le générateur.")
else:
    print("search_query4 n'est ni un itérateur ni un générateur.")
    result = None
