from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.carrier.asyncore.dgram import udp
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from time import time


class Snmp:
    """Conexão com a impressora via SNMP"""
    def __init__(self, ip_adress: str, mib_cod: str):
        self.ip_adress = ip_adress
        self.mib_cod = mib_cod
        self.cod_alert = None

    def snmp_connection(self):
        # Protocol version to use
        pMod = api.protoModules[api.protoVersion1]

        # Build PDU
        reqPDU = pMod.GetRequestPDU()
        pMod.apiPDU.setDefaults(reqPDU)
        pMod.apiPDU.setVarBinds(
            reqPDU, (('1.3.6.1.2.1.43.5.1.1.17.1', pMod.Null('')),
                     (self.mib_cod, pMod.Null('')))
        )
        # 1.3.6.1.2.1.43.5.1.1.17.1 - Número de série
        # 1.3.6.1.2.1.43.18.1.1.7.1.1 - Alerta

        # Build message
        reqMsg = pMod.Message()
        pMod.apiMessage.setDefaults(reqMsg)
        pMod.apiMessage.setCommunity(reqMsg, 'public')
        pMod.apiMessage.setPDU(reqMsg, reqPDU)

        startedAt = time()

        # Teste timeout conexão
        def cbTimerFun(timeNow):
            if timeNow - startedAt > 3:
                raise Exception("Request timed out")

        # noinspection PyUnusedLocal,PyUnusedLocal
        def cbRecvFun(transportDispatcher, transportDomain, transportAddress,
                      wholeMsg, reqPDU=reqPDU):
            while wholeMsg:
                rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
                rspPDU = pMod.apiMessage.getPDU(rspMsg)

                # Match response to request
                if pMod.apiPDU.getRequestID(reqPDU) == pMod.apiPDU.getRequestID(rspPDU):
                    # Check for SNMP errors reported
                    errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
                    if errorStatus:
                        print(errorStatus.prettyPrint())

                    else:
                        for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
                            self.cod_alert = val.prettyPrint()

                    transportDispatcher.jobFinished(1)

            return wholeMsg


        transportDispatcher = AsyncoreDispatcher()

        transportDispatcher.registerRecvCbFun(cbRecvFun)
        transportDispatcher.registerTimerCbFun(cbTimerFun)

        # UDP/IPv4
        transportDispatcher.registerTransport(
            udp.domainName, udp.UdpSocketTransport().openClientMode()
        )

        # Pass message to dispatcher
        transportDispatcher.sendMessage(
            encoder.encode(reqMsg), udp.domainName, (self.ip_adress, 161)
        )
        transportDispatcher.jobStarted(1)

        transportDispatcher.runDispatcher()

        transportDispatcher.closeDispatcher()
