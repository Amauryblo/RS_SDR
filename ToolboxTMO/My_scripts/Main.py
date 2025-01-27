# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 11:20:52 2025

@author: ablot
"""
########################### Import des modules ##################################
import os
import importlib.util
from osgeo import gdal
import numpy as np


# Définir les chemins des dossiers contenant les modules
current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir)
tools_dir = os.path.join(parent_dir, 'tools')
tmo_dir = os.path.join(parent_dir, 'TMO')
cf_path = os.path.join(parent_dir, 'Created_files')

# # Vérification des chemins
# print(f"Chemin du script actuel : {current_script_dir}")
# print(f"Chemin vers tools : {tools_dir}")
# print(f"Chemin vers TMO : {tmo_dir}")
# print(f"Chemin vers Created_files : {cf_path}")

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
tools_open = import_dynamic("open", os.path.join(tools_dir, 'open.py'))
tools_save = import_dynamic("save", os.path.join(tools_dir, 'save.py'))
tools_image_display = import_dynamic("ImageDisplay", os.path.join(tools_dir, 'ImageDisplay.py'))
# tools_meta = import_dynamic("modif_meta", os.path.join(tools_dir, 'modif_metadata.py'))


############# ajouter les TMO nécessaires ici ##############################

# Importer les modules depuis 'TMO'
tmo_mantiuk = import_dynamic("Mantiuk", os.path.join(tmo_dir, 'Mantiuk.py'))
tmo_gamma = import_dynamic("Gamma", os.path.join(tmo_dir, 'Gamma.py'))
tmo_gamma_inv = import_dynamic("Gamma_Inv", os.path.join(tmo_dir, 'Gamma_Inverse.py'))


# Importer les classes et fonctions nécessaires des modules
OpenGDAL = tools_open.OpenGDAL
CreateImageFromDetails = tools_save.CreateImageFromDetails
ImageDisplay = tools_image_display.ImageDisplay
MantiukTMO = tmo_mantiuk.MantiukTMO
GammaTMO = tmo_gamma.GammaTMO
GammaInvTMO = tmo_gamma_inv.GammaInverseTMO
# MetadataLogger = tools_meta.MetadataLogger

# # Confirmation des imports
# print("Import réussi pour OpenGDAL, CreateImageFromDetails, ImageDisplay et MantiukTMO.")















################################ Exemple de Script ##########################


# Chemin de l'image d'entrée

# im_tif = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\image_hdr\memorial.tif"
# im_tif2 = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\image_hdr\Izmir_Turkey.tif"
im_NY = r"C:\Users\ablot\Documents\PPMD\TMO_Toolbox\TMO\TMO_Toolbox\tools\NewYork.tif"
meta_path = os.path.join(cf_path, "nom_meta.txt")


##### Ouverture image et sauvegarde métadonnées
image_metadata = OpenGDAL(im_NY, meta_path)

##### Récupérer la matrice correspondant à l'image
pixel_matrix = image_metadata.get_pixel_matrix(normalize=False)
ps = image_metadata.get_pixel_matrix(normalize=True)

####### Enregistre l'image de base dans le fichier Created_files avec les métadonnées intégrés
CreateImageFromDetails(pixel_matrix, meta_path, 'image_originale').create_image()


### Appliquer fonction Gamma et enregistrer Image
mat_mod2 = GammaTMO(pixel_matrix, gamma=2.2, metadata_file=meta_path).apply_correction()
CreateImageFromDetails(mat_mod2, meta_path, 'image_Gamma_TMO').create_image()

### Appliquer fonction Gamma Inverse et enregistrer l'image
mat_mod3 = GammaInvTMO(mat_mod2, metadata_file=meta_path).apply_inverse_correction()
CreateImageFromDetails(mat_mod3, meta_path, 'image_Gamma_Inv_TMO').create_image()




##############  Comparaison des matrices ##############

def normalize_matrices(matrices):
    """
    Normalise une liste de matrices en les convertissant dans la plage [0, 1].
    :param matrices: Liste de matrices à normaliser.
    :return: Liste de matrices normalisées.
    """
    normalized_matrices = []
    
    for matrix in matrices:
        dtype = matrix.dtype
        
        # Conversion en float32 pour éviter les erreurs numériques
        matrix = matrix.astype(np.float32)
        
        # Normalisation en fonction du type de données
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
        
        normalized_matrices.append(matrix)
    
    return normalized_matrices

# Normaliser pixel_matrix, mat_mod2, et mat_mod3
normalized_pixel_matrix = normalize_matrices(pixel_matrix)
normalized_mat_mod2 = normalize_matrices(mat_mod2)
normalized_mat_mod3 = normalize_matrices(mat_mod3)

# Calculer la moyenne de chaque matrice
mean_pixel_matrix = np.mean(normalized_pixel_matrix[0])  # Moyenne de la première matrice de pixel_matrix
mean_mat_mod2 = np.mean(normalized_mat_mod2[0])  # Moyenne de la première matrice de mat_mod2
mean_mat_mod3 = np.mean(normalized_mat_mod3[0])  # Moyenne de la première matrice de mat_mod3

# Affichage des moyennes
print('\n')
print(f"Moyenne de pixel_matrix : {mean_pixel_matrix}")
print(f"Moyenne de mat_mod2 : {mean_mat_mod2}")
print(f"Moyenne de mat_mod3 : {mean_mat_mod3}")

# Calculer la différence entre pixel_matrix et mat_mod3
difference1 = np.abs(normalized_pixel_matrix[0] - normalized_mat_mod3[0])

# Moyenne de la différence
mean_difference = np.mean(difference1)

# Affichage de la moyenne des différences
print(f"Moyenne des différences entre pixel_matrix et mat_mod3 : {mean_difference}")


############# Afficher les images ###############

# Créer une instance de la classe ImageDisplay pour afficher les 2 images
Images = ImageDisplay(
    images=[normalized_pixel_matrix, normalized_mat_mod3],
    titles=["Image Originale", "Image Modifiée (Gamma puis Gamma Inverse)"]
)
# Afficher les images
Images.show()

