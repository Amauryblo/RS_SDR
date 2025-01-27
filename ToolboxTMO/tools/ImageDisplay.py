# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 10:03:46 2025

@author: ablot
"""

import matplotlib.pyplot as plt
import numpy as np

class ImageDisplay:
    def __init__(self, images, titles=None):
        """
        Initialise la classe d'affichage d'images.
        :param images: Liste d'images ou de matrices (2D pour niveaux de gris, 3D pour RGB).
        :param titles: Liste des titres pour chaque image (optionnel).
        """
        self.images = images if isinstance(images, list) else [images]
        self.titles = titles if titles else [f"Image {i+1}" for i in range(len(self.images))]
        
        if len(self.images) != len(self.titles):
            raise ValueError("Le nombre d'images et de titres doit être identique.")

    def show(self, cmap="gray"):
        """
        Affiche les images côte à côte.
        :param cmap: Colormap pour les images en niveaux de gris (par défaut : 'gray').
        """
        num_images = len(self.images)
        plt.figure(figsize=(10 * num_images, 5))

        for i, img in enumerate(self.images):
            plt.subplot(1, num_images, i + 1)

            # Si l'image est une liste (comme dans votre cas), afficher chaque image dans la liste
            if isinstance(img, list):
                # Si la liste contient 3 matrices, considérer que c'est une image RGB
                if len(img) == 3 and all(len(sub_img.shape) == 2 for sub_img in img):
                    img = np.stack(img, axis=-1)  # Combiner les matrices en une image RGB
                else:
                    # Si la liste ne correspond pas à 3 matrices 2D, afficher chaque matrice séparément
                    for sub_img in img:
                        self._show_single_image(sub_img, cmap)
                    continue  # Passer à l'image suivante si la liste ne représente pas un RGB

            self._show_single_image(img, cmap)
            plt.title(self.titles[i])
            plt.axis("off")

        plt.show()

    def _show_single_image(self, img, cmap):
        """
        Affiche une seule image en tenant compte de son type (niveau de gris ou RGB).
        :param img: L'image à afficher (matrice numpy).
        :param cmap: Colormap pour les images en niveaux de gris.
        """
        # Vérifier la profondeur de l'image (8 bits ou 16 bits)
        if img.dtype == np.uint16:
            # Si l'image est en 16 bits, normaliser les valeurs entre 0 et 1
            img = img.astype(float) / 65535  # Normalisation pour affichage
        elif img.dtype == np.uint8:
            # Si l'image est en 8 bits, aucun besoin de normalisation
            img = img.astype(float) / 255  # Optionnel : normaliser pour afficher en flottant entre 0 et 1

        if len(img.shape) == 2:  # Image en niveaux de gris
            plt.imshow(img, cmap=cmap)
        elif len(img.shape) == 3:  # Image RGB
            plt.imshow(img)  # Pas de colormap pour les images RGB
        else:
            raise ValueError("Format d'image non pris en charge. Attendu 2D (gris) ou 3D (RGB).")