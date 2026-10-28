#!/bin/bash
clear

# Forzar limpieza profunda de pantalla
printf "\033[3J\033[H\033[2J"

# Lanzamos el agente de Python que ahora controlará TODA la interfaz y la animación
python agente_padrino.py
