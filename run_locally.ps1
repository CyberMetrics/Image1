# Script to run services locally without Docker
Write-Host "Setting up environment..."

# 1. Install ML Dependencies
Write-Host "Installing ML Service requirements..."
pip install -r services/ml/requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install ML reqs"; exit }

# 2. Install Web Dependencies
Write-Host "Installing Web Service requirements..."
pip install -r services/web/requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install Web reqs"; exit }

# 3. Start ML Service (Background)
Write-Host "Starting ML Service on port 5001..."
$mlProcess = Start-Process python -ArgumentList "services/ml/app.py" -PassThru
Write-Host "ML Service started (PID: $($mlProcess.Id))"

# 4. Start Web Service (Foreground)
Write-Host "Starting Web Service on port 5000..."
$env:ML_SERVICE_URL="http://localhost:5001"
# Ensure MONGO_URI is set (using default from settings if not here, but setting explicitly is safer)
$env:MONGO_URI="mongodb+srv://satishpakalapati59_db_user:satish@cluster0.7salcwk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

python services/web/app.py
