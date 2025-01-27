"""
Created on Thu Jan 16 17:49:46 2025

@author: ablot
"""

from osgeo import gdal
import numpy as np
import os

class OpenGDAL:
    def __init__(self, image_path, metadata_output_path=None):
        """
        Initialise l'objet et sauvegarde les métadonnées si un chemin de sortie est spécifié.
        :param image_path: Chemin de l'image à ouvrir.
        :param metadata_output_path: Chemin du fichier pour sauvegarder les métadonnées (optionnel).
        """
        self.image_path = image_path
        self.dataset = gdal.Open(image_path)

        if not self.dataset:
            raise FileNotFoundError(f"Impossible d'ouvrir le fichier {image_path} avec GDAL.")

        self.metadata = self.get_metadata()
        self.details = self.get_image_details()

        # Sauvegarde automatique des métadonnées si le chemin est fourni
        if metadata_output_path:
            self.save_metadata(metadata_output_path)

    def get_metadata(self):
        # Extraction des métadonnées GDAL
        metadata = self.dataset.GetMetadata()
        return metadata

    def get_image_details(self):
        """
        Retourne des détails sur l'image, incluant l'extension de l'image.
        """
        driver = self.dataset.GetDriver().LongName
        raster_size = (self.dataset.RasterXSize, self.dataset.RasterYSize)
        bands = self.dataset.RasterCount
        projection = self.dataset.GetProjection() or "Non défini"
        geotransform = self.dataset.GetGeoTransform() or (0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        pixel_size = (geotransform[1], geotransform[5])

        # Extraire l'extension de l'image
        _, extension = os.path.splitext(self.image_path)

        return {
            'driver': driver,
            'size': raster_size,
            'bands': bands,
            'projection': projection,
            'geotransform': geotransform,
            'pixel_size': pixel_size,
            'extension': extension  # Ajout de l'extension
        }

    def get_color_details(self):
        """
        Retourne les informations sur l'encodage des couleurs et l'interprétation des bandes.
        """
        color_details = []
        for i in range(1, self.dataset.RasterCount + 1):
            band = self.dataset.GetRasterBand(i)
            interpretation = gdal.GetColorInterpretationName(band.GetColorInterpretation())
            data_type = gdal.GetDataTypeName(band.DataType)
            color_details.append({
                'band': i,
                'interpretation': interpretation,
                'data_type': data_type
            })
        return color_details

    def get_pixel_matrix(self, normalize=True):
        """
        Récupère les valeurs des pixels sous forme de matrice (ou matrices pour plusieurs bandes).
        :param normalize: Si True, normalise les matrices entre 0 et 1.
        :return: Matrice unique (si une bande) ou liste de matrices (si plusieurs bandes).
        """
        bands = self.dataset.RasterCount
        raster_size = (self.dataset.RasterYSize, self.dataset.RasterXSize)
    
        # Créer une liste pour stocker les matrices de chaque bande
        matrices = []
    
        for i in range(1, bands + 1):
            band = self.dataset.GetRasterBand(i)
            data = band.ReadAsArray()  # Lecture de la bande sous forme de matrice
    
            # Normalisation systématique entre 0 et 1
            if normalize:
                # Calcul de la valeur maximale pour la normalisation
                max_val = np.iinfo(data.dtype).max  # La valeur maximale pour le type de données de la bande
                data = data.astype(np.float32)  # Convertir en float pour la division
                data = data / max_val  # Normaliser les valeurs entre 0 et 1
    
            matrices.append(data)
    
        # Si une seule bande, retourner une matrice unique, sinon retourner une liste de matrices
        return matrices if bands > 1 else matrices[0]

    def save_metadata(self, output_file):
        """
        Sauvegarde les détails, métadonnées et informations colorimétriques dans un fichier texte :
        - "Details" : Contient les informations générales sur l'image.
        - "Metadata" : Contient les métadonnées extraites du fichier.
        - "Color Details" : Contient les informations sur les bandes et leur interprétation.
        """
        with open(output_file, 'w', encoding='utf-8') as file:
            # Section Details
            file.write("Details :\n")
            for key, value in self.details.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")

            # Section Metadata
            file.write("Metadata :\n")
            for key, value in self.metadata.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")

            # Section Color Details
            file.write("Color Details :\n")
            color_details = self.get_color_details()
            for color_detail in color_details:
                file.write(f"Band {color_detail['band']}: Interpretation = {color_detail['interpretation']}, "
                           f"Data Type = {color_detail['data_type']}\n")
        print(f"Métadonnées et détails sauvegardés dans '{output_file}'.")

    def show_metadata(self):
        # Retourne les métadonnées en tant que dictionnaire
        return self.metadata


# Exemple d'utilisation
if __name__ == "__main__":
    # Chemin de l'image à analyser
    image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\Izmir_Turkey.tif"
    
    # Chemin du fichier de sortie pour les métadonnées
    metadata_output_path = "metadata_gdal.txt"

    try:
        # Création de l'objet OpenGDAL avec sauvegarde automatique des métadonnées
        image_metadata = OpenGDAL(image_path, metadata_output_path)
        pixel_matrix = image_metadata.get_pixel_matrix(normalize=True)
        print("Valeurs de la matrice des pixels :")
        for i, matrix in enumerate(pixel_matrix):
            print(f"Bande {i + 1} : Min = {matrix.min()}, Max = {matrix.max()}")
        
        # Afficher les métadonnées
        print("Métadonnées de l'image :")
        print(image_metadata.show_metadata())

        # Afficher des détails généraux sur l'image
        print("\nDétails sur l'image :")
        print(image_metadata.get_image_details())

        # Afficher les détails colorimétriques
        print("\nDétails colorimétriques :")
        color_details = image_metadata.get_color_details()
        for color_detail in color_details:
            print(f"Band {color_detail['band']}: Interpretation = {color_detail['interpretation']}, "
                  f"Data Type = {color_detail['data_type']}")

    except Exception as e:
        print(f"Erreur : {e}")

print(gdal.GetDriverByName('JPEG'))
print(gdal.GetDriverByName('GTiff'))

# # Exemple d'utilisation
# if __name__ == "__main__":
#     image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\memorial.tif"
#     # image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\Archeo_colle.png"
#     # Création de l'objet OpenGDAL
#     try:
#         image_metadata = OpenGDAL(image_path)

#         # Afficher les métadonnées
#         print("Métadonnées de l'image :")
#         print(image_metadata.show_metadata())

#         # Afficher des détails généraux sur l'image
#         print("\nDétails sur l'image :")
#         print(image_metadata.get_image_details())

#         # Récupérer la matrice des pixels
#         pixel_matrix = image_metadata.get_pixel_matrix()
#         print("\nMatrice des pixels :")
#         if isinstance(pixel_matrix, list):
#             for i, matrix in enumerate(pixel_matrix):
#                 print(f"Bande {i + 1} :")
#                 print(matrix)
#         else:
#             print(pixel_matrix)

#         # Sauvegarder les métadonnées dans un fichier
#         image_metadata.save_metadata("metadata_gdal.txt")
#         print("\nMétadonnées sauvegardées dans 'metadata_gdal.txt'.")

#     except Exception as e:
#         print(f"Erreur : {e}")