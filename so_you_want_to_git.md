# So You Want to Git...

## Git Basics

### What is Git?
Github probably has some tagline that I can’t remember that explains what it does in one nice, neat little sentence, but at its core, Github is like Google Drive for code. It’s a tool that enables multiple people to work on one codebase at the same time. This is accomplished, in essence, through _branches_, _commits_, and _merges_.

### Basic Git Structure 
A github repository is a codebase that’s hosted remotely by Github. A repository can be cloned into a local repository which is stored on your local machine. Importantly, the local repository you work on does not auto-update to the remote repository. In other words, local changes will remain local until you push them.

Every github repository has a number of branches, always including one main branch called _main_ (or master, depending on when the repository was created). Think of main as the most up-to-date release of the code. other branches are in development and basically contain suggestions.

### Cloning a Respository 
1. Find the repository you want to clone on github.
2. On the repo’s main page, hit “code.”
3. If you’ve set up an ssh key, copy the “ssh” link under the “local” tab. if you haven’t [set up an ssh key](software_setup.md), you should do so, but for now just copy the “https” link under the “local” tab.
4. Open a terminal. If you’re on windows, your default is powershell, but we recommend you get windows terminal. If you’re on mac or linux, your default terminal is fine.
5. From there run:
    >```
    >git clone [link-to-repo] [path-to-desired-repo-location] 
    >```
    Or cd into your desired folder and run:
    >```
    >git clone [link-to-repo]
    >```

### Basic Version Control
Your local repository will not automatically update based on changes being made in the remote repository. There are two basic commands for updating your local repository: “git fetch” and “git pull”. “git fetch” will essentially download the changelog from the remote repository. Your local repository will now know what changes have been made in the remote repository, but it won’t implement them in the local instance. Notably, a git fetch will fetch the changelog for all branches. In order to actually implement those changes, you’ll have to run “git pull”. “git pull” will “pull” the remote changes from the branch that you’re on (and _only_ the branch that you’re on) into the local branch. Always remember that pulling on one branch will not pull on another. This is very important when doing things like git merge.

### When to Fetch
A git fetch is primarily useful when you want to know if any changes have been made to the branch you’re on, or to main, without making any changes to the branch you’re working on. If you’re not experienced with Github, you probably won’t be using this very often.

### When to Pull
There are two main relevant commands when making a branch: git branch and git checkout. 

To create a new branch called branch-name (locally) run:
>```
>git branch branch-name
>```
To switch to a different branch called branch-name run:
>```
>git checkout branch-name
>```
These commands can be combined by adding the -b flag to git checkout. For example, to create a new branch called branch name and switch to it run:
>```
>git checkout -b branch-name
>```

Once on your desired branch git pull to make sure your local main branch is up to date with origin/main:
>```
>git pull
>```


## House Rules

### Creating a New Branch
Branches should be named according to the github issue they’re associated with. for example, a branch for the issue “implement claw” would be called implement-claw.

Remember to link your branch to the relevant github issue.


### Making Commits 
Commit your changes often. as a rule of thumb, you should be committing, at minimum, whenever you shut down for the day. If life pulls you away and you can’t come to club for a few weeks, it’s suboptimal if your code changes are just sitting on your computer, inaccessible to everyone else. It’s also good practice to commit whenever you finish a sub-task of whatever issue you’re working on, kind of like indenting a new paragraph. For example, a sub-task of “implement claw” might be “create claw class”.

Make sure you’re writing descriptive commit messages. A commit message should describe all of the changes you made in that commit. Someone should be able to understand what you did and when on a branch just from reading the commit history.

### Pull Requests
Always squash and merge.
Follow the pull request template.
Before you submit the pull request, remember to request a review from Mia or if they are not available, from a software team member who has been here for a while.
Make sure that your branch is up to date with main and it’s able to be merged automatically (there are no merge conflicts).	
If there are merge conflicts you can go through and resolve them from within the pull request

## Common Problems and Troubleshooting Tips




