# Script PowerShell pour renommer automatiquement les fichiers CamScanner en Reçu #X.pdf

# Dossier courant = là où tu mets le script
$folder = Get-Location

# Chercher tous les fichiers PDF qui contiennent CamScanner
$files = Get-ChildItem -Path $folder -Filter .pdf  Where-Object { $_.Name -match CamScanner }

foreach ($file in $files) {
    # Récupère le dernier nombre dans le nom
    if ($file.Name -match (d+).pdf$) {
        $num = $matches[1]
        $newName = Reçu #$num.pdf
        $newPath = Join-Path $folder $newName

        # Évite d’écraser un fichier existant
        $i = 1
        while (Test-Path $newPath) {
            $newName = Reçu #$num ($i).pdf
            $newPath = Join-Path $folder $newName
            $i++
        }

        # Renommer
        Rename-Item -Path $file.FullName -NewName $newName
        Write-Output Renommé $($file.Name) - $newName
    }
}
