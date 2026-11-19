$ErrorActionPreference = "Stop"
# Generate a demonstration certificate in Docker, not on the Windows filesystem.
docker volume create lab11_tls | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Failed to create Docker volume" }
$script = @'
apk add --no-cache openssl >/dev/null
openssl req -x509 -nodes -newkey rsa:2048 -sha256 -days 7 -keyout /certs/server.key -out /certs/server.crt -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
chown 101:101 /certs /certs/server.crt /certs/server.key
chmod 700 /certs
chmod 644 /certs/server.crt
chmod 600 /certs/server.key
'@
docker run --rm -v lab11_tls:/certs alpine:3.23 sh -ec $script
if ($LASTEXITCODE -ne 0) { throw "Failed to generate certificate" }
Write-Host "Created local SELF-SIGNED TLS certificate in Docker volume lab11_tls."
