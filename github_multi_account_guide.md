# 🐙 Managing Multiple GitHub Accounts on Your Local PC

If you have multiple GitHub accounts on your local machine (e.g., personal, work, and client accounts), you might wonder: **Which account will the Antigravity AI use when committing or pushing?**

This guide explains how Git integration works with the AI, reassures you about your `.gitignore` configuration, and provides step-by-step instructions on how to seamlessly configure your local PC to route Git operations to the correct GitHub account.

---

## 🔍 How Does the AI Access GitHub?

> [!IMPORTANT]
> **The AI does NOT have its own independent GitHub account, cloud session, or separate credentials.**
>
> When the AI runs Git commands (like `/ship-phase`, `git push`, or `git commit`), it executes them **directly in your local shell (PowerShell/terminal)** using your system's `git` installation. 

Therefore:
* **The AI acts as you.** It inherits whatever Git credentials, SSH keys, configuration scopes, and authorization mechanisms are active on your computer.
* If your local terminal is configured to use account **A**, the AI will use account **A**.
* If you tell Git to use a specific SSH key or HTTPS token for this repository, the AI will automatically use that configuration.

---

## 🛡️ Your `.gitignore` is Perfect!

First, don't worry about creating the `.gitignore` by mistake. The `.gitignore` file you created is **exactly correct** and contains all the necessary exclusions for:
* Python virtual environments (`.venv/`)
* Local databases and traces (`traces.db`, `traces/`)
* Secret environment variables (`.env`, `.env.local`)
* OS-specific system files (`.DS_Store`, `Thumbs.db`)

You are completely safe, and these files will never be accidentally committed to any of your GitHub accounts.

---

## 🛠️ How to Configure Git for Multiple GitHub Accounts

To make sure your commits are made under the correct account and pushed to the right repository, you can use one of the two standard Git methods.

### 📋 Checklist Before Starting
For this repository (`Rag-project-Ant`), decide which GitHub account you want to use. Then, choose one of the two methods below to configure it:
* **Method 1: SSH Keys (Recommended & Most Robust)** — Best if you want completely isolated accounts without typing passwords/tokens.
* **Method 2: HTTPS with Repository-Specific Credentials** — Easiest if you prefer simple login tokens.

---

### 🔑 Method 1: SSH Key Routing (Recommended)

SSH key routing is the cleanest way to manage multiple accounts. You generate a unique SSH key for each GitHub account and use an SSH configuration file to map them.

#### 1. Generate a Dedicated SSH Key for This Project
Open your PowerShell terminal and run:
```powershell
ssh-keygen -t ed25519 -C "your-email-for-this-account@example.com" -f "$env:USERPROFILE\.ssh\id_ed25519_project_ant"
```
*(Press Enter when prompted for a passphrase to leave it empty, or choose a passphrase you remember.)*

#### 2. Add the SSH Key to Your GitHub Account
1. Open the public key file in a text editor or view it in PowerShell:
   ```powershell
   cat ~\.ssh\id_ed25519_project_ant.pub
   ```
2. Copy the entire output string starting with `ssh-ed25519`.
3. Go to **GitHub** ➔ **Settings** ➔ **SSH and GPG keys** ➔ **New SSH Key**.
4. Give it a title (e.g., "Antigravity Local PC") and paste the key.

#### 3. Configure Your SSH Config File
Create or modify your local SSH configuration file.
File path: `C:\Users\<Your-Username>\.ssh\config` (Create the `config` file without an extension if it doesn't exist).

Add a custom host block for this specific account:

```text
# --- Personal Account (Default) ---
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519

# --- Project-Specific Account (For Rag-project-Ant) ---
Host github-ant
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_project_ant
    IdentitiesOnly yes
```

#### 4. Configure Your Git Remote URL
Now, when you link your local repository to GitHub, instead of using the standard clone URL:
`git@github.com:your-username/Rag-project-Ant.git`

Use your **custom host alias** (`github-ant`):
```powershell
git remote add origin git@github-ant:your-username/Rag-project-Ant.git
```
*(If you already added the remote, you can update it using:)*
```powershell
git remote set-url origin git@github-ant:your-username/Rag-project-Ant.git
```

**Why this works:** Every time Git connects to `github-ant`, your SSH client will automatically use the dedicated key `id_ed25519_project_ant`, connecting you to the correct GitHub account!

---

### 🌐 Method 2: HTTPS with Git Credential Manager (GCM)

If you cloned using HTTPS (`https://github.com/username/repo.git`), Windows uses **Git Credential Manager** to save your login tokens.

To prevent Git from using a cached token from another account:

1. Open the **Windows Credential Manager** (Search "Credential Manager" in the Windows start menu).
2. Go to **Windows Credentials**.
3. Look for entries named `git:https://github.com`.
4. If you see credentials belonging to a different account, you can **Remove** them.
5. The next time the AI or you run a `git push`, Git Credential Manager will pop up a window asking you to log in. Simply log into the account you wish to use for this project.

---

## 👤 Step 2: Set Your Commit Author Details (Crucial!)

Regardless of how you connect (SSH or HTTPS), Git tags each commit with a name and email. If you don't configure this, your commits might show up under the wrong account name on GitHub.

Open your PowerShell terminal **inside your project folder** (`e:\ai-projects\Rag-project-Ant`) and configure your account local settings:

```powershell
# Set the name and email ONLY for this repository (omitting --global)
git config --local user.name "Your Account Name"
git config --local user.email "your-email-for-this-account@example.com"
```

> [!TIP]
> Always verify your local repository settings by running:
> ```powershell
> git config --local -l
> ```
> This guarantees that all commits authored in this directory use the correct developer identity.

---

## 🧪 Step 3: Test Your Connection

To verify that Git is correctly identifying you under the desired account, run the appropriate command:

### For SSH Setup (Method 1)
Run:
```powershell
ssh -T git@github-ant
```
You should see a message like:
> *Hi your-username! You've successfully authenticated, but GitHub does not provide shell access.*

### For HTTPS Setup (Method 2)
Run:
```powershell
git push -u origin main
```
If you are prompted to log in, log in with the correct account. If it succeeds, the credentials are successfully cached specifically for this URL.
