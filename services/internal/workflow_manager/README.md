# How to set up a local environment and tests

1. Make sure, you started the infra via Docker Compose 
2. Install [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
3. Prepare test-job Docker image
```shell
./test/resources/prepare-job.sh/ps1
```
4. Install the projects in editable mode
```shell
python devcli.py --config-path ..\.config\dev\projects.json install python [version]
```
(as of 07/2024 only python projects are in the repo)
5. Test/Run the project
```shell
python -m pytest ./test
```