#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ImageMinitel est une classe permettant de convertir une image lisible par
PIL en semi-graphiques pour le Minitel.

"""

from operator import itemgetter

from minitel.constantes import ESC, SO, DC2, COULEURS_MINITEL
from minitel.Sequence import Sequence
from minitel.Minitel import Minitel

from PIL import Image

from minitel.tui.core.color import Color
from minitel.tui.core.effect import Effect
from minitel.tui.core.mixel import Mixel

def calculer_histogramme(pixels, bins=256):
    histogramme = [0] * bins
    for pixel in pixels:
        histogramme[pixel] += 1
    return histogramme

def initialize_centers(pixels, k=8):
	histogramme = calculer_histogramme(pixels)
	total_pixels = sum(histogramme)
	seuil = total_pixels // k  # Seuil pour chaque cluster

	# Calculer la somme cumulée
	somme_cumulee = 0
	centres = []
	for valeur in range(256):
		somme_cumulee += histogramme[valeur]
		if somme_cumulee >= seuil:
			centres.append(valeur)
			somme_cumulee = 0  # Réinitialiser pour le prochain cluster
			if len(centres) == k:
				break

	# Si on n'a pas assez de centres, compléter avec des valeurs uniformes
	if len(centres) < k:
		valeurs_complementaires = set(range(0, 256, 256 // k))
		centres += list(valeurs_complementaires - set(centres))[:k - len(centres)]
		centres = sorted(centres)
	centres = sorted(centres)
	return centres

def kmeans_quantification(pixels, k=8, max_iter=100, eps=1e-4):
	# Initialisation aléatoire des centres
	centres = initialize_centers(pixels)

	for _ in range(max_iter):
		# Étape 1 : Associer chaque pixel au centre le plus proche
		clusters = [[] for _ in range(k)]
		for pixel in pixels:
			distances = [abs(pixel - centre) for centre in centres]
			cluster_idx = distances.index(min(distances))
			clusters[cluster_idx].append(pixel)

		# Étape 2 : Recalculer les centres
		nouveaux_centres = []
		for cluster in clusters:
			if cluster:
				nouveau_centre = sum(cluster) // len(cluster)
			else:
				nouveau_centre = centres[clusters.index(cluster)]
			nouveaux_centres.append(nouveau_centre)

		# Vérifier la convergence
		d = 0.0
		for i in range(len(centres)):
			d += abs(centres[i] - nouveaux_centres[i])
		d /= len(centres)
		if nouveaux_centres == centres or d < eps:
			break
		centres = nouveaux_centres

	return centres

def quantify_with_kmeans(image_pil):
	# Extraire les pixels de l'image PIL
	pixels = list(image_pil.get_flattened_data())

	# Appliquer k-means
	niveaux = kmeans_quantification(pixels, k=8)

	# Quantifier les pixels
	pixels_quantifies = []
	level_quantifies = []
	for pixel in pixels:
		distances = [abs(pixel - niveau) for niveau in niveaux]
		value = distances.index(min(distances))
		level = niveaux[value]
		pixels_quantifies.append(value)
		level_quantifies.append(level)

	# Reconstruire une image PIL à partir des pixels quantifiés
	image_quantifiee = Image.new(image_pil.mode, image_pil.size)
	image_quantifiee.putdata(pixels_quantifies)
	gray = Image.new(image_pil.mode, image_pil.size)
	gray.putdata(level_quantifies)

	return image_quantifiee, gray, niveaux

# def _huit_niveaux(niveau):
#     """Convertit un niveau sur 8 bits (256 valeurs possibles) en un niveau
#     sur 3 bits (8 valeurs possibles).

#     :param niveau:
#         Niveau à convertir. Si c’est un tuple qui est fourni, la luminosité de
#         la couleur est alors calculée. La formule est issue de la page
#         http://alienryderflex.com/hsp.html
#     :type niveau:
#         un tuple ou un entier

#     :returns:
#         Un entier compris entre 0 et 7 inclus.
#     """
#     # Niveau peut soit être un tuple soit un entier
#     # Gère les deux cas en testant l’exception
#     try:
#         return int(niveau * 8 / 256)
#     except TypeError:
#         gray = round(2.55 * xyz_to_lab(*rgb_to_xyz(niveau[0], niveau[1], niveau[2])))
#         level = int(gray * 8 / 256)
#         return level
#         # return int(
#         #     round(
#         #         sqrt(
#         #             0.299 * niveau[0] ** 2 +
#         #             0.587 * niveau[1] ** 2 +
#         #             0.114 * niveau[2] ** 2
#         #         )
#         #     ) * 8 / 256
#         # )

def _deux_couleurs(couleurs):
    """Réduit une liste de couleurs à un couple de deux couleurs.

    Les deux couleurs retenues sont les couleurs les plus souvent
    présentes.

    :param couleurs:
        Les couleurs à réduire. Chaque couleur doit être un entier compris
        entre 0 et 7 inclus.
    :type couleurs:
        Une liste d’entiers

    :returns:
        Un tuple de deux entiers représentant les couleurs sélectionnées.
    """
    assert isinstance(couleurs, list)

    # Crée une liste contenant le nombre de fois où un niveau est
    # enregistré
    niveaux = [0, 0, 0, 0, 0, 0, 0, 0]

    # Passe en revue tous les niveaux pour les comptabiliser
    for couleur in couleurs:
        niveaux[couleur] += 1

    # Prépare la liste des niveaux afin de pouvoir la trier du plus
    # utilisé au moins utilisé. Pour cela, on crée une liste de tuples
    # (niveau, nombre d’apparitions)
    # niveaux = [(index, valeur) for index, valeur in enumerate(niveaux)]

    # Trie les niveaux par nombre d’apparition
    niveaux = sorted(enumerate(niveaux), key = itemgetter(1), reverse = True)
    # Retourne les deux niveaux les plus rencontrés
    return (niveaux[0][0], niveaux[1][0])

def _arp_ou_avp(couleur, arp, avp):
    """Convertit une couleur en couleur d’arrière-plan ou d’avant-plan.

    La conversion se fait en calculant la proximité de la couleur avec la
    couleur d’arrière-plan (arp) et avec la couleur d’avant-plan (avp).

    :param couleur:
        La couleur à convertir (valeur de 0 à 7 inclus).
    :type couleur:
        un entier

    :param arp:
        La couleur d’arrière-plan (valeur de 0 à 7 inclus)
    :type arp:
        un entier

    :param avp:
        La couleur d’avant-plan (valeur de 0 à 7 inclus)
    :type avp:
        un entier

    :returns:
        0 si la couleur est plus proche de la couleur d’arrière-plan, 1 si
        la couleur est plus proche de la couleur d’avant-plan.
    """
    assert isinstance(couleur, int)
    assert isinstance(arp, int)
    assert isinstance(avp, int)

    if(abs(arp - couleur) < abs(avp - couleur)):
        return 0

    return 1

def _minitel_arp(niveau):
    """Convertit un niveau en une séquence de codes Minitel définissant la
    couleur d’arrière-plan.

    :param niveau:
        Le niveau à convertir (valeur de 0 à 7 inclus).
    :type niveau:
        un entier

    :returns:
        Un objet de type Sequence contenant la séquence à envoyer au
        Minitel pour avec une couleur d’arrière-plan correspondant au
        niveau.
    """
    assert isinstance(niveau, int)

    try:
        return Sequence([ESC, 0x50 + COULEURS_MINITEL[niveau]])
    except IndexError:
        return Sequence([ESC, 0x50])

def _minitel_avp(niveau):
    """Convertit un niveau en une séquence de codes Minitel définissant la
    couleur d’avant-plan.

    :param niveau:
        Le niveau à convertir (valeur de 0 à 7 inclus).
    :type niveau:
        un entier

    :returns:
        Un objet de type Sequence contenant la séquence à envoyer au
        Minitel pour avec une couleur d’avant-plan correspondant au niveau.
    """
    assert isinstance(niveau, int)

    try:
        return Sequence([ESC, 0x40 + COULEURS_MINITEL[niveau]])
    except IndexError:
        return Sequence([ESC, 0x47])

class ImageMinitelMixels:
    """Convertit une image PIL en Mixels pour Minitel semi-graphique."""

    def __init__(self, disjoint=False):
        self.disjoint = disjoint
        self.mixels: list[Mixel] = []
        self.largeur = 0
        self.hauteur = 0

    def importer(self, image: Image.Image):
        """Convertit l'image PIL en Mixels."""
        # Dimensions du Minitel semi-graphique
        self.largeur = image.width // 2
        self.hauteur = image.height // 3
        self.mixels = []

        for ligne in range(self.hauteur):
            for col in range(self.largeur):
                # On récupère les 6 pixels du bloc 2x3
                bloc_pixels = [
                    image.getpixel((col * 2 + dx, ligne * 3 + dy))
                    for dy in range(3)
                    for dx in range(2)
                ]

                # Deux couleurs max par bloc
                arp, avp = _deux_couleurs(bloc_pixels)

                # Quantification du bloc selon arp/avp
                bloc_pixels_bin = [_arp_ou_avp(px, arp, avp) for px in bloc_pixels]

                # Convertit 2x3 pixels en caractère semi-graphique
                char_code = self._pixels_to_char(bloc_pixels_bin)

                # Crée un Mixel avec position et couleurs
                self.mixels.append(
                    Mixel(
                        x=col + 1,       # position colonne (1-index)
                        y=ligne + 1,     # position ligne (1-index)
                        character=chr(char_code),
                        effect=Effect.SEMIGRAPHIQUE,
                        color=Color.WHITE,  # tu peux mapper arp/avp si tu veux couleurs
                    )
                )

    def _pixels_to_char(self, bloc):
        """
        Transforme 6 pixels (liste de 0/1) en code caractère semi-graphique Minitel.
        bloc[0..5] correspond à :
            [0,1,
             2,3,
             4,5]
        """
        bits = [
            '0',            # bit 0 toujours 0
            str(bloc[5]),   # bit 1
            '1',            # bit 2 toujours 1
            str(bloc[4]),   # bit 3
            str(bloc[3]),   # bit 4
            str(bloc[2]),   # bit 5
            str(bloc[1]),   # bit 6
            str(bloc[0]),   # bit 7
        ]
        return int(''.join(bits), 2)

    def render(self):
        """Renvoie la liste de mixels prête à Graphics.update()"""
        return self.mixels
