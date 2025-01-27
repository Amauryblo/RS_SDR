# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 15:40:22 2025

@author: ablot
"""

############################## Import des librairies nécessaires #####################
import numpy as np
from PIL import Image
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


###################################  Classe ##############################

import numpy as np

class GammaTMO:
    def __init__(self, pixel_matrix, gamma=2.2, metadata_file="metadata.txt"):
        """
        Initialise le Tone Mapping Operator Gamma.
        :param pixel_matrix: Matrice 2D ou liste de matrices (plusieurs bandes).
        :param gamma: Valeur gamma à appliquer.
        :param metadata_file: Chemin du fichier de métadonnées.
        """
        self.single_input = not isinstance(pixel_matrix, list)  # Si une seule matrice
        self.pixel_matrix = pixel_matrix if isinstance(pixel_matrix, list) else [pixel_matrix]
        self.gamma = gamma
        self.metadata_file = metadata_file
        self.metadata_logger = MetadataLogger(metadata_file)

        # Enregistrement de l'initialisation dans les métadonnées
        self.metadata_logger.log_class_usage(
            class_name=self.__class__.__name__,
            pixel_matrix_shape=[matrix.shape for matrix in self.pixel_matrix],
            gamma=self.gamma
        )

    def apply_correction(self):
        """
        Applique la correction gamma sur la matrice ou les matrices et convertit une image 16 bits en 8 bits.
        :return: Matrice ou liste de matrices avec correction gamma appliquée et convertie en 8 bits.
        """
        processed_matrices = []

        for matrix in self.pixel_matrix:
            # Vérification du type de données de la matrice
            dtype = matrix.dtype

            # Conversion en float32 pour éviter les erreurs numériques
            matrix = matrix.astype(np.float32)

            # Normalisation en fonction du type de données (en particulier pour uint16)
            if dtype == np.uint8:
                # Si l'image est en 8 bits (0-255), normalisation entre 0 et 1
                matrix = matrix / 255.0
            elif dtype == np.uint16:
                # Si l'image est en 16 bits (0-65535), normalisation entre 0 et 1
                matrix = matrix / 65535.0
            elif np.issubdtype(dtype, np.floating):
                # Si l'image est déjà flottante (0-1), aucune normalisation nécessaire
                pass
            else:
                # Pour d'autres types de données (si nécessaire)
                raise ValueError(f"Type de données {dtype} non pris en charge pour la normalisation")

            # Application de la correction gamma
            corrected_matrix = np.power(matrix, 1 / self.gamma)

            # Conversion en 8 bits (0-255) après la correction gamma
            corrected_matrix = (corrected_matrix * 255).clip(0, 255).astype(np.uint8)

            # Si l'image était en 16 bits, elle est maintenant convertie en 8 bits
            processed_matrices.append(corrected_matrix)

        # Enregistrement de l'appel de la fonction dans les métadonnées
        self.metadata_logger.log_function_call(
            func_name="apply_correction",
            input_shapes=[matrix.shape for matrix in self.pixel_matrix],
            gamma=self.gamma,
            output_shapes=[matrix.shape for matrix in processed_matrices]
        )

        # Retourne une matrice unique si l'entrée était une seule matrice, sinon une liste
        return processed_matrices[0] if self.single_input else processed_matrices
################################### Utilisation ##############################
# if __name__ == "__main__":
#     # Exemple d'utilisation
#     input_image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\ToolboxTMO\Created_files\nom_choisi.tif"
#     output_image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\ToolboxTMO\Created_files\test_gamma.tif"

#     # Charger une image 16 bits
#     pixel_matrix = np.array(Image.open(input_image_path))

#     # Initialiser la classe de correction gamma
#     gamma_corrector = GammaCorrection(pixel_matrix, gamma=2.2, metadata_file="metadata.txt")

#     # Appliquer la correction et sauvegarder l'image
#     gamma_corrector.save_image(output_image_path)
