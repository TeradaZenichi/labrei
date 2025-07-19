#!/bin/bash
# ========================================
# Shell script to start LabREI Microgrid Docker Compose stack (Windows WSL/Git Bash)
# ========================================

# Move to script's directory (project root)
cd "$(dirname "$0")"

echo ""
echo "== Starting Docker Compose stack in detached mode =="
docker-compose up -d

if [ $? -ne 0 ]; then
    echo
    echo "[ERROR] Failed to start Docker Compose."
    exit 1
fi

echo
echo "== Showing running containers =="
docker-compose ps

echo
echo "== Tailing logs (press CTRL+C to stop) =="
docker-compose logs -f &

echo
echo "== Opening pgAdmin in the default browser =="
# For WSL/Git Bash: 'start' may not exist, use xdg-open or Windows start
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5050
elif command -v start > /dev/null; then
    start http://localhost:5050
else
    # Try Windows way via explorer
    explorer.exe "http://localhost:5050"
fi

echo
echo "== All done! Press any key to exit... =="
read -n 1 -s -r
