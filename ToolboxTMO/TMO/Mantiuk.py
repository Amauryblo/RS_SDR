# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 09:36:37 2025

@author: ablot
"""
############################## Import des librairies nécessaires #####################
import numpy as np
from scipy.ndimage import gaussian_filter

import os
import importlib.util

# Définir les chemins des dossiers contenant les modules
current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir)
tools_dir = os.path.join(parent_dir, 'tools')

# Vérification des chemins
print(f"Chemin du script actuel : {current_script_dir}")
print(f"Chemin vers tools : {tools_dir}")


# Fonction pour charger un module de manière dynamique
def import_dynamic(module_name, module_path):
    assert os.path.exists(module_path), f"Module introuvable : {module_path}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(f"Module '{module_name}' importé avec succès depuis {module_path}")
    return module
############# ajouter les outils nécessaires ici
# Importer les modules depuis 'tools'
tools_meta = import_dynamic("modif_meta", os.path.join(tools_dir, 'modif_metadata.py'))

# Importer les classes et fonctions nécessaires des modules
MetadataLogger = tools_meta.MetadataLogger


###################################  Classe ##############################

class MantiukTMO:
    def __init__(self, pixel_matrices, contrast_scaling=0.8, detail_amplification=1.2, metadata_file="metadata.txt"):
        """
        Initialise le Tone Mapping Operator (TMO) de Mantiuk.
        :param pixel_matrices: Une matrice (2D) ou une liste de matrices (pour plusieurs bandes).
        :param contrast_scaling: Facteur de réduction du contraste global (0-1, typiquement 0.8).
        :param detail_amplification: Facteur d'amplification des détails locaux (>1 pour amplifier).
        :param metadata_file: Le chemin vers le fichier où les métadonnées seront enregistrées.
        """
        
        
        self.single_input = not isinstance(pixel_matrices, list)  # Vrai si l'entrée est une matrice unique
        self.pixel_matrices = pixel_matrices if isinstance(pixel_matrices, list) else [pixel_matrices]
        self.contrast_scaling = contrast_scaling
        self.detail_amplification = detail_amplification
        self.metadata_logger = MetadataLogger(metadata_file)
        # Si un metadata_logger n'est pas passé, on en crée un avec le fichier spécifié
        # self.metadata_logger = metadata_logger if metadata_logger else MetadataLogger(metadata_file)

        # Enregistrer l'initialisation de la classe dans les métadonnées
        self.metadata_logger.log_class_usage(
            class_name=self.__class__.__name__,
            pixel_matrices_shape=[matrix.shape for matrix in self.pixel_matrices],
            contrast_scaling=self.contrast_scaling,
            detail_amplification=self.detail_amplification
        )

    def tone_map(self):
        """
        Applique le Tone Mapping Operator (TMO) de Mantiuk à chaque matrice de pixels.
        :return: Une matrice (2D) ou une liste de matrices tonemappées, du même type que l'entrée.
        """
        processed_matrices = []

        for matrix in self.pixel_matrices:
            # Conversion explicite en float32 pour compatibilité
            matrix = matrix.astype(np.float32)
            
            # 1. Convertir en luminance logarithmique pour modéliser la perception humaine
            log_luminance = np.log1p(matrix)  # log(1 + pixel) pour éviter les problèmes avec 0

            # 2. Décomposition multi-échelle (filtrage gaussien pour tendances globales)
            base = gaussian_filter(log_luminance, sigma=30)  # Tendances globales (grandes structures)
            details = log_luminance - base  # Détails locaux

            # 3. Compression du contraste global
            compressed_base = base * self.contrast_scaling

            # 4. Amplification des détails locaux
            amplified_details = details * self.detail_amplification

            # 5. Reconstruction de l'image tonale
            tone_mapped_log = compressed_base + amplified_details
            tone_mapped = np.expm1(tone_mapped_log)  # Exponentielle pour revenir à l'espace linéaire

            # 6. Normalisation entre 0 et 255
            tone_mapped = (tone_mapped - np.min(tone_mapped)) / (np.max(tone_mapped) - np.min(tone_mapped)) * 255
            tone_mapped = tone_mapped.astype(np.uint8)

            processed_matrices.append(tone_mapped)

        # Enregistrer l'appel de la méthode dans les métadonnées
        self.metadata_logger.log_function_call(
            func_name="tone_map",
            input_shapes=[matrix.shape for matrix in self.pixel_matrices],
            contrast_scaling=self.contrast_scaling,
            detail_amplification=self.detail_amplification,
            output_shapes=[matrix.shape for matrix in processed_matrices]
        )

        # Retourner une matrice unique si l'entrée était une matrice unique, sinon une liste
        return processed_matrices[0] if self.single_input else processed_matrices