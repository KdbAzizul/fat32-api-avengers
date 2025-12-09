# 1. Login to Docker Hub
Write-Host "Logging into Docker Hub..." -ForegroundColor Cyan
docker login

# 2. Define the Mapping: Local Folder Name -> Docker Hub Repo Name
# Make sure these match exactly what you created on Docker Hub
$serviceMap = @{
    "api-gateway"          = "demo-api-gateway"
    "frontend"             = "demo-frontend-service"
    "user-service"         = "demo-user-service"
    "campaign-service"     = "demo-campaign-service"
    "donation-service"     = "demo-donation-service"
    "payment-service"      = "demo-payment-service"
    "notification-service" = "demo-notification-service"
    "banking-service"      = "demo-banking-service"
}

$username = "shahriar22"

# 3. Loop using GetEnumerator (Safer method)
$serviceMap.GetEnumerator() | ForEach-Object {
    $localFolder = $_.Key
    $repoName = $_.Value
    
    # Validation check
    if ([string]::IsNullOrWhiteSpace($repoName)) {
        Write-Host "Skipping $localFolder because repo name is missing!" -ForegroundColor Red
        return # Skip to next
    }

    $fullImageName = "$username/$repoName:latest"

    Write-Host "---------------------------------------------------"
    Write-Host "Processing: $localFolder -> $fullImageName" -ForegroundColor Yellow
    Write-Host "---------------------------------------------------"

    # A. BUILD & TAG
    Write-Host "Building image..."
    docker build -t $fullImageName ./$localFolder

    if ($LASTEXITCODE -eq 0) {
        # B. PUSH
        Write-Host "Pushing to Docker Hub..."
        docker push $fullImageName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Success: $fullImageName" -ForegroundColor Green
        } else {
            Write-Host "❌ Error pushing: $fullImageName" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Error building: $localFolder" -ForegroundColor Red
    }
}

Write-Host "---------------------------------------------------"
Write-Host "All operations completed." -ForegroundColor Cyan