# Software Development Best Practices for the Northeastern Marine Robotics Team:
We aren't too strict about following this down to the letter, but try to stick to this as much as possible. If you have any questions, please ask in the `#software-development` channel in the discord, or feel free to DM me (Joshua) directly.

## Version Control:
- We use git for version control. If you don't know how, here's a [basic overview](https://rogerdudler.github.io/git-guide/). There are tons of great resources online, or ask at a meeting or in the discord.
- We have a write-protected branch called `main` which we will try to keep as the current version of code running on the ROV.
- When making changes, please create a new branch with `<name/initials>/<short-description-of-changes>` for example `jc/add-self-destruct-button`. Then create a pull request to merge your changes into `main`. This will allow us to review your changes before they are merged into the main branch.
- For pull requests: we won't have a formal requirement for code review, but please try to get at least one person to look at your code before merging.
> Important Note: The RaspberryPi's are signed in to a separate GitHub account. Please be careful that you are on the correct branch when making and pushing changes. Please commit and push changes when you are done, and if there are uncommitted changes on the pi, please stash them.

## Code Style:
- We use Python, so follow [PEP8](https://peps.python.org/pep-0008/). Line length of 100 characters is fine.
- Also encouraged to use an autoformatter such as [black](https://github.com/psf/black) and a linter such as [pylint](https://github.com/pylint-dev/pylint) or similar.
- Docstrings are encouraged but not required for all public functions. [Google style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) are preferred.
- General good coding practices such as descriptive variable names, comments, etc. are encouraged.
