# IPFIXanalysis

Roadmap:
- Decode the IPFIX sub-template-multilist structured data
- Decode values to human friendly values, Example:
    - sslCipherList **4866** -> **TLS_AES_256_GCM_SHA384** chipeer suite
    - ReverseUnionTCPFlags **24** -> (000011000) **ACK, PSH** (server host of the flow)
    - ReverseInitialTCPFlags **18** -> (000010010) **SYN, ACK** (server host of the flow)
- Qt Widget Interface:
    - Combined analysis IPFIX and PCAP: Data-series 
    - charts and graphs from analysis results

___

## Qt Widget Interface

**DPI info-elements (HTTP):**
![](/docs/HTTP.png)

**DPI info-elements (HTTPS/TLS):**
![](/docs/HTTPS-TLS.png)

**DPI info-elements (DNS):**
![](/docs/DNS.png)

___

## Qt Quick (QML / JavaScript) Interface

___

## Java FX Interface
___

## Kotlin mobile Interface
___