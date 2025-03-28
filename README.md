# DSL for Metadata Editing of Media Files

## Requirements
- Have Python 3.9+
- Have pip (preferably 22.x.x+)
- Nice to have: Pycharm

## Before making ANY changes
Before writing any code, everytime you open your code editor, write these commands in the command line:
```
git fetch
git pull origin dev
git pull origin <current branch>
```
`git fetch` - download the latest remote changes from  Github

`git pull origin dev` - get merged changes from dev branch

`git pull origin <current branch>` - get any possible remote changes on your branch. **Make sure to do it to avoid merge conflicts**

To see your current branch, use `git status`

## How to make new changes
1) Select a new task from "Todo" of [DSL Project](https://github.com/users/IacovlevMaxim/projects/1)
2) Run the commands from "Before making ANY changes" section
3) Make sure you are on dev branch (see using `git status`). If you are in a branch of your another task, see "How to Branch" section. If you want to change to dev (and you know what you are doing), run `git checkout dev` to change to dev branch.
4) Create a new branch for your task using `git checkout -b <new branch name>`. Please make sure the branch name is descriptive of the task you are doing.
5) Now you can commit to this branch any changes that are related to the task. Make sure to commit everytime an integral part of the task works, so that in case some new change breaks the code indefinitely, you can go back in time to when it worked.
6) When you are sure the tasks is done, run `git push origin <the branch of your task>`. Command line will prompt you to open a pull request, similar to the example below. Click on the link and create a pull request. Go to [DSL Project](https://github.com/users/IacovlevMaxim/projects/1) and move your task to "Review" column. Attach the pull request link to the task. Max will make sure the contribution is correct. If something is wrong, you will be able to push your changes. If everything is ok, I will merge your changes into dev and move your task to Done. Hooray!
```
Create a pull request for 'dev' on GitHub by visiting:
https://github.com/IacovlevMaxim/dsl/pull/new/dev
```

## How to collaborate
This is very important. Parts of a big project such as DSL cannot be developed independently, without considering the bigger picture. The following guidelines are introduced to make sure the collaboration is hand-in-hand and efficient.
1) Write readable code. Python is notorious for "circus trick" approaches and implementation, and that is the last thing we want. Try to write in a way that others will understand, even if it might be a bit less efficient. If by looking at the code it is not evident why or how it works, add a comment with explanation. If you do not know why or how it works, also write it down or ask your peers.
2) Write maintainable code. Split it into functions, avoid hard-coding, define self-explanatory variables that can later be reused. Remove stuff that is not necessary.
3) Ask for help. Everyone in the team is interested in finishing this project, so do not hesitate to ask for help, especially if it regarding the code written by others. If you feel like a task is too hard for you, tell the teammates about it.
4) Notify of any change in status of task. Write in the group chat when you start a task, when you opened a pull request and when it is merged.
5) Write tests for your code. Development of a DSL is quite entangled, with many parts dependent of each other. To make sure one change does not break another one, it is very highly encouraged to write unit tests for the code that you have written. With correctly written unit tests that cover all atomic possibilities, you will be sure that your changes are correct.

## How to write unit tests
Take as an example tests/unit/print.py file. Each file defines a test class, inside of which goes one function that tests a specific rule. Make sure that the tests are minimal and only include your part of the code. After running a test set, you will be able to see which test pass and which fail. Your goal is to write test cases that cover all possibilities and to get a 100% pass rate. 

## How to Branch
Never branch from main. All branches should be made from dev and merged into dev.

I will write down possible scenarios of branching, if you dont find your scenario here, please write to Max.

### I just installed the repo and want to make my first task.
Just follow the "How to make new changes" section

### I finished one task and want to start another one
Everything described below is **not recommended**, if you are not quite familiar with Github. You might run into merge conflicts, forget to do a pull from remote, or branch out from different place, in which case it might be difficult to untangle. However, I tried my best to describe the process below. 

If your new task is completely independent of the one you just did, meaning that 
1) No changes from your first task will affect the code from second task, or vice versa
2) Second task does not depend on the code from first task, 

then you can simply do `git checkout dev`, run commands from "Before making ANY changes" section and then create the branch for your new task. 

If you want to be safe that your code does not overlap with your previously completed task, you can create a new branch from your current task.

For example, you have just completed a task, which is on branch `task1`. In this case, `git status` will return `On branch task1`. Now, to start another task `task2` which builds upon `task1`, you can create branch `task2` **from `task1`** by using `git checkout -b task2` (again, make sure `git status` returns `On branch task1`). 

When you are done with `task2`, perform `git push origin task2` and create a new pull request. If by the time you complete `task2` the branch `task1` got merged into `dev`, I am pretty sure you can merge `task2` directly into `dev`. If `task1` has not been merged yet, open a pull request from `task2` into `task1`. 

### Whoops, I branched out from the wrong place, what should I do?
Not good. 

If you have not done any changes and just ran a malformed `git checkout -b`, that's good. Remove the branch and create a correct one.

If you have done changes but have not committed anything yet, make sure to stash your changes using `git stash`. This will save your changes without committing them anywhere. Make sure to run `git status` to see if there are not uncommited changes and `git log` to make sure there are no commits made on this branch. After stashing your changes, correctly create the branch and run `git stash pop`, which will return all your changes back into the code.

If you have done changes *and* committed them, really not good. Write to Max.

