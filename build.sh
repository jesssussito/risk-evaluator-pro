#!/usr/bin/env bash
# build.sh — Genera el ejecutable con PyInstaller.
# Uso: bash build.sh

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo ""
echo "================================================="
echo "  Risk Evaluator Pro — Build"
echo "================================================="

# 1. Verificar PyInstaller
if ! command -v pyinstaller &>/dev/null; then
    echo ""
    echo "[ERROR] pyinstaller no encontrado en PATH."
    echo "        Instálalo con: pip install pyinstaller"
    exit 1
fi

# 2. Limpiar artefactos anteriores
echo ""
echo "[1/3] Limpiando build/ y dist/..."
rm -rf build/ dist/
echo "      Hecho."

# 3. Ejecutar PyInstaller
echo ""
echo "[2/3] Ejecutando PyInstaller (main.spec)..."
echo "-------------------------------------------------"
if pyinstaller main.spec; then
    echo "-------------------------------------------------"
    echo ""
    echo "[3/3] Build completado con éxito."
    echo ""
    echo "  Ejecutable: dist/main.exe"
    echo "================================================="
    echo ""
else
    echo "-------------------------------------------------"
    echo ""
    echo "[ERROR] PyInstaller falló. Revisa los mensajes anteriores."
    echo "================================================="
    echo ""
    exit 1
fi
