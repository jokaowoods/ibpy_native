from ibapi.wrapper import EWrapper
from .finishable_queue import FinishableQueue, Status as QStatus

import queue

class IBWrapper(EWrapper):
    """
    The wrapper deals with the action coming back from the IB gateway or 
    TWS instance
    """

    __contract_details_queue = {}

    def __init__(self):
        self.__err_queue = queue.Queue()

        super().__init__()

    # Error handling
    def has_err(self):
        return not self.__err_queue.empty()
 
    def get_err(self, timeout=10):
        if self.has_err():
            try:
                return self.__err_queue.get(timeout=timeout)
            except queue.Empty:
                return None

        return None
       
    def error(self, id, errorCode, errorString):
        # override method
        error_msg = "IB error id %d errorcode %d string %s" \
            % (id, errorCode, errorString)

        self.__err_queue.put(error_msg)

    # Get contract details
    def init_contract_details_queue(self, reqId):
        self.__contract_details_queue[reqId] = queue.Queue()

        return self.__contract_details_queue[reqId]

    def contractDetails(self, reqId, contractDetails):
        # override method
        if reqId not in self.__contract_details_queue.keys():
            self.init_contract_details_queue(reqId)

        self.__contract_details_queue[reqId].put(contractDetails)

    def contractDetailsEnd(self, reqId):
        # override method
        if reqId not in self.__contract_details_queue.keys():
            self.init_contract_details_queue(reqId)

        self.__contract_details_queue[reqId].put(QStatus.FINISHED)
