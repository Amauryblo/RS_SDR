# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 23:18:19 2025

@author: ablot
"""

import inspect
import os

class MetadataLogger:
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        
    def log_function_call(self, func_name, **kwargs):
        """
        Enregistre le nom de la fonction et ses paramètres dans le fichier metadata_file.
        
        Parameters:
        - func_name (str): Le nom de la fonction appelée.
        - kwargs: Les paramètres de la fonction sous forme de paires clé-valeur.
        """
        try:
            with open(self.metadata_file, 'a') as file:
                file.write(f"Fonction appelée : {func_name}\n")
                file.write("Paramètres :\n")
                for param, value in kwargs.items():
                    file.write(f"  {param}: {value}\n")
                file.write("-" * 40 + "\n")
        except Exception as e:
            print(f"Erreur lors de l'enregistrement dans le fichier de métadonnées : {e}")
    
    def log_class_usage(self, class_name, **kwargs):
        """
        Enregistre l'utilisation d'une classe avec ses paramètres dans le fichier metadata_file.
        
        Parameters:
        - class_name (str): Le nom de la classe utilisée.
        - kwargs: Les paramètres de la classe sous forme de paires clé-valeur.
        """
        try:
            with open(self.metadata_file, 'a') as file:
                file.write(f"Classe utilisée : {class_name}\n")
                file.write("Paramètres :\n")
                for param, value in kwargs.items():
                    file.write(f"  {param}: {value}\n")
                file.write("-" * 40 + "\n")
        except Exception as e:
            print(f"Erreur lors de l'enregistrement dans le fichier de métadonnées : {e}")
