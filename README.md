# ipfix-viewer

Simple viewer(s) for IPFIX file records 
(supports: Bidirectional Record, ...)

Roadmap:
- Decode the IPFIX sub-template-multilist structured data
- Decode values to human friendly values, Example:
    - sslCipherList **4866** -> **TLS_AES_256_GCM_SHA384** chipeer suite
    - ReverseUnionTCPFlags **24** -> (000011000) **ACK, PSH** (server host of the flow)
    - ReverseInitialTCPFlags **18** -> (000010010) **SYN, ACK** (server host of the flow)
- Qt Widget Interface:
    - Implement the model *"setup"* in TreeModel(QAbstractItemModel) class

## Mediocre CLI decoder
![](/docs/cli-decoder.png)  
* DPI info-elements (HTTPS/TLS in above example)
___

## Qt Widget Interface
![](/docs/Qt-widgets.png)
* DPI info-elements (HTTP in above example)
___

## Qt Quick (QML / JavaScript) Interface

___

## Java FX Interface
___

## Kotlin mobile Interface
___