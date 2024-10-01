# wigreen_prpl_app
Orchestrator for prpl app

## Build the image
Clone recipe in prpl_sdk_lb6:
```bash
git clone https://github.com/Nicolas44Hernandez/wigreen_prpl_app.git
```

Run the sdk helper 
```bash
~/sdk_helper/prpl-sdk
```

Search the application recipe
```bash
user@prplSDK sdkworkdir$ devtool search wigreen
NOTE: Starting bitbake server...
NOTE: Reconnecting to bitbake server...
NOTE: Retrying server connection (#1)...
WARNING: You have included the meta-virtualization layer, but 'virtualization' has not been enabled in your DISTRO_FEATURES. Some bbappend files may not take effect. See the meta-virtualization README for details on enabling virtualization support.
Loading cache: 100% |########################################################################################################################################################################| Time: 0:00:02
Loaded 5257 entries from dependency cache.
Parsing recipes: 100% |######################################################################################################################################################################| Time: 0:00:01
Parsing of 3881 .bb files complete (3878 cached, 3 parsed). 5258 targets, 384 skipped, 0 masked, 0 errors.

Summary: There was 1 WARNING message shown.
wigreen 
user@prplSDK sdkworkdir$
```

Add the python3-amx recipe
```bash
user@prplSDK sdkworkdir$ devtool modify python-amx
``` 

Add the recipe
```bash
user@prplSDK sdkworkdir$ devool modify wigreen
``` 

Build the project 
```bash
user@prplSDK sdkworkdir$ devool build wigreen
``` 

Build image 
```bash
user@prplSDK sdkworkdir$ devool build wigreen
``` 

## Publish the image

Publish image to registry
```bash
user@prplSDK sdkworkdir$ skopeo copy oci:/sdkworkdir/tmp/deploy/images/container-cortexa53/image-lcm-container-minimal-container-cortexa53.rootfs-oci docker://<REGISTRY>/orchestrator --dest-creds=<USER>:<PASSORD>

``` 

## Install the image
Connect to Prpl device

```bash
ubus-cli "SoftwareModules.InstallDU(URL = 'docker://<REGISTRY>/orchestrator', Username = <USER> , Password = <PASSWORD>, ExecutionEnvRef = 'generic', UUID = 'aade1eee-8ee1-5690-887f-b41aab7ca15e')"

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


# TODO:
- [ ] Add prpl expertice center links to docs