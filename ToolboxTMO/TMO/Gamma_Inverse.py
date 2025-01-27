# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 17:28:33 2025

@author: ablot
"""

import numpy as np
from os.path import exists
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

# Importer les modules depuis 'tools'
tools_meta = import_dynamic("modif_meta", os.path.join(tools_dir, 'modif_metadata.py'))

# Importer les classes et fonctions nécessaires des modules
MetadataLogger = tools_meta.MetadataLogger


class GammaInverseTMO:
    def __init__(self, pixel_matrix, metadata_file="metadata.txt"):
        """
        Initialise le Tone Mapping Operator Gamma inverse.
        :param pixel_matrix: Matrice 2D ou liste de matrices (plusieurs bandes).
        :param metadata_file: Chemin du fichier de métadonnées.
        """
        self.single_input = not isinstance(pixel_matrix, list)  # Si une seule matrice
        self.pixel_matrix = pixel_matrix if isinstance(pixel_matrix, list) else [pixel_matrix]
        self.metadata_file = metadata_file
        self.gamma = self._get_gamma_from_metadata(metadata_file)
        
        # Log initial dans les métadonnées
        self._log_tmo_usage()

    def _get_gamma_from_metadata(self, metadata_file):
        """
        Extrait la valeur du gamma à partir du fichier des métadonnées.
        :param metadata_file: Chemin du fichier des métadonnées.
        :return: La valeur du gamma utilisée dans la correction TMO.
        """
        if not exists(metadata_file):
            raise FileNotFoundError(f"Le fichier des métadonnées '{metadata_file}' est introuvable.")
        
        # Lecture du fichier des métadonnées et extraction de la valeur gamma
        with open(metadata_file, 'r', encoding='utf-8') as file:
            for line in file:
                if "gamma" in line:
                    # Cherche une ligne contenant 'gamma' et extrait la valeur
                    gamma_value = line.split(":")[1].strip()
                    return float(gamma_value)
        
        raise ValueError(f"Aucune valeur gamma trouvée dans le fichier des métadonnées '{metadata_file}'.")

    def _log_tmo_usage(self):
        """
        Enregistre les informations concernant l'utilisation du TMO inverse dans le fichier des métadonnées.
        """
        # Création d'une instance de MetadataLogger
        metadata_logger = MetadataLogger(self.metadata_file)
        
        # Log des informations sur l'utilisation de la classe GammaInverseTMO
        metadata_logger.log_class_usage(
            class_name="GammaInverseTMO",
            gamma=self.gamma
        )
    
    def apply_inverse_correction(self):
        """
        Applique la correction inverse de gamma sur la matrice ou les matrices.
        :return: Liste de matrices avec la correction inverse appliquée.
        """
        processed_matrices = []
    
        for matrix in self.pixel_matrix:
            # Conversion en float32 pour éviter les erreurs numériques
            matrix = matrix.astype(np.float32)
    
            # Normalisation (0-1) si ce n'est pas déjà le cas
            matrix = matrix / 255.0 if matrix.max() > 1 else matrix
    
            # Application de la correction inverse gamma
            inverse_corrected_matrix = np.power(matrix, self.gamma)
    
            # Re-normalisation (0-65535) et conversion en uint16 pour l'image en 16 bits
            inverse_corrected_matrix = (inverse_corrected_matrix * 65535).clip(0, 65535).astype(np.uint16)
    
            processed_matrices.append(inverse_corrected_matrix)
    
        # Si l'entrée était une matrice 3D, séparez les canaux en matrices 2D
        if len(self.pixel_matrix) == 1 and len(self.pixel_matrix[0].shape) == 3:
            height, width, channels = self.pixel_matrix[0].shape
            separated_channels = [
                processed_matrices[0][:, :, i] for i in range(channels)
            ]
            return separated_channels

        # Retourne une matrice unique si l'entrée était une seule matrice, sinon une liste
        return processed_matrices[0] if self.single_input else processed_matrices
