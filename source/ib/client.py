from ibapi.contract import Contract
from ibapi.client import EClient
from ib.wrapper import IBWrapper

import ib.finishable_queue as fq

MAX_WAIT_SECONDS = 10

class IBClient(EClient):
    """
    The client calls the native methods from IBWrapper instead of 
    overriding native methods
    """
    def __init__(self, wrapper: IBWrapper):
        self.__wrapper = wrapper
        super().__init__(self, wrapper)

    def resolve_contract(self, contract: Contract, req_id: int):
        """
        From a partially formed contract, returns a fully fledged version
        :returns fully resolved IB contract
        """

        # Make place to store the data that will be returned
        contract_details_queue = fq.FinishableQueue(
            self.__wrapper.init_contract_details_queue(req_id)
        )

        print("Getting full contract details from IB...")

        self.reqContractDetails(req_id, contract)

        # Run until we get a valid contract(s) or timeout
        new_contract_details = contract_details_queue.get(
            timeout=MAX_WAIT_SECONDS
        )

        while self.__wrapper.has_err():
            print(self.__wrapper.get_err())

        if contract_details_queue.get_status() == fq.TIMEOUT:
            print("Exceed maximum wait for wrapper to confirm finished")

        if len(new_contract_details) == 0:
            print("Failed to get additional contract details: \
                returning unresolved contract")
            
            return contract

        if len(new_contract_details) > 1:
            print("Multiple contracts found: returning 1st contract")

        resolved_contract = new_contract_details[0].contract

        return resolved_contract
