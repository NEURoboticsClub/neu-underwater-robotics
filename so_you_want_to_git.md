# So You Want to Git...

### Before You Begin
If you’re already comfortable with git, feel free to use this document as a refresher, or just skip over most of it. If you’re uncertain, I do recommend at least skimming it to ensure that you’re following best practices and don’t end up with issues later that are difficult to solve. EVERYONE should read the house rules, regardless of how good you are with git. I’ve included a short list of common problems and troubleshooting advice, but don’t be afraid to ask someone else for help if you don’t feel comfortable resolving the issue yourself or if your error isn’t on the list. The list will also grow as issues pop up. This is a learning environment, and we’re all happy to help :)

## Git Basics

### What is Git?
Github probably has some tagline that I can’t remember that explains what it does in one nice, neat little sentence, but at its core, github is like google drive for code. It’s a tool that enables multiple people to work on one codebase at the same time. This is accomplished, in essence, through _branches_, _commits_, and _merges_.

### Basic Git Structure 
A github repository is a codebase that’s hosted remotely by github. This remote repository can be _cloned_ into a local repository on your own computer. Importantly, the local repository you work on does not auto-update to the remote repository. In other words, local changes will remain local until you _push_ them. This is bidirectional – your local repository won’t reflect remote changes unless you _pull_ them.

Every github repository has a number of branches, always including one main branch called _main_ (or _master_, depending on when the repository was created). Think of _main_ as the most up-to-date release of the code. Other branches are in development and basically contain suggestions.

### Cloning a Respository 
The first thing you’ll want to do to get started with software development is clone the neu-underwater-robotics repository. The process for cloning a repository is as follows:

1. Find the repository you want to clone on github (in this case, github.com/neuroboticsclub/neu-underwater-robotics).
2. On the repo’s main page, hit “code.”
3. If you’ve set up an ssh key, copy the “ssh” link under the “local” tab. if you haven’t [set up an ssh key](software_setup.md), you should do so, but for now just copy the “https” link under the “local” tab.
4. Open a terminal. If you’re on windows, your default is powershell, but we recommend you get Windows terminal. If you’re on Mac or Linux, your default terminal is fine.
5. From there run:
    >```
    >git clone [link-to-repo] [path-to-desired-repo-location] 
    >```
    Or cd into your desired folder location for the repo and run:
    >```
    >git clone [link-to-repo]
    >```

### Basic Version Control
There are two basic commands for updating your local repository: 
```
git fetch
git pull
```
__git fetch__ will essentially download the changelog from the remote repository. Your local repository will now know what changes have been made in the remote repository, but it won’t implement them in the local instance. Notably, a __git fetch__ will fetch the changelog for all branches. In order to actually implement those changes, you’ll have to run __git pull__. __git pull__ will “pull” the remote changes from the branch that you’re on (and only the branch that you’re on) into the local branch. Notably, __git pull__ runs __git fetch__ as a prerequisite, so whenever you pull, git will also automatically fetch changes to all branches. Always remember that pulling on one branch will not pull on another. This is very important when doing things like merges.

## Git Status

### When to Fetch
A git fetch is primarily useful when you want to know if any changes have been made to the branch you’re on, or to main, without making any changes to the branch you’re working on. You’ll mostly be using this before you commit and push.

### When to Pull
You should git pull in any of these scenarios:
* You’re about to make a new branch
* You’re about to start making changes to a branch
* You’re about to make a commit (see “Commit and Push Your Changes”)

## Your First Pull Request

### Make a Branch
There are two primary commands that are relevant when making a branch: 
```
git branch 
git checkout
```
__git branch__ [branch-name] creates a new branch (locally). __git checkout__ [branch-name] switches to a branch. These commands can be combined using the -b flag to git checkout.

To checkout to main:
>```
>git checkout main
>```
To make sure your local branch is up to date with origin/main:
>```
>git pull
>```
To create a new branch and switch to it.
>```
>git checkout -b [branch-name]
>```
To push the new branch to the remote repository, such that the new branch now exists remotely as well: 
>```
>git push --set-upstream origin [branch-name]
>```
If you can’t remember that whole thing, just __git push__. Git will give you an error and feed you the command you need to use, so you can just copy and paste it.

Now, start making changes!

### Commit and Push Your Changes
1. Make sure there are no un-pulled remote changes. You can do this by running:
```
git fetch
git status
```
If git status tells you that you’re up to date with origin/[branch-name], you’re good to go. If not, the quickest way to fix it is to (in order) run
```
git stash
git pull
git stash pop
```
This may result in some merge conflicts. If that happens, refer to “Resolving Merge Conflicts,” then carry on.

2. Next, to stage all of your changes:
```
git add . 
```
or
```
git add --all
```
They do the same thing. If you don’t want to commit all of your changes and don’t know how to go about accomplishing that yourself, ask a senior member of the software team.
3. Now to commit the changes you stages:
```
git commit -m “[insert commit message]”
```
Make sure this message is descriptive – see the “Making Commits” section of the house rules for details on what that means.
4. Finally:
```
git push
```
### Make a Pull Request
1. Got to github.com and sign in.
2. Navigate to the neu-underwater-robotics repository.
3. If you’ve just pushed a commit, there should be a banner saying that there have been new changes to whatever branch you’re on, along with a link to compare and pull request. If this is the case, click it. If not, find your branch in the dropdown that says “main”. Under the header for the branch, there should be a banner saying “This branch is x commits ahead of, y commits behind main.” Click the hyperlink on “x commits ahead of”, then click the green “Create pull request” button on the page it sends you to.
4. The title of your pull request should be the same as the branch name, which should be the same as the name of the issue it’s associated with. Fill out the description in accordance with the pull request template, which should autofill in the description when you open the pull request editor.
5. In the header that shows the branches you’re comparing, there should be a green or red piece of text that tells you whether the branch can be automatically merged. If your branch can be automatically merged, go ahead and hit the green “Create pull request” button, then move on to the next step. If it _can’t_, hit the arrow next to that button and select “Create draft pull request,” then hit the button, which should now be grey and say “Draft pull request.” Then, refer to “Resolving Merge Conflicts.” Once you’ve resolved your conflicts, you can make your draft into a proper pull request, then move onto the next step.
6. Request a review from Mia and/or another experienced member of the software team.

### Resolving Merge Conflicts
This process is specifically for merging changes from main into a branch you’re working on. If you want to merge changes from a branch other than main, follow the steps like normal, but with whatever branch you’re merging with instead of main. If you ever encounter merge conflicts in another context (like when running __git stash pop__), just skip steps 1 and 2.
1. Pull the most recent version of main (git checkout main, git pull), then checkout your branch.
2. Run
```
git merge main
```
3. Git will give you an error in the terminal telling you that you have merge conflicts and to resolve them before committing your merge. It should also give you a list of files that have conflicts. For each of those files:
    1. Open the file in your IDE.
    2. Find each spot in the file where you see __“<<<<<<< HEAD”__, __“=======”__, and __“>>>>>>> main”__ (“main” will be the name of whatever branch you’re merging with if you’re merging with a branch other than main).
    3. Pick which change you want to keep, then delete the other change, along with the three line breaks listed in step ii. above.
    4. Once you’ve done this for each conflict in the file, make sure it looks clean and has the correct changes before moving on.
4. Once you’ve resolved each conflict in each file, commit and push like normal.
5. You’re good to go :)

### Merging a Pull Request
1. Once you’ve requested a review on your pull request, wait for your reviewer to add their comments.
2. If your reviewer left comments on your pull requests, even if it’s just for code organization or comments, please go through and make the requested changes. If you have questions, don’t be afraid to find your reviewer and ask. Once you’re done making changes, commit and push, then re-request a review from your reviewer. Repeat until your pull request is approved.
3. Once your pull request is approved and there are no unresolved comments, go ahead and merge by clicking the green “Squash and Merge” button at the bottom of the pull request page. If the button doesn’t say “Squash and Merge,” don’t click it. Hit the arrow, then find and click the squash and merge option, _then_ hit the green button.
4. Once your pull request is successfully merged, remember to delete your branch. They can always be recovered later, but this helps keep our repository free of clutter.

## House Rules

### Creating a New Branch
* __Branches should be named according to the github issue they’re associated with.__ For example, a branch for the 40th issue “implement claw” would be called _40-implement-claw_.
* __Remember to link your branch to the relevant github issue.__ This can be done by navigating to the issue on github.com, clicking the gear next to “Development” in the right-hand sidebar, searching for the name of the branch you’re working on, and clicking it in the dropdown, to link it to the issue.

### Making Commits
* __Commit your changes often.__ As a rule of thumb, you should be committing, at minimum, whenever you shut down for the day. If life pulls you away and you can’t come to the club for a few weeks, it’s not great if your code changes are just sitting on your computer, inaccessible to everyone else. It’s also good practice to commit whenever you finish a sub-task of whatever issue you’re working on, kind of like indenting a new paragraph. For example, a sub-task of “implement claw” might be “create claw class”. This keeps the git history clear and makes it easy to revert specific changes.
* __Make sure you’re writing descriptive commit messages.__ A commit message should describe all of the changes you made in that commit. Someone should be able to understand the gist of what you did on a branch and when just from reading the commit history.

### Pull Requests
* __Always squash and merge.__
* __Follow the pull request template.__
* Before you submit the pull request, __remember to request a review__ from Mia or, if they’re not available, from a member of the software team who’s been here for a while. This helps ensure that pull requests are reviewed and merged in a timely manner, which prevents conflicts down the line.
* __Smaller pull requests are generally better.__ It’s better to merge changes in batches of smaller changes than to make one giant pull request. Obviously, don’t merge code that doesn’t work on its own, but also don’t wait until every part of a huge task is done to merge it. You can always make a new branch and a new pull request, and updating main incrementally helps keep the code current and prevents a lot of the issues that are associated with huge merge commits. It’s a balancing act, so ask someone if you’re ever unsure.
* __Make sure that your branch is up to date with main and is able to be merged automatically__ (i.e. there are no merge conflicts) before making your pull request. If this isn’t the case, make a draft pull request and refer to “Resolving merge conflicts” if you don’t already know how.

## Common Problems and Troubleshooting Tips

### Pushing When You Haven't Pulled Remote Changes

This error occurs when you try to push a commit to a remote branch that’s ahead of your local branch by some number of commits. Luckily, it’s an easy fix if you know how:
1. You need to pull the changes that you don’t have from the remote branch. Unfortunately, because you have a staged commit on your local branch, you can’t just __git pull__. Instead, you have to use the “rebase” flag:
```
git pull --rebase.
```
2. Now you can push like normal:
```
git push
```

### Undoing a Commit
To “undo” a local commit (that hasn’t been pushed), you’ll want to run:
```
git reset --soft HEAD~1
```
This will unstage the committed changes and get rid of the local commit. The __“--soft”__ flag prevents git reset from changing the actual code, so all of your changes won’t be erased. HEAD~1 indicates the commit to reset to. HEAD is the most recent commit, and HEAD~x is the x-th commit before the most recent commit. Commands like __git reset__ and __git revert__ can get finicky, so _please_ ask someone if you’re not sure what you’re doing. It helps prevent a headache for everyone involved.































