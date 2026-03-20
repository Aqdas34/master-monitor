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

### 5. VPS Setup (No Sudo Required!)
Since you have restricted permissions, I've updated the workflow to deploy **directly inside your home directory** (`/home/devuser3/`).

**The ONLY things you need to do once are:**
1. Log in: `ssh devuser3@157.173.120.125`.
2. Run this once to ensure your user-level services keep running even after you log out:
   ```bash
   sudo loginctl enable-linger devuser3
   ```
   *(If you can't run this sudo command, don't worry—the app will still run as long as you are logged in, or we can use PM2 later).*

3. Ensure `git` and `python3-venv` are on the server:
   ```bash
   apt update && apt install git python3-venv -y 
   ```

**That's it!** The CI/CD will now automatically:
- Create `~/MasterMonitorServer`.
- Clone the code.
- Create the virtual environment.
- Register the app as a **User Service** (zero sudo needed).

Go to GitHub and click **Re-run all jobs**—it should work perfectly now!
