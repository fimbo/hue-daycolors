# hue-daycolors
polls the hue-bridge and checks if the state meets the configured state for the time of the day

## Preliminaries to run Script
1. install python 2.7 [Python BeginnersGuide](https://wiki.python.org/moin/BeginnersGuide/Download)
2. run `pip install beautifulhue enum`
3. adapt the config **config/config.json** to your needs 
4. run the script `./run.sh`

alternatively run the docker-image [fimbo/hue-daycolors](https://hub.docker.com/r/fimbo/hue-daycolors/) with everything preinstalled.

## Run Container
either run `./docker-run.sh`
or
`docker run -it -v $(pwd)/config:/hue-daycolors/config hue-daycolors:latest`

## Configuration

- enter the ip address of your hue bridge in the field **host**
- enter a generated user id in the field **user** (*automatic userid generation follows*)
- define your profiles
- define the timespans for your rooms with the active profile

### Example
```json
    "host": "192.168.10.4",
    "user": "JMfz4SkDIvUBgCzaLcsIKSeoWVoNouTI-jSityAe",
    "profiles":
    {
        "read":
        {
            "ct": 343,
            "bri": 254
        },
        "energize":
        {
            "ct": 343
        },
        "watchTV":
        {
            "ct": 343
        }
    },
    "rooms": [
    {
        "name": "Home",
        "default-profile": "read",
        "spans": [
        {
            "from": "06:00",
            "to": "10:00",
            "profile": "energize"
        },
        {
            "from": "18:00",
            "to": "23:59",
            "profile": "sleep"
        }]
    },
    {
        "name": "Living room",
        "default-profile": "read",
        "spans": [
        {
            "from": "18:00",
            "to": "23:59",
            "profile": "watchTV"
        }]
    },
    {
        "name": "Office",
        "default-profile": "energize",
        "spans": [
        {
            "from": "18:00",
            "to": "23:59",
            "profile": "read"
        }]
    }]
}
