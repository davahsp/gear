# GEAR Development Workflow
Made by Dava Hannas Putra

1. Open an <b>empty</b> directory that will be your repository root

2. Run the following command

    ```bash
    git clone -b development --single-branch https://gitlab.cs.ui.ac.id/propensi-2025-2026-genap/kelas-c/propensi-gacor/propensi-gacor-fullstack.git .
    ```
    
    This will clone only the `development` branch into your local repository.

3. Rename the local branch `development` into `feat/{your-feature}`

    ```bash
    git branch -m feat/{your-feature}
    ```

4. Set the default upstream to be `origin/feat/{your-feature}`

    ```bash
    git push -u origin feat/{your-feature}
    ```
  
5. Now as your local feature branch is tied to the correct corresponding remote feature branch, you can start your work and commits at your current local branch. Run and only run `git push` to push your commits to the default upstream, not directly to `origin/development`. Your work will be merged to `origin/development` via merge requests only.

6. To make a merge request on `Gitlab`, please create a MR with title following the following format.

    ```
    feat({your-feature}): overall changes you implement within a merge request. 
    do not use any uppercase letter. the description should start with a verb, 
    like implement carousel for home page, and fix bugs regarding sales management
    ```

    The merge request should have <b>both</b> `squash commit` and `delete branch after merge` option <b>checked</b>.

    Always request merge to `development` branch, not `staging`, let alone `main`. 

7. Wait for your merge request to be accepted and merged into `development`.

8. Please routinely pull from `origin/development` using the following command.

    ```
    git fetch origin development
    git rebase origin/development
    ```
  
    This will anticipate potential conflicts when issuing merge requests.

9. Contact Dava if you encounter merge request conflict.

10. After your merge request has been accepted and integrated to `development`, please run the following command

    ```bash
    git fetch origin development
    git reset --hard origin/development
    ```

    The command above makes your branch exactly matches the `development` branch so you can start committing your work again for next merge requests. Only do this when your MR has been accepted and you have not made any work since the MR was issued. If you have made commit(s) after the MR was issued and before the MR is accepted (not advised, though), please contact Dava