#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from minitel.Minitel import Minitel
from minitel.ImageMinitel import ImageMinitel
from PIL import Image, ImageCms
from time import sleep
import random
import numpy as np

def calculer_histogramme(pixels, bins=256):
    histogramme = [0] * bins
    for pixel in pixels:
        histogramme[pixel] += 1
    return histogramme

def initialiser_centres_par_histogramme(pixels, k=8):
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
	centres = initialiser_centres_par_histogramme(pixels)

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

minitel = Minitel('COM6')

minitel.deviner_vitesse()
minitel.identifier()
minitel.definir_vitesse(4800)
minitel.definir_mode('VIDEOTEX')
minitel.configurer_clavier(etendu = True, curseur = False, minuscule = True)
minitel.echo(False)
minitel.efface()
minitel.curseur(False)

exemples = [
#   (r"C:\Users\mimix\OneDrive\Images\new24.jpg", 80, 72, 1, 1),
#   (r"C:\Users\mimix\OneDrive\Images\new25.jpg", 80, 72, 1, 1),
#   (r"C:\Users\mimix\Documents\TSS_2025_15_07\TSS_2025_15_07\Graphics\Battlers\lizardman_2.png", 80, 72, 1, 1),
  (r"C:\Users\mimix\OneDrive\Images\new33.jpg", 80, 72, 1, 1),
  (r"C:\Users\mimix\OneDrive\Images\new29.jpg", 80, 72, 1, 1),
]

for fichier, largeur, hauteur, colonne, ligne in exemples:
	image = Image.open(fichier)
	image = image.resize((largeur, hauteur), Image.Resampling.LANCZOS)

	image = image.convert("L")
	image_q, level, niveaux_optimaux = quantify_with_kmeans(image)
	
	# level.save("./test.png")

	# pixels = [int((value * 8) / 256) for value in list(image.get_flattened_data())]
	# classic = Image.new(image.mode, image.size)
	# classic.putdata(pixels)
	# classic.save("./gray.png")

	# print(np.mean(np.abs(np.array(pixels) - np.array(image_q.get_flattened_data()))))

	image_minitel = ImageMinitel(minitel)
	image_minitel.importer(image_q)
	image_minitel.envoyer(colonne, ligne)

	minitel.sortie.join()
	sleep(8)
	minitel.efface()
	minitel.semigraphique(False)

minitel.close()
