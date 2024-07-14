# Legal Beagles
 
#### Files
- **Dockerfile** : This file will be used to build the image of **worker** and **patch** in this repository.
- **docker-compose.yml** : This file will be used to build the image and run the extractor locally.
- **taskfile.yml** : This file contains multi step processes which will aid us in building and running extractor locally.
#### Directories
- **setup/** : This directory contains file required to setup extractor locally.
- **src/** : This directory contains extractor code.
- **tests/** : This directory will contain the test files.
#### This repository depends on the following other repositories
- https://gitlab.unicourt.net/codaxtr/core-3
- https://gitlab.unicourt.net/codaxtr/codaxtr-central
#### Required Packages for local setup 
- [git](https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu-20-04) 
- [docker](https://docs.docker.com/engine/install/ubuntu/)
- [docker-compose](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)
- [taskfile](https://taskfile.dev/installation/)
- [pycharm](https://www.jetbrains.com/help/pycharm/installation-guide.html) or vs code
- [terminator](https://linux.how2shout.com/install-terminator-terminal-emulator-in-ubuntu-22-04-lts/)
- [awscli](https://pypi.org/project/awscli/)
- [pip](https://linuxize.com/post/how-to-install-pip-on-ubuntu-20.04/)
- [python](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-an-ubuntu-20-04-server)
- [requests](https://pypi.org/project/requests/)
---

### Local Setup using **task**
- Task file describes various execution tasks via yaml, and its core is written in go; it is more modern and easier
    to use than Makefile’s tab splitting and bash combination syntax
- Documentation: [Task file](https://taskfile.dev/usage/)
#### How to install task file
- Run below command to install task
   ```commandline
    sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
   ```
  Doc :[installation](https://taskfile.dev/installation/)

#### Use below task commands to setup CA extractor locally.
1. Clone **legal-beagles** git repo
   1. First, go to https://gitlab.unicourt.net/codaxtr/garuda/legal-beagles and fork the repo.
   2. Then, clone the forked repo inside your workspace.
   3. After cloning, you should see directory named **legal-beagles**.
   4. Change the directory to **legal-beagles** and add upstream url for **legal-beagles**.
    ```shell
    git remote add upstream git@gitlab.unicourt.net:codaxtr/garuda/legal-beagles.git
    ```
2. Setup worker locally
   1. Run below task command to setup and run worker container.
   ```shell
    task all
    ```
---
### Task commands does following things.
   1. Install repository tools by running "python3 install.py" inside the "setup/local_setup/repo_tools" directory.
      ```shell
      cd setup/local_setup/repo_tools
      python3 install.py
      ```
      - The above command will install a pre-commit hook for git.The hook checks for mixed indentations. ie files indented using tabs and spaces. Ideally, we should either tabs OR spaces but not both.
   2. Create a new "docker-compose.yml" file in your project folder. If it already exists, this step is skipped.
      - Here we copy `setup/local_setup/sample-docker-compose.yml` file inside your project folder with name `docker-compose.yml`.
      - We skip this step if `docker-compose.yml` file is already exist.
   3. Add secrets to the "docker-compose.yml" file, reading them from AWS Secret Manager.
      - We read secrets from AWS secret manager and add them to `docker-compose.yml` file.
   4. Build worker and patch docker container.
      ```shell
      docker-compose up -d --build --remove-orphans
      ```
      - The above command creates worker and patch docker container.
      -   **--remove-orphans** : Allows the user to remove containers which were created in a previous run of docker-compose up, but which has since been deleted from the `docker-compose.yml` file.
   6. Run celery in worker container
      ```shell
         docker exec -it worker-legal-beagles sh -c  "celery -A extractor_celery worker -Q worker_download_document,worker_pc_refresh_case_by_case_number,worker_pc_docket_processing,worker_pc_history_processing,worker_pc_relate_case,worker_pc_county_import_case,worker_pc_parse_file,worker_pc_extractor_webhook,worker_pc_p_refresh_case_by_case_number,worker_pc_p_docket_processing,worker_pc_p_history_processing,worker_pc_p_download_document,worker_pc_p_extractor_webhook,worker_pc_case_decision_parsing,worker_pc_tp_refresh_case_by_case_number,worker_pc_tp_docket_processing,worker_pc_tp_history_processing,worker_pc_tp_download_document,worker_pc_tp_extractor_webhook,worker_extractor,worker_docket_processing,worker_history_processing,worker_relate_case,worker_county_import_case,worker_date_range_download,worker_parse_file,worker_schedule_run,worker_import_document_health_check,worker_case_extraction_health_check,worker_proxy_health_check,worker_ramp_up_date_range_extractor,worker_ramp_up_incremental_extractor,worker_ramp_up_date_range_download_extractor --loglevel=info --concurrency 1 -n w1.%h -Ofair --without-mingle --without-gossip --without-heartbeat -P solo --prefetch-multiplier=1"
      ```
      - The above command runs celery command inside worker container.
      - **exec** : Execute a command in a running container
      - **-c** : Runs command inside container.
      - Alternative command
         ``` shell
          docker exec -it worker-legal-beagles sh
          # Run celery command inside container manually.
          celery -A extractor_celery worker -Q worker_download_document,worker_pc_refresh_case_by_case_number,worker_pc_docket_processing,worker_pc_history_processing,worker_pc_relate_case,worker_pc_county_import_case,worker_pc_parse_file,worker_pc_extractor_webhook,worker_pc_p_refresh_case_by_case_number,worker_pc_p_docket_processing,worker_pc_p_history_processing,worker_pc_p_download_document,worker_pc_p_extractor_webhook,worker_pc_case_decision_parsing,worker_pc_tp_refresh_case_by_case_number,worker_pc_tp_docket_processing,worker_pc_tp_history_processing,worker_pc_tp_download_document,worker_pc_tp_extractor_webhook,worker_extractor,worker_docket_processing,worker_history_processing,worker_relate_case,worker_county_import_case,worker_date_range_download,worker_parse_file,worker_schedule_run,worker_import_document_health_check,worker_case_extraction_health_check,worker_proxy_health_check,worker_ramp_up_date_range_extractor,worker_ramp_up_incremental_extractor,worker_ramp_up_date_range_download_extractor --loglevel=info --concurrency 1 -n w1.%h -Ofair --without-mingle --without-gossip --without-heartbeat -P solo --prefetch-multiplier=1
         ```
---
## Useful task commands
1)  Running task `--list (or task -l)` lists all tasks with a description
    -   ```bash
        task -list-all
        ```
    -   ```bash
        task -l
        ```
    -   ```bash
        task -a
        ```
| cmd                    | aliases             | description                                    |
|:-----------------------|---------------------|:-----------------------------------------------|
| `task all`             |                     | Complete setup                                 |
| `task run`             |                     | Run docker container.                          |
| `task add_secret`      |                     | Add credentials to Worker docker compose file. |
| `task core:auth`       | `task c:auth`       | aws authentication.                            |
| `task core:build`      | `task c:build`      | Docker Container build.                        |
| `task core:clean`      | `task c:clean`      | leaning Compiled, Cache and Log Files.         |
| `task dev_setup`       |                     | Worker local setup.                            |
| `task core:exec`       | `task c:exec`       | Execute docker containers.                     |
| `task core:new_branch` | `task c:new_branch` | Creates new branch and pull staging changes.   |
| `task core:rebuild`    | `task c:rebuild`    | Docker Container Rebuild.                      |
| `task core:up`         | `task c:up`         | Docker Container up.                           |
| `task core:log`        | `task c:log`        | Prints docker container logs                   |
| `task cmd`             | `task c:cmd`        | Prints all useful commands                     |
| `task core:psql`       | `task c:psql`       | Access the PostgreSQL database                 |

> **_NOTE:_** Sometimes cache file created might require sudo access to be removed in which case you can prefix the below command with `sudo`

---

Tags: `#extractor`, `#legal-beagles`, `#core-package`, `#worker`