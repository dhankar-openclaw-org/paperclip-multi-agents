To bring a public GitHub fork completely up to date with the original repository (upstream)—including fetching and creating **all new branches** that have been added since you first made the fork—you cannot rely on GitHub’s web interface "Sync Fork" button. The web button only updates the specific branch you are currently viewing (usually `main` or `master`).

The absolute best practice is to execute a **Sync and Track Sequence** via your local Ubuntu terminal. Here is the step-by-step master workflow:

---

### Step 1: Link Your Local Repository to the Original (Upstream)

Open your terminal, navigate into your project workspace directory, and check your current remote links:

```bash
git remote -v

```

If you only see your personal fork (`origin`), you need to register the original master repository as a secondary network source named **`upstream`**:

```bash
# Add the original repository as 'upstream'
git remote add upstream https://github.com/ORIGINAL_OWNER/ORIGINAL_REPO.git

# Verify both paths now exist
git remote -v

```

*(Replace `ORIGINAL_OWNER/ORIGINAL_REPO` with the actual path of the primary project).*

---

### Step 2: Fetch Everything From the Original Source

Tell Git to pull down absolute tracking snapshots of all historical commits, tags, and branches that exist on the original repository:

```bash
git fetch upstream

```

This updates your local terminal's mapping references (`refs/remotes/upstream/*`) but does not alter your working files yet.

---

### Step 3: Fast-Forward Your Existing Main Branches

Switch to your primary integration branch (e.g., `main` or `master`) and merge the original project changes directly into it:

```bash
# 1. Switch to your local main branch
git checkout main

# 2. Merge the upstream changes to catch up instantly
git merge upstream/main

```

---

### Step 4: Track and Clone All New Upstream Branches

To pull down and track **all new branches** created on the original repository since you forked it, run this automated bash loop in your terminal window:

```bash
for branch in $(git branch -r | grep 'upstream/' | grep -v 'HEAD' | sed 's/upstream\///'); do
    git checkout -b "$branch" "upstream/$branch" 2>/dev/null || (git checkout "$branch" && git merge "upstream/$branch")
done

```

#### 🔍 What this automation loop does:

1. **`git branch -r`**: Scans all external remote branches on the network layer.
2. **`grep 'upstream/'`**: Filters the list to exclusively isolate tracking lines belonging to the original repository.
3. **`git checkout -b "$branch"`**: If a branch exists on the original repo but does not exist in your fork yet, this cleanly creates a matching local branch and locks it onto the original project's remote tracking target.
4. **`git merge`**: If you already have that branch locally, it safely updates it by fast-forwarding any new historical commits.

---

### Step 5: Push Everything Back to Your GitHub Public Fork

Now that your local machine is perfectly synchronized with the original project, push all your updated and brand-new branches back up to your public GitHub profile (`origin`) in one command:

```bash
git push origin --all

```

Go back to your GitHub browser dashboard page and refresh—your public fork will now state that every single branch is perfectly even and up to date with the original master repository!