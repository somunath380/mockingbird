from typing import Dict, List, Text
from common.builder import URLBuilder
from connections import aiohttp_request
from common.exceptions import CustomGlobalException
from common.logger import LoggerHelper
from constants.common_constants import KAFKA_INTEGRATION_TOPIC_MAPPING
from integrations.ajio_vms.ajio_vms_constants import AJIO_VMS_INTEGRATION, AJIO_VMS_INVENTORY_AUTH_TOKEN, AJIO_VMS_INVENTORY_DOMAIN, AJIO_VMS_STATUS
from integrations.ajio_vms.crons.cron_helper import create_headers_url_payload, fetch_integration_details
from integrations.ajio_vms.crons.cron_helper import get_all_orders_from_paginated_response_ajio
from constants.common_constants import STATUS_CODE_200
from prometheus.helper import cron_failed_error, cron_successful
import asyncio

from kafka_utils.producer.producer import emit_data_on_topic # for running on x1

from kafka.producer.producer import emit_data_on_topic  # for running on prod

fl_obj = LoggerHelper()
fl_obj.set_base_logging_json(
    {
        "affiliate_id": None,
        "affiliate_bag_id": None,
        "state": None,
        "shipment_id": None,
    }
)
 

async def get_paginated_stores_list_response_of_given_store(store_id = None):
    headers: Dict = {"Authorization": AJIO_VMS_INVENTORY_AUTH_TOKEN}
    url_filters: Dict = {
        "integration_filter": {"integration_name": AJIO_VMS_INTEGRATION},
        "domain_filter": {"domain_name": AJIO_VMS_INVENTORY_DOMAIN},
        "url_filter": {"url_name": "inventory-extention-stores-list"}
    }
    url_payload: Dict = URLBuilder.fetch_url(**url_filters)
    url: Text = url_payload["url"]
    data: Dict = {"limit": 100}
    current_page: Text = 1
    all_stores_list: List = []
    # calling get list of stores api for all the pages till next_page is available
    while current_page:
        data["page"]: Text = current_page
        resp: Dict = await aiohttp_request(
            request_type="GET", url=url,
            headers=headers, data=data)
        print('RESPONSE :', resp, '\n')
        error_msg: Text = str(resp.get("error_message", ""))
        print('ERROR MESSAGE : ', error_msg, '\n')
        # if we are not able to get stores list then no use of going further
        # so raised exception for if any error occured
        if resp["status_code"] != STATUS_CODE_200:
            raise CustomGlobalException(
                error_msg,
                resp["status_code"],
                error_data={"error_message": error_msg}
            )
        for store in resp["json"]["data"]:
            all_stores_list.append(store)
        # if we have next page then continue or else break
        if resp["json"]["page"]["has_next"]:
            current_page = current_page + 1
        else:
            break
    # set store details in cache
    new_list = [i for i in all_stores_list if i.get("store_id") == store_id]
    print(new_list)
    return new_list



import requests
url = 'https://ajio.extensions.fyndx1.de/extension/stores'
headers = {'Authorization' : 'Basic YWppbzphamlvI2Z5bmQ='}
rsp = requests.get(url, headers=headers)
print(rsp.status_code)
print(rsp.json()[])





async def get_paginated_stores_list_response() -> Dict:  #run this
    headers: Dict = {"Authorization": AJIO_VMS_INVENTORY_AUTH_TOKEN}
    url_filters: Dict = {
        "integration_filter": {"integration_name": AJIO_VMS_INTEGRATION},
        "domain_filter": {"domain_name": AJIO_VMS_INVENTORY_DOMAIN},
        "url_filter": {"url_name": "inventory-extention-stores-list"}
    }

    url_payload: Dict = URLBuilder.fetch_url(**url_filters)
    url: Text = url_payload["url"]
    print('URL PAYLOAD : ', url_payload)
    data: Dict = {"limit": 100}
    current_page: Text = 1
    all_stores_list: List = []

    # calling get list of stores api for all the pages till next_page is available
    while current_page:
        data["page"]: Text = current_page

        resp: Dict = await aiohttp_request(
            request_type="GET", url=url,
            headers=headers, data=data)

        error_msg: Text = str(resp.get("error_message", ""))
        # if we are not able to get stores list then no use of going further
        # so raised exception for if any error occured
        if resp["status_code"] != STATUS_CODE_200:
            raise CustomGlobalException(
                error_msg,
                resp["status_code"],
                error_data={"error_message": error_msg}
            )

        for store in resp["json"]["data"]:
            all_stores_list.append(store)
        # if we have next page then continue or else break
        if resp["json"]["page"]["has_next"]:
            current_page = current_page + 1
        else:
            break
    return all_stores_list


async def ajio_vms_get_orders_pendency(fl_obj, mode='view', *args, **kwargs):
    """Cron for polling orders which are in Open status and whose acknowledgment is not yet received."""
    fl_obj: LoggerHelper = fl_obj  # injected by fyndlogger_dec
    fl_obj.log_action("ajio_vms_get_orders_pendency", **{
        "hog_module_msg": "Inside ajio_vms_get_orders_pendency"})

    store_list_resp: List = await get_paginated_stores_list_response_of_given_store(11665)

    if mode=='emit':
        data_to_be_emited: Dict = {
            "integration_details": await fetch_integration_details(fl_obj),
            "state": "order_create"
        }
        topics = set()
        topics.add(KAFKA_INTEGRATION_TOPIC_MAPPING["ajio_vms"]["topics"][0])

    # get orders of all the stores using their auth token (without PO orders)
    for store_details in store_list_resp:
        store_id: Text = store_details["store_id"]
        try:
            headers, url, payload_data = await create_headers_url_payload(
                store_details, "get-orders-pendency-ajio", fl_obj)
            print('\n HEADERS -> {headers} URL -> {url} PAYLOAD -> {payload_data} \n'.format(headers=headers, url=url, payload_data=payload_data))
            store_orders_resp: Dict = await get_all_orders_from_paginated_response_ajio(
                headers, url, payload_data, "ajio_vms_get_orders_pendency", fl_obj)
            print('RESPONSE FROM STORE -> ', store_orders_resp, '\n')
        except Exception:
            continue
        if mode=='emit':
            if store_orders_resp["all_orders"]:
                data_to_be_emited["store_orders_details"]: Dict = store_orders_resp
                # emit all orders details to kafka
                emit_data_on_topic(topics=topics, partition_value=store_id, data_to_be_emitted=data_to_be_emited)
            cron_successful(integration_name="ajio_vms", cron_name="ajio_vms_get_orders_pendency")

asyncio.run(ajio_vms_get_orders_pendency(fl_obj, mode='view'))


async def ajio_vms_get_return_created_orders(*args, **kwargs):
    """Cron for polling return orders from each stores.

    First we are fetching list of all stores with their Authentication tokens.
    Then we are fetching list of all return orders for each and every stores.
    These orders will have status RETURN_CREATED.
    """
    fl_obj: LoggerHelper = kwargs["fl_obj"]  # injected by fyndlogger_dec
    fl_obj.log_action("ajio_vms_get_return_created_orders", **{
        "hog_module_msg": "Inside ajio_vms_get_return_created_orders"})
    try:
        # call inventory api to get list of all the stores with their Authentication tokens
        store_list_resp: List = await get_list_of_stores_cache(fl_obj, "ajio_stores_list")
        if not store_list_resp:
            store_list_resp: List = await get_paginated_stores_list_response(fl_obj)

        data_to_be_emited: Dict = {
            "integration_details": await fetch_integration_details(fl_obj)}

        topics = set()
        topics.add(KAFKA_INTEGRATION_TOPIC_MAPPING["ajio_vms_return"]["topics"][0])

        # get orders of all the stores using their auth token
        for store_details in store_list_resp:
            store_id: Text = store_details["store_id"]
            try:
                headers, url, payload_data = await create_headers_url_payload(
                    store_details, "get-return-orders-ajio", fl_obj)
                payload_data["filter_type"] = "returnOrderStatus"
                payload_data["filter_value"] = AJIO_VMS_STATUS["return_created"]

                store_orders_resp: Dict = await get_all_orders_from_paginated_response_ajio(
                    headers, url, payload_data, "ajio_vms_get_return_created_orders", fl_obj)
            except Exception:
                continue

            if store_orders_resp:
                data_to_be_emited["store_orders_details"] = store_orders_resp
                # emit all orders details to kafka
                emit_data_on_topic(topics=topics, partition_value=store_id, data_to_be_emitted=data_to_be_emited)
        cron_successful(integration_name="ajio_vms", cron_name="ajio_vms_get_return_created_orders")
    except BendingException:
        fl_obj.raw_fl_obj.warning(get_exception_text())
        cron_failed_error(integration_name="ajio_vms", cron_name="ajio_vms_get_return_created_orders")
        raise BendingException(
            "BendingException | {}-{}-Exception:{}".format(
                "Ajio VMS", "ajio_vms_get_return_created_orders", get_exception_text()))

    except Exception:
        fl_obj.raw_fl_obj.warning(get_exception_text())
        cron_failed_error(integration_name="ajio_vms", cron_name="ajio_vms_get_return_created_orders")
        raise Exception(
            "Http Request Failed | {}-{}".format(
                "Ajio VMS", "ajio_vms_get_return_created_orders"))




#####################





async def ajio_vms_get_orders_pendency(store_details, *args, **kwargs):
    fl_obj = LoggerHelper()
    fl_obj.set_base_logging_json(
        {
            "affiliate_id": None,
            "affiliate_bag_id": None,
            "state": None,
            "shipment_id": None,
        }
    )
    store_list_resp: List = store_details
    # get orders of all the stores using their auth token (without PO orders)
    for store_details in store_list_resp:
        store_id: Text = store_details["store_id"]
        try:
            headers, url, payload_data = await create_headers_url_payload(
                store_details, "get-orders-pendency-ajio", fl_obj)
            store_orders_resp: Dict = await get_all_orders_from_paginated_response_ajio(
                headers, url, payload_data, "ajio_vms_get_orders_pendency", fl_obj)
            print(f"\n STORE ORDER RESPONSE : {store_orders_resp}\n")
        except Exception:
            continue



asyncio.run(ajio_vms_get_orders_pendency(store_details))



async def ajio_vms_get_confirmed_orders(*args, **kwargs):
    fl_obj: LoggerHelper = kwargs["fl_obj"]  # injected by fyndlogger_dec
    fl_obj.log_action("ajio_vms_get_confirmed_orders", **{
        "hog_module_msg": "Inside ajio_vms_get_confirmed_orders"})
    try:
        # call inventory api to get list of all the stores with their Authentication tokens
        store_list_resp: List = await get_list_of_stores_cache(fl_obj, "ajio_stores_list")
        if not store_list_resp:
            store_list_resp: List = await get_paginated_stores_list_response(fl_obj)

        data_to_be_emited: Dict = {
            "integration_details": await fetch_integration_details(fl_obj)}

        topics = set()
        topics.add(KAFKA_INTEGRATION_TOPIC_MAPPING["ajio_vms_po"]["topics"][0])

        # get orders of all the stores using their auth token (with PO details)
        for store_details in store_list_resp:
            store_id: Text = store_details["store_id"]
            try:
                headers, url, payload_data = await create_headers_url_payload(
                    store_details, "get-orders-po-ajio", fl_obj)
                payload_data["filter_type"] = "orderStatus"
                payload_data["filter_value"] = AJIO_VMS_STATUS["confirmed"]
                store_orders_resp: Dict = await get_all_orders_from_paginated_response_ajio(
                    headers, url, payload_data, "ajio_vms_get_confirmed_orders", fl_obj)
            except Exception:
                continue

            if store_orders_resp:
                data_to_be_emited["store_orders_details"] = store_orders_resp
                # emit all orders details to kafka
                emit_data_on_topic(topics=topics, partition_value=store_id, data_to_be_emitted=data_to_be_emited)
        cron_successful(integration_name="ajio_vms", cron_name="ajio_vms_get_confirmed_orders")
    except BendingException:
        fl_obj.raw_fl_obj.warning(get_exception_text())
        cron_failed_error(integration_name="ajio_vms", cron_name="ajio_vms_get_confirmed_orders")
        raise BendingException(
            "BendingException | {}-{}-Exception:{}".format(
                "Ajio VMS", "ajio_vms_get_confirmed_orders", get_exception_text()))

    except Exception:
        fl_obj.raw_fl_obj.warning(get_exception_text())
        cron_failed_error(integration_name="ajio_vms", cron_name="ajio_vms_get_confirmed_orders")
        raise Exception(
            "Http Request Failed | {}-{}".format(
                "Ajio VMS", "ajio_vms_get_confirmed_orders"))






from integrations.ajio_vms.crons.cron_helper import return_kafka_lag

async def ajio_vms_get_confirmed_orders(*args, **kwargs):
    fl_obj: LoggerHelper =  LoggerHelper() # injected by fyndlogger_dec
    fl_obj.log_action("ajio_vms_get_confirmed_orders", **{
        "hog_module_msg": "Inside ajio_vms_get_confirmed_orders"})
    kafka_lag = await return_kafka_lag("ajio_vms_po")
    if kafka_lag is False:
        raise CustomGlobalException("Kafka lag more than threshold value", 6006)
    try:
        # call inventory api to get list of all the stores with their Authentication tokens
        store_list_resp: List = await get_list_of_stores_cache(fl_obj, "ajio_stores_list")
        if not store_list_resp:
            store_list_resp: List = await get_paginated_stores_list_response(fl_obj)

        data_to_be_emited: Dict = {
            "integration_details": await fetch_integration_details(fl_obj)}

        topics = set()
        topics.add(KAFKA_INTEGRATION_TOPIC_MAPPING["ajio_vms_po"]["topics"][0])

        # get orders of all the stores using their auth token (with PO details)
        for store_details in store_list_resp:
            store_id: Text = store_details["store_id"]
            try:
                headers, url, payload_data = await create_headers_url_payload(
                    store_details, "get-orders-po-ajio", fl_obj)
                payload_data["filter_type"] = "orderStatus"
                payload_data["filter_value"] = AJIO_VMS_STATUS["confirmed"]
                store_orders_resp: Dict = await get_all_orders_from_paginated_response_ajio(
                    headers, url, payload_data, "ajio_vms_get_confirmed_orders", fl_obj)
            except Exception:
                continue

            if store_orders_resp:
                data_to_be_emited["store_orders_details"] = store_orders_resp
                # emit all orders details to kafka
                emit_data_on_topic(topics=topics, partition_value=store_id, data_to_be_emitted=data_to_be_emited)
        cron_successful(integration_name="ajio_vms", cron_name="ajio_vms_get_confirmed_orders")
    except BendingException:
        fl_obj.raw_fl_obj.warning(get_exception_text())
        cron_failed_error(integration_name="ajio_vms", cron_name="ajio_vms_get_confirmed_orders")
        raise BendingException(
            "BendingException | {}-{}-Exception:{}".format(
                "Ajio VMS", "ajio_vms_get_confirmed_orders", get_exception_text()))

    except Exception:
        fl_obj.raw_fl_obj.warning(get_exception_text())
        cron_failed_error(integration_name="ajio_vms", cron_name="ajio_vms_get_confirmed_orders")
        raise Exception(
            "Http Request Failed | {}-{}".format(
                "Ajio VMS", "ajio_vms_get_confirmed_orders"))
