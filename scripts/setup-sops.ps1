# Run in PowerShell from the unpacked project folder. Requires sops and age-keygen in PATH.
# Keeps the age private identity OUTSIDE Git, in $HOME\.lab10-private\age-key.txt
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$keyDir = Join-Path $HOME '.lab10-private'
$keyFile = Join-Path $keyDir 'age-key.txt'
$secretDir = Join-Path $root 'secrets'
$plain = Join-Path $secretDir 'temporary.env'
$encrypted = Join-Path $secretDir 'secrets.enc.env'

if (-not (Get-Command 'sops' -ErrorAction SilentlyContinue)) { throw 'Install SOPS from github.com/getsops/sops/releases, then open a NEW PowerShell window.' }
if (-not (Get-Command 'age-keygen' -ErrorAction SilentlyContinue)) { throw 'Install age from github.com/FiloSottile/age/releases, then open a NEW PowerShell window.' }
New-Item -ItemType Directory -Force -Path $keyDir, $secretDir | Out-Null
if (-not (Test-Path $keyFile)) {
  & age-keygen -o $keyFile
  if ($LASTEXITCODE -ne 0) { throw 'age-keygen failed' }
}
$recipient = (& age-keygen -y $keyFile).Trim()
if ($LASTEXITCODE -ne 0 -or -not $recipient.StartsWith('age1')) { throw 'age recipient missing' }
$sampleValue = 'lab10-demo-' + [guid]::NewGuid().ToString('N')
try {
  [System.IO.File]::WriteAllText($plain, "LAB10_API_KEY=$sampleValue`n", (New-Object System.Text.UTF8Encoding($false)))
  & sops encrypt --age $recipient --input-type dotenv --output-type dotenv --output $encrypted $plain
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $encrypted)) { throw 'SOPS encryption failed' }
} finally {
  Remove-Item -Force -ErrorAction SilentlyContinue $plain
}
$sopsConfig = Join-Path $root '.sops.yaml'
$configBody = "creation_rules:`n  - path_regex: '^secrets/.*\.enc\.env$'`n    age: '$recipient'`n"
[System.IO.File]::WriteAllText($sopsConfig, $configBody, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Encrypted file created: $encrypted"
Write-Host "Public age recipient recorded in .sops.yaml"
Write-Host "Your private age identity is OUTSIDE the project: $keyFile"
Write-Host 'Next: save the CONTENTS of this key file under GitHub repository secret LAB10_AGE_PRIVATE_KEY.'
Write-Host 'Never commit the private key or paste its content into a chat.'
Write-Host 'Commit only secrets/secrets.enc.env and optionally .sops.yaml with your PUBLIC age key.'
