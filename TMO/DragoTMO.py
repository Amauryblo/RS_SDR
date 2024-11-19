# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 10:43:12 2024

@author: ablot
"""

### DragoTMO

import imageio
import sys
import os
from tools_package.Luminance import LuminanceCalculator


# Ajouter le répertoire parent (Project) au chemin de recherche
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Utiliser la classe
calculator = LuminanceCalculator("C://Users//ablot//Documents//PPMD//Python HDR//TMO//Scripts//image_hdr//memorial.tif")
luminance_image = calculator.calculate_luminance()
if luminance_image is not None:
    print(f"Luminance calculée : {luminance_image.shape}")

calculator.save_luminance_image("luminance_image.tif")