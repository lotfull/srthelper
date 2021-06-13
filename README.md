# SRT Helper

## Ping
    ping (-d=DO) (-t=1) (-o=ping.json)

test ping using https://github.com/jakejarvis/provider-speed-tests:

    -d --provider = to selected provider in list (DO, AWS, ALL)
    -t --tries = number of ping tests
    -o --output = output filename, default ping.json

example result json: 

    {"DO-NYC1": 134.531, "DO-NYC2": 132.959, "DO-NYC3": 133.545}

## Bestdc
    bestdc (ping1.json, ...) (-o=bestping.json)

calculate and return best ping provider from provided ping json files

    -o --output = output filename, default bestdc.json

example result: 

    DO-NYC1


## Config
    config (-b=1000) (--mss=1360) (--payload=1316) (--latency=500) (ping1.json, ...) (-o=bestping.json) (--proxy_rcv_port=1234) (--proxy_snd_port=1235)

Create srt config for sender, receiver and proxy

    -b --bitrate = bitrate of video, default 1000
    --mss = mss, default 1360
    --payload = payload, default 1316
    --latency = latency, default 500

    -d --provider = proxy server provider to get instance, required if proxy_ip not set
    --proxy_ip = proxy server ip, required if provider not set

    --proxy_rcv_ip = proxy server receive ip, optional
    --proxy_rcv_port = proxy server receive port, default 1234
    --proxy_snd_ip = proxy server send ip, optional
    --proxy_snd_port = proxy server send port, default 1235
    --proxy_name = proxy server docker container name, default proxy_{proxy_rcv}_{proxy_snd}

    -o --output = output filename, default config.json

example result json: 

    {
        "sender": "srt://X.X.X.X:1234?transtype=live&rcvlatency=50&peerlatency=50&fc=104&rcvbuf=1006600&sndbuf=1006600&payloadsize=1316&mss=1360",
        "receiver": "srt://X.X.X.X:1235&transtype=live&rcvlatency=50&peerlatency=50&fc=104&rcvbuf=1006600&sndbuf=1006600&payloadsize=1316&mss=1360",
        "proxy_ip": "X.X.X.X",
        "proxy_rcv": "X.X.X.X:1234",
        "proxy_snd": "X.X.X.X:1235",
        "proxy_config": "srt-live-transmit srt://:1234 srt://:1235"
        "proxy_config_script": "docker run -d --name=srtlivetransmit --net=host --restart=unless-stopped fenestron/srt:latest srt-live-transmit srt://:1234 srt://:1235"
    }

