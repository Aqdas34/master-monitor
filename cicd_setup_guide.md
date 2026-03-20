### 1. Generate an SSH Key (on your local machine)
If you don't have an SSH key yet, run this command in your terminal:
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```
- Press **Enter** to save it in the default location (`C:\Users\YourName\.ssh\id_rsa`).
- **Do not** add a passphrase (leave it empty) so GitHub can use it automatically.

### 2. How to get the Private Key (for GitHub Secrets)
1. Navigate to your `.ssh` folder (usually `C:\Users\YourName\.ssh\`).
2. Open the file named `id_rsa` (the one **without** .pub) in a text editor like Notepad.
3. Copy the **entire** content, including the `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` lines.
4. Paste this into the **`SSH_PRIVATE_KEY`** secret in GitHub.

### 3. Add the Public Key to your VPS
GitHub needs permission to log in. You must add the **Public Key** (`id_rsa.pub`) to your VPS:
1. Open `id_rsa.pub` and copy its content.
2. Log in to your VPS: `ssh devuser3@157.173.120.125`.
3. Run these commands:
   ```bash
   mkdir -p ~/.ssh
   echo "PASTE_YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

### 4. GitHub Repository Secrets
Once the keys are set up, add these to your repository (`Settings > Secrets and variables > Actions`):

| Secret Name | Value |
|-------------|-------|
| `SSH_HOST` | `157.173.120.125` |
| `SSH_USER` | `devuser3` |
| `SSH_PRIVATE_KEY` | Paste your **Private SSH Key** |

### 5. Automated VPS Setup (Critical!)
The GitHub Actions workflow uses `sudo` to manage your server. Since GitHub cannot type your password, you **MUST** enable passwordless sudo for your user:

1.  **Log in to your VPS**:
    ```bash
    ssh devuser3@157.173.120.125
    ```
2.  **Run this exact command**:
    ```bash
    echo "devuser3 ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/devuser3
    ```
    *This allows the CI/CD to update your app and restart services without getting stuck at a password prompt.*

3.  **Ensure Git and Venv are installed**:
    ```bash
    sudo apt update && sudo apt install git python3-venv -y
    ```

After running the `NOPASSWD` command, go to GitHub and click **Re-run all jobs** in the Actions tab. It should now pass successfully!
