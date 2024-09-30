# wigreen_prpl_app
Orchestrator for prpl app

## Installation procedure
Connect to Prpl device

```bash
ubus-cli "SoftwareModules.InstallDU(URL = 'docker://<registry>/<my_project_name>/<image_name>', Username = <USER> , Password = <PASSWORD>, ExecutionEnvRef = 'generic', UUID = 'aade1eee-8ee1-5690-887f-b41aab7ca15e')"

``` 

## Attach to container
```bash
lxc-ls --fancy
lxc-attach <DUID>
```

# UNINSTALL 
```bash
ubus-cli "SoftwareModules.DeploymentUnit.cpe-<IMAGE>.Uninstall(RetainData = "No")"
```
