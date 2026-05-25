# 🚀 Step-by-Step: Creating & Linking Your New Git Repository

I saw the terminal errors in your screenshot! The reason you saw `fatal: --local can only be used inside a git repository` is because **Git has not been initialized in this folder yet**. 

Before configuring or pushing, we must initialize a Git database (the `.git` hidden folder) in this project.

Here is the exact sequence to initialize your local folder and link it to a brand-new GitHub repository under your preferred account (`KrushnkantKulkarni`).

---

## 🛠️ Step 1: Initialize Your Local Git Repository

Open your PowerShell terminal inside `e:\ai-projects\Rag-project-Ant` and run the following commands in order:

### 1. Initialize Git
This creates the hidden `.git` folder and sets your default branch name to `main`:
```powershell
git init -b main
```

### 2. Configure Your Identity (Locally)
Now that the Git repository is initialized, configuring your identity locally will succeed! Run:
```powershell
git config --local user.name "KrushnkantKulkarni"
git config --local user.email "kkulkarni@gmail.com"
```
*(Verify it by running `git config --local -l`)*

---

## 📂 Step 2: Make Your First Local Commit

Now, let's save your current files (including the `.gitignore` you created) into Git's local history.

### 1. Stage all files
This prepares your files for the commit:
```powershell
git add .
```

### 2. Create the initial commit
This saves a snapshot of the files locally:
```powershell
git commit -m "chore: initial commit with gitignore and guides"
```

---

## 🌐 Step 3: Create a New Remote Repository on GitHub

Next, we need to create a remote repository on GitHub to receive your code.

1. Open your browser and go to: **[github.com/new](https://github.com/new)**
2. Make sure you are logged into your **`KrushnkantKulkarni`** account.
3. Fill in the repository details:
   * **Repository name**: `Rag-project-Ant`
   * **Description**: *(Optional)* "RAG Observability and Failure Forensics Tool"
   * **Public/Private**: Select your preferred visibility.
4. > [!WARNING]
   > **DO NOT** check any of these boxes:
   > * [ ] Add a README file
   > * [ ] Add .gitignore
   > * [ ] Choose a license
   >
   > *(Since we already created and committed these files locally, checking these boxes will cause a merge conflict immediately.)*
5. Click the green **Create repository** button at the bottom.

---

## 🔗 Step 4: Link Your Local Folder to GitHub & Push

Once created, GitHub will show you a page with your repository's URL. Copy the URL (either HTTPS or SSH) and run the matching commands below:

### 🔹 Option A: If using HTTPS (easiest default)
Run these commands in PowerShell:
```powershell
# 1. Add your GitHub repository as the remote destination
git remote add origin https://github.com/KrushnkantKulkarni/Rag-project-Ant.git

# 2. Push your main branch to GitHub
git push -u origin main
```
*When prompted by Windows, log in or select your `KrushnkantKulkarni` credentials.*

### 🔹 Option B: If using SSH (Best for multiple accounts)
If you set up the custom SSH host alias (`github-ant`) in your `~/.ssh/config` file (as detailed in the [github_multi_account_guide.md](file:///e:/ai-projects/Rag-project-Ant/github_multi_account_guide.md)), run:
```powershell
# 1. Add remote using the custom SSH host alias
git remote add origin git@github-ant:KrushnkantKulkarni/Rag-project-Ant.git

# 2. Push your main branch to GitHub
git push -u origin main
```

---

## 🔍 How to Verify Everything is Connected Correctly

To make sure your remote tracking is fully set up, you can run:

```powershell
# Check the remote URL
git remote -v

# Check status (should say "Your branch is up to date with 'origin/main'")
git status
```

Once this is complete, you are fully set up! You can then proceed with your development lifecycle and begin using active slash commands like `/build-phase`.
