# Runtime-docker-build

> Info: Instructions below are for setting up the environment *from scratch* in a CI/CD pipeline. If you only want to build and test the Docker image, go to [Build and push Docker image](#build-and-push-docker-image).

#### Table of content

- [Prerequisites](#prerequisites)
- [Build and push Docker image](#build-and-push-docker-image)
- [Run the container](#run-the-container)
- [Other Dockerfiles](#other-dockerfiles)
- [Known issues](#known-issues)

## Prerequisites 

### Install Rust and build Kuksa Databroker artifacts

Guide for installing Rust is [here](https://www.rust-lang.org/tools/install)

First, build artifacts using the `build-all-targets.sh` script. You will need to have  `cross`, `cargo-license` and `cargo-cyclonedx` dependencies installed for running this script. Upon running, it should build for both AMD64 and ARM64 by default.

```
cd runtime-docker-build
./build-all-targets.sh
```

> Note: Cross-platform building for the first time can take a while, about 10-15 minutes.

### Components inside the Docker container

- [Kuksa Databroker](https://github.com/eclipse-kuksa/kuksa-databroker/tree/0.4.4) - `0.4.4`
- [Vehicle Signal Specification](https://github.com/COVESA/vss-tools/tree/v4.0) - `4.0`
- [vehicle-model-generator](https://github.com/eclipse-velocitas/vehicle-model-generator/tree/v0.7.2) - `0.7.2`
- [Kuksa Syncer](kuksa-syncer/)
- [Kuksa Mock Provider](https://github.com/eclipse-kuksa/kuksa-mock-provider) (with modification to the source code)
- [Velocitas Python SDK](https://github.com/eclipse-velocitas/vehicle-app-python-sdk/tree/v0.14.1) - `0.14.1`
- [Kit Manager](https://github.com/nhan-orgs/Kit-Manager)
- [Python](https://www.python.org/downloads/release/python-3100/) - `3.10`

All of these has been included in the Dockerfile. If you want to understand what's going on inside, read more at [dockerfile-explained](doc/dockerfile-explained.md)

## Build and push Docker image

### Multi-architecture build

Using the BuildKit to build multi-architecture Docker image requires an output, it can be either compressed into a local tar ball or push to a container registry. For unknown reasons, the local option doesn't work so we're stuck with the `--push` option at the moment.

```shell
docker buildx create --driver docker-container --driver-opt network=host --driver-opt env.http_proxy=$https_proxy --driver-opt env.https_proxy=$https_proxy --name mybuilder --platform "linux/amd64,linux/arm64" default

docker buildx use mybuilder

docker buildx build --push --platform linux/amd64,linux/arm64 -t boschvn/sdv-runtime:latest -f Dockerfile .
```

If you're outside of Bosch's enterprise network, you can skip the `http_proxy https_proxy` driver option. Otherwise, make sure you set up your local proxy beforehand.

### Mono-architecture build

For mono-architecture image build, you can use the default BuildKit in Docker and this option also let us build locally without pushing to a remote registry.

```shell
docker buildx use default # You can use 'docker buildx ls' to check the name beforehand

docker buildx build --platform linux/amd64 -t sdv-runtime:latest -f Dockerfile .
```

## Run the container

**Default:** the Databroker will be running in insecure mode (no TLS) and the Syncer will connect to https://kit.digitalauto.tech .

```
docker run -d --name sdv-runtime boschvn/sdv-runtime:latest
```

> Tip: If you want to use kuksa-client to interact with the databroker from outside the container, you can add port forwarding in the run command like this `-p 55555:55555`.

### Parse arguments  

#### Arguments for Kit Server URL

`$SYNCER_SERVER_URL`

For now, only https://kit.digitalauto.tech works (A `localhost` option is in development).

```
docker run -d --name sdv-runtime -e SYNCER_SERVER_URL="example.com" boschvn/sdv-runtime:latest
```

#### Arguments for Kuksa databroker

`$DATABROKER_ARGS`

For all Kuksa databroker commands, see [Kuksa Databroker docs](https://github.com/eclipse-kuksa/kuksa-databroker/blob/main/doc/user_guide.md)

Below is an example of using the insecure mode:

```
docker run -d --name sdv-runtime -e DATABROKER_ARGS="--insecure" boschvn/sdv-runtime:latest
```

#### Arguments for setting runtime name

`$RUNTIME_NAME`

The name for the runtime will always follow this format: "RunTime-$RUNTIME_NAME-PID"

```
docker run -d --name sdv-runtime -e RUNTIME_NAME="CustomName" boschvn/sdv-runtime:latest
```

#### Arguments for generating vehicle model

`$KUKSA_DATABROKER_METADATA_FILE` and `$VSS_DATA`

To do: Merge the two environment variables into one for simplicity and write a quick guide of how to create a custom VSS.json file.

```
docker run -d -v /path/to/custom-vss.json:/home/dev/ws/custom-vss.json -e KUKSA_DATABROKER_METADATA_FILE=/home/dev/ws/custom-vss.json -e VSS_DATA=/home/dev/ws/custom-vss.json --name sdv-runtime boschvn/sdv-runtime:latest
```

Upon successful model generation, the logs should output something like this:

```Shell
2024-07-23T04:42:55.764302Z  INFO databroker: Populating metadata from file '/home/dev/ws/custom-vss.json'

.....

Known extended attributes: 
Loading json...
Generating tree from json...
Recursing tree and creating Python code...
All done.
Generated vehicle model from custom vss.json file at /home/dev/python-packages/vehicle
Connecting to Kit Server: https://kit.digitalauto.tech
Kuksa connected True
Connected to Kit Server 
```

#### Arguments for generating custom mock datapoints

`$MOCK_SIGNAL`

> Note: By default, if no argument for MOCK_SIGNAL is specified, the pre-defined signals in `mock/signals.json` will be used by `mock/mockprovider.py`.

```
docker run -v /path/to/custom-signals.json:/home/dev/signals.json -e MOCK_SIGNAL=/home/dev/signals.json --name sdv-runtime  boschvn/sdv-runtime:latest
```

The json file that you mount to the container should follow the same format as `mock/signals.json`, a quick preview is show below:

```
[
    {
        "signal": "Vehicle.Body.Hood.IsOpen",
        "value": "False"
    },
    {
        "signal": "Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed",
        "value": "0"
    },
    {
        "signal": "Vehicle.ADAS.CruiseControl.SpeedSet",
        "value": "0"
    }
]
```

Successful generation will have an output like this:

```
INFO:mock_service:Databroker connected!
INFO:mock_service:Datapoint added/removed
INFO:mock_service:Subscribing to 4 mocked datapoints...
INFO:mock_service:Feeding 'Vehicle.Body.Hood.IsOpen' with value False
INFO:mock_service:Feeding 'Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed' with value 0
```

## Other Dockerfiles

### Dockerfile-syncer

Only include the Velocitas Python SDK and some other necessary Python libs. Need to have Kuksa databroker and MQTT broker containers running alongside this one.

### Dockerfile-vss3

Old Dockerfile that support VSS-3.1.1, it behaves almost the same as the latest image that support VSS-4.0.

```
docker build -t sdv-runtime:v3.1.1 -f Dockerfile.vss3 .
```

## Known issues

1. Container can't connect to kit.digitalauto.tech when running inside Bosch's network (Server returns 503) => One workaround is to run the kit server inside the container and have the playground website connected to that:
    - In your browser, open the Developer Tool (`F12`), then goes to `Storage` (Firefox) or  `Application` (Edge). Select the `Local Storage` of the playground website and then add the following key-value pair: `customKitServer` - `http://localhost:3090`
    - Run the `sdv-runtime` container with the following command: 

    ```
    docker run -d --name sdv-runtime  -p 3090:3090 -e SYNCER_SERVER_URL="http://localhost:3090" boschvn/sdv-runtime:latest
    ```

    - Go back to `Dashboard` and you should be able to select the container running on your local machine.
2. Container doesn't have Internet connection whatsoever when running inside Bosch's network => Make sure you have configured a local proxy for your Docker in `~/.docker/config.json`, the IP address depends on your actual network configuration.
3. Newest version of Kuksa Databroker isn't working with VSS4.0 for unknown reasons.