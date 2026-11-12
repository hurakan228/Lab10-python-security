The encrypted file `secrets.enc.env` is created locally by `scripts/setup-sops.ps1`.
Commit the encrypted file. Do not commit the plaintext file, `.env`, or the private age key.
The private age key is stored under your Windows home directory outside this project.
