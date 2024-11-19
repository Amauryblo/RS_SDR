# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 11:27:04 2024

@author: ablot
"""

import imageio
import numpy as np

class LuminanceCalculator:
    def __init__(self, image_path):
        """
        Initialise la classe avec le chemin de l'image.
        :param image_path: chemin vers l'image .tif
        """
        self.image_path = image_path
        self.image = self.load_image()
    
    def load_image(self):
        """
        Charge l'image à partir du fichier.
        :return: image chargée sous forme de tableau numpy
        """
        try:
            image = imageio.imread(self.image_path)
            return image
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")
            return None
    
    def calculate_luminance(self):
        """
        Calcule la luminance de l'image en utilisant une moyenne pondérée des canaux RGB.
        :return: tableau numpy représentant la luminance de l'image
        """
        if self.image is None:
            print("L'image n'a pas pu être chargée.")
            return None
        
        # Vérifier si l'image a trois canaux (RGB)
        if len(self.image.shape) == 3 and self.image.shape[2] == 3:
            # Extraire les canaux R, G, B
            R = self.image[:, :, 0]
            G = self.image[:, :, 1]
            B = self.image[:, :, 2]

            # Appliquer la formule de la luminance
            # luminance = 0.2989 * R + 0.5870 * G + 0.1140 * B
            luminance =(R + G + B)/3
            return luminance
        else:
            print("L'image n'est pas en format RGB.")
            return None
    
    def save_luminance_image(self, output_path):
        """
        Sauvegarde l'image de luminance sous forme de fichier .tif.
        :param output_path: chemin où sauvegarder l'image luminance
        """
        luminance = self.calculate_luminance()
        if luminance is not None:
            # Normaliser la luminance à 8 bits (0-255)
            luminance = np.clip(luminance, 0, 255).astype(np.uint8)
            imageio.imwrite(output_path, luminance)
            print(f"L'image de luminance a été sauvegardée à {output_path}")
        else:
            print("Erreur dans le calcul de la luminance. L'image n'a pas été sauvegardée.")