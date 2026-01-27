#!/usr/bin/env python
# -*- coding: utf-8 -*-

from minitel.Minitel import Minitel
from minitel.ImageMinitel import ImageMinitel
from PIL import Image, ImageCms
from time import sleep
import random

def kmeans_quantification(pixels, k=8, max_iter=20):
    # Initialisation aléatoire des centres
    centres = random.sample(pixels, k)

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
        if nouveaux_centres == centres:
            break
        centres = nouveaux_centres

    return centres

minitel = Minitel('COM6')

minitel.deviner_vitesse()
minitel.identifier()
minitel.make_speed(4800)
minitel.definir_mode('VIDEOTEX')
minitel.configurer_clavier(etendu = True, curseur = False, minuscule = True)
minitel.echo(False)
minitel.efface()
minitel.curseur(False)

exemples = [
  ('testimage1.jpg', 80, 72, 1, 1),
  ('testimage2.jpg', 36, 72, 11, 1),
  ('testimage3.jpg', 80, 72, 1, 1),
  ('testimage4.jpg', 80, 72, 1, 1),
  ('testimage5.jpg', 80, 72, 1, 1),
  ('testimage6.jpg', 80, 72, 1, 1),
]

for fichier, largeur, hauteur, colonne, ligne in exemples:
	image = Image.open(fichier)
	image = image.resize((largeur, hauteur), Image.ANTIALIAS)
	rgb2lab_transform = ImageCms.buildTransformFromOpenProfiles(
		ImageCms.createProfile("sRGB"),
		ImageCms.createProfile("LAB"),
		"RGB",
		"LAB"
	)
	lab_im = ImageCms.applyTransform(image, rgb2lab_transform)
	print(lab_im)
	# niveaux_optimaux = kmeans_quantification(lab_im[0], k=8)
	# image_minitel = ImageMinitel(minitel)
	# image_minitel.importer(image)
	# image_minitel.envoyer(colonne, ligne)

	# minitel.sortie.join()
	# sleep(1)
	minitel.efface()

minitel.close()
