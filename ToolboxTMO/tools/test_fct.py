# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 20:04:15 2025

@author: ablot
"""
from open import OpenGDAL
from save import CreateImageFromDetails
from Mantiuk import MantiukTMO
from ImageDisplay import ImageDisplay as Idisp


# Chemins des fichiers
# image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\Izmir_Turkey.tif"
# meta_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\metadata_open.txt"
# output_path1 = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\ImageAvant.tif"
# output_path2 = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\ImageApres.tif"

image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\Izmir_Turkey.tif"
# image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\memorial.tif"
# image_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\Dunes_Saudi_Arabia.tif"
meta_path = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\metadata_open.txt"
output_path1 = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\ImageAvant.tif"
output_path2 = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\ImageApres.tif"


# Chargement des données
image_metadata = OpenGDAL(image_path, meta_path)
pixel_matrix = image_metadata.get_pixel_matrix(normalize=True)
 
# Création d'une première image
# CreateImageFromDetails(pixel_matrix, meta_path, output_path1).create_image()

# print("Valeurs de la matrice des pixels :")
# for i, matrix in enumerate(pixel_matrix):
#     print(f"Bande {i + 1} : Min = {matrix.min()}, Max = {matrix.max()}")
    
# Modification des pixels et création d'une deuxième image
# for i in range(len(pixel_matrix)):
#     pixel_matrix[i] = pixel_matrix[i] +15  # Attention à la cohérence des valeurs pour le type de données

# CreateImageFromDetails(pixel_matrix, meta_path, output_path2).create_image()


######☻ pour demain, faire en sorte que le fichier métadata se crée automatiquement


######### test 2

# meta_path2 = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\metadata_open2.txt"
# image_metadata2 = OpenGDAL(image_path, meta_path2)
# pixel_matrix2 = image_metadata2.get_pixel_matrix()


# CreateImageFromDetails(pixel_matrix, meta_path, output_path2).create_image()


##### dimanche : savoir sous quel format mettre les images implémenter 





#### test TMO 

CreateImageFromDetails(pixel_matrix, meta_path, output_path1).create_image()
image_metadata = OpenGDAL(image_path, meta_path)
pixel_matrix = image_metadata.get_pixel_matrix(normalize=True)

for i in range(len(pixel_matrix)):
    pixel_matrix[i] = pixel_matrix[i] +30
    
mat_mod = MantiukTMO(pixel_matrix, contrast_scaling=0.8, detail_amplification=1.2).tone_map()


CreateImageFromDetails(mat_mod, meta_path, output_path2).create_image()


# Créer une instance de la classe ImageDisplay
Images = Idisp(
    images=[pixel_matrix, mat_mod],
    titles=["Image Originale", "Image Modifiée (Mantiuk TMO)"]
)

# Afficher les images
Images.show()


import numpy as np

# # Exemple d'image en niveaux de gris et RGB
# gray_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
# rgb_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

# # Affichage
# viewer = Idisp(images=[gray_image, rgb_image], titles=["Niveaux de gris", "Image RGB"])
# viewer.show()




