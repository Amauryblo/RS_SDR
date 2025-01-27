# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 17:50:19 2025

@author: ablot
"""

################### class save
### doit sauvegarder l'image et les métadonnées
from osgeo import gdal, osr
import numpy as np
import os
from PIL import Image, PngImagePlugin

# Définir le chemin du dossier de sortie
current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir)
cf_path = os.path.join(parent_dir, 'Created_files')

class CreateImageFromDetails:
    def __init__(self, pixel_matrices, details_file, output_image_name_without_extension):
        self.pixel_matrices = pixel_matrices if isinstance(pixel_matrices, list) else [pixel_matrices]
        for matrix in self.pixel_matrices:
            if len(matrix.shape) != 2:
                raise ValueError("Chaque matrice dans 'pixel_matrices' doit être en 2D (hauteur x largeur).")
        self.details_file = details_file
        self.output_image_name_without_extension = output_image_name_without_extension
        self.details = self._read_details_from_file()
    
        self.extension = self.details.get("extension", ".tif")
        if not self.extension.startswith("."):
            self.extension = "." + self.extension
    
        self.output_image_path = os.path.join(cf_path, f"{self.output_image_name_without_extension}{self.extension}")
        self.driver = self._get_driver()

    def _read_details_from_file(self):
        """
        Lit les détails et métadonnées depuis le fichier texte fourni.
        Retourne un dictionnaire avec les détails nécessaires pour recréer l'image.
        """
        details = {}
        with open(self.details_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    details[key.strip()] = value.strip()
        return details

    def _get_driver(self):
        """
        Récupère le driver pour GDAL, basé sur l'extension de fichier.
        Retourne le nom du driver si applicable.
        """
        extension_to_driver = {
            ".tif": "GTiff",
            ".tiff": "GTiff",
            ".png": "PNG",
            ".bmp": "BMP"
        }

        return extension_to_driver.get(self.extension.lower())

    def create_image(self):
        """
        Crée une image en fonction des métadonnées.
        Utilise Pillow pour JPEG, sinon GDAL pour les autres formats.
        Gère automatiquement les codages 8 bits et 16 bits.
        """
        if self.extension.lower() in [".jpg", ".jpeg"]:
            # Pour JPEG, convertir en 8 bits car JPEG ne prend pas en charge 16 bits
            self.pixel_matrices = [self._scale_to_8bit(matrix) for matrix in self.pixel_matrices]
            self._create_image_with_pillow()
        else:
            self._create_image_with_gdal()

    def _scale_to_8bit(self, matrix):
        """
        Met à l'échelle une matrice 16 bits (0-65535) en 8 bits (0-255).
        Si la matrice est déjà en 8 bits, la retourne sans modification.
        """
        if matrix.dtype == np.uint16:
            return (matrix / 65535.0 * 255).astype(np.uint8)
        return matrix

    def _create_image_with_gdal(self):
        """
        Crée une image avec GDAL (pour TIFF, PNG, BMP).
        """
        # Vérifiez que toutes les matrices ont la même taille
        rows, cols = self.pixel_matrices[0].shape
        for matrix in self.pixel_matrices:
            if matrix.shape != (rows, cols):
                raise ValueError("Toutes les matrices dans 'pixel_matrices' doivent avoir les mêmes dimensions.")
    
        bands = len(self.pixel_matrices)
    
        # Détection automatique du type de données
        if np.issubdtype(self.pixel_matrices[0].dtype, np.uint16):
            data_type = gdal.GDT_UInt16
        elif np.issubdtype(self.pixel_matrices[0].dtype, np.uint8):
            data_type = gdal.GDT_Byte
        else:
            raise ValueError("Type de données non pris en charge : uniquement uint8 ou uint16.")
    
        # Création du dataset GDAL
        driver = gdal.GetDriverByName(self.driver)
        if not driver or not driver.Create:
            raise ValueError(f"Le driver '{self.driver}' n'est pas supporté ou ne permet pas la création.")
    
        out_dataset = driver.Create(self.output_image_path, cols, rows, bands, data_type)
        if not out_dataset:
            raise RuntimeError(f"Impossible de créer le fichier de sortie : {self.output_image_path}")
    
        # Écrire les bandes dans le dataset
        for i, matrix in enumerate(self.pixel_matrices):
            out_dataset.GetRasterBand(i + 1).WriteArray(matrix)
    
        # Ajouter le géotransform et la projection si disponibles
        geotransform = self.details.get("geotransform")
        if geotransform:
            out_dataset.SetGeoTransform(tuple(map(float, geotransform.strip("()").split(","))))
    
        projection = self.details.get("projection")
        if projection:
            srs = osr.SpatialReference()
            srs.ImportFromWkt(projection)
            out_dataset.SetProjection(srs.ExportToWkt())
    
        # Ajouter des métadonnées supplémentaires
        metadata = {k: v for k, v in self.details.items() if k not in ["geotransform", "projection"]}
        metadata["Pixel Matrices Shape"] = str([matrix.shape for matrix in self.pixel_matrices])
        metadata["Bit Depth"] = "16-bit" if data_type == gdal.GDT_UInt16 else "8-bit"
        out_dataset.SetMetadata(metadata)
    
        out_dataset.FlushCache()
        out_dataset = None
        print(f"Image GDAL sauvegardée dans : {self.output_image_path}")

    def _create_image_with_pillow(self):
        """
        Crée une image JPEG avec Pillow (en 8 bits uniquement).
        Si les données sont en 16 bits, elles seront mises à l'échelle en 8 bits.
        """
        # Vérifier si la matrice est une image couleur (3 canaux)
        if len(self.pixel_matrices) == 3:
            # Empiler les canaux pour former une image couleur (RGB)
            image_data = np.dstack(self.pixel_matrices)
            if image_data.dtype != np.uint16:
                image_data = (image_data / 65535.0 * 255).astype(np.uint8)  # Pour JPEG, la convertir en 8 bits
        elif len(self.pixel_matrices) == 1:
            # Image en niveaux de gris
            image_data = self.pixel_matrices[0]
        else:
            raise ValueError("Les matrices de pixels doivent contenir 1 ou 3 canaux (niveaux de gris ou RGB).")
    
        # Convertir en image Pillow
        image = Image.fromarray(image_data)
    
        # Ajouter des métadonnées (limitées pour JPEG)
        metadata = {key: value for key, value in self.details.items() if key not in ["geotransform", "projection"]}
    
        # Utiliser PngInfo pour ajouter des métadonnées
        jpeg_metadata = PngImagePlugin.PngInfo()  # PngInfo peut être utilisé même pour JPEG
        for key, value in metadata.items():
            jpeg_metadata.add_text(key, value)
    
        # Sauvegarder l'image
        image.save(self.output_image_path, "PNG", pnginfo=jpeg_metadata)  # PNG prend en charge 16 bits
        print(f"Image PNG sauvegardée dans : {self.output_image_path}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de matrice d'image (100x100 pixels, image couleur)
    pixel_matrices = [
        np.random.randint(0, 256, (100, 100), dtype=np.uint8),  # Canal rouge
        np.random.randint(0, 256, (100, 100), dtype=np.uint8),  # Canal vert
        np.random.randint(0, 256, (100, 100), dtype=np.uint8)   # Canal bleu
    ]
    details_file = os.path.join(cf_path, 'nom_meta.txt')  # Chemin vers le fichier contenant les métadonnées
    output_image_name_without_extension = 'nouvelle_image'

    # Créer l'image
    create_image = CreateImageFromDetails(pixel_matrices, details_file, output_image_name_without_extension)
    create_image.create_image()



# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Matrice ou liste de matrices
#     pixel_matrices = [
#         np.random.randint(0, 255, (512, 768), dtype=np.uint8),  # Bande Rouge
#         np.random.randint(0, 255, (512, 768), dtype=np.uint8),  # Bande Verte
#         np.random.randint(0, 255, (512, 768), dtype=np.uint8)   # Bande Bleue
#     ]

#     # Chemin du fichier contenant les métadonnées
#     details_file = os.path.join(cf_path, "nom_meta.txt")

#     # Chemin de sortie pour la nouvelle image
#     output_image_path = "output_image.tif"

#     try:
#         # Création de l'image
#         image_creator = CreateImageFromDetails(pixel_matrices, details_file, 'nom_image')
#         image_creator.create_image()
#     except Exception as e:
#         print(f"Erreur : {e}")