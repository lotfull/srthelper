# SRT Helper

## Ping
    ping (-d=DO) (-t=1) (-o=ping.json)

test ping using https://github.com/jakejarvis/provider-speed-tests:

    -d --provider = to selected provider in list (DO, AWS, ALL)
    -t --tries = number of ping tests
    -o --output = output filename, default ping.json

example result json: 

    {"DO-NYC1": 134.531, "DO-NYC2": 132.959, "DO-NYC3": 133.545}

## Bestping
    bestping (ping1.json, ...) (-o=bestping.json)

calculate and return best ping provider from provided ping json files

    -o --output = output filename, default bestping.json

example result: 

    {'region': 'fra1', 'provider': 'DO', 'host': 'speedtest-fra1.digitalocean.com', 'ping': 112.962}


## Config
    config direct/forwarder (-b=1000) (--mss=1360) (--payload=1316) (--latency=500) \
    (--provider=DO) (--region=fra1) (--forwarder_rcv_port=1234) (--forwarder_snd_port=1235) (-o=config.json)

Create direct/forwarder srt config for sender, receiver, and optional forwarder

    mode = direct/forwarder
    -b --bitrate = bitrate of video, default 1000
    --mss = mss, default 1360
    --payload = payload, default 1316
    --latency = latency, default 500

    --provider = forwarder server provider to get instance, required if ip not set
    --region = forwarder server provider to get instance, required if ip not set
    --ip = forwarder server ip, required if provider not set
    --user = forwarder server user, default=root

    --rcv_ip = forwarder server receive ip, optional
    --rcv_port = forwarder server receive port, default 1234
    --snd_ip = forwarder server send ip, optional
    --snd_port = forwarder server send port, default 1235
    --name = forwarder server docker container name, default forwarder_{rcv}_{snd}

    -o --output = output filename, default config.json

example result json: 

    {
        "sender": "srt://X.X.X.X:1234?transtype=live&rcvlatency=50&peerlatency=50&fc=104&rcvbuf=1006600&sndbuf=1006600&payloadsize=1316&mss=1360",
        "receiver": "srt://X.X.X.X:1235&transtype=live&rcvlatency=50&peerlatency=50&fc=104&rcvbuf=1006600&sndbuf=1006600&payloadsize=1316&mss=1360",
        "forwarder_ip": "X.X.X.X",
        "forwarder_rcv": "X.X.X.X:1234",
        "forwarder_snd": "X.X.X.X:1235",
        "forwarder_config": "srt-live-transmit srt://:1234 srt://:1235"
        "forwarder_config_script": "docker run -d --name=srtlivetransmit --net=host --restart=unless-stopped fenestron/srt:latest srt-live-transmit srt://:1234 srt://:1235"
    }

example direct request

    srthelper config direct -b 1000000 --rtt 300 --latency 1000 --ip=136.243.3.102 --src_ip=204.48.27.153

example srt config response

    srt://204.48.27.153:1234?transtype=live&rcvlatency=1000&peerlatency=1000&mss=1360&payloadsize=1316&fc=109&rcvbuf=145188&sndbuf=145188
