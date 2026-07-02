#!/bin/bash
# Clean script for FastArch repository

set -e

echo "🧹 Limpiando FastArch repo..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contadores
deleted=0

# Función para contar archivos eliminados
remove_and_count() {
    local pattern=$1
    local desc=$2
    local count=$(find . -type d -name "$pattern" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        echo -e "${YELLOW}  Eliminando $count directorios de $desc${NC}"
        find . -type d -name "$pattern" -exec rm -rf {} + 2>/dev/null || true
        deleted=$((deleted + count))
    fi
}

# Limpiar directorios de caché
remove_and_count "__pycache__" "__pycache__"
remove_and_count ".pytest_cache" "pytest cache"
remove_and_count "*.egg-info" "egg-info"
remove_and_count ".ruff_cache" "ruff cache"

# Limpiar archivos .pyc
echo -e "${YELLOW}  Eliminando archivos .pyc${NC}"
find . -type f -name "*.pyc" -delete
echo -e "${YELLOW}  Eliminando archivos .pyo${NC}"
find . -type f -name "*.pyo" -delete

# Limpiar archivos de cobertura
if [ -f ".coverage" ]; then
    echo -e "${YELLOW}  Eliminando .coverage${NC}"
    rm -f .coverage
    deleted=$((deleted + 1))
fi

# Limpiar htmlcov
if [ -d "htmlcov" ]; then
    echo -e "${YELLOW}  Eliminando directorio htmlcov${NC}"
    rm -rf htmlcov
    deleted=$((deleted + 1))
fi

# Opción: limpiar venv
if [ "$1" = "--venv" ] || [ "$1" = "-v" ]; then
    if [ -d ".venv" ]; then
        echo -e "${RED}  Eliminando .venv${NC}"
        rm -rf .venv
        deleted=$((deleted + 1))
    fi
fi

echo ""
echo -e "${GREEN}✅ Limpieza completada!${NC}"
echo -e "   Items eliminados: ${YELLOW}~$deleted${NC}"

if [ "$1" != "--venv" ] && [ "$1" != "-v" ]; then
    echo ""
    echo -e "${YELLOW}💡 Usa './clean.sh --venv' para también eliminar el venv${NC}"
fi
