from google.appengine.ext import ndb
import logging
import meraki_models

def get_meraki_organisations(apiKey=None):
    if not apiKey:
        logging.debug("no apiKey passed")
        return None
    key = ndb.Key('MerakiOrganisation', apiKey)
    organisations = key.get()
    if not organisations:
        organisations = meraki_models.MerakiOrganisation(id=apiKey)
    return organisations


def get_meraki_network(networkId=None):
    if not networkId:
        logging.debug("no networkId passed")
        return None
    key = ndb.Key('MerakiNetwork', networkId)
    network = key.get()
    if not network:
        network= meraki_models.MerakiNetwork(id=networkId)
    return network

def get_meraki_network_list(orgId=None):
    if not orgId:
        logging.debug("no orgId passed")
        raise Exception('MissingOrgId')
    key = ndb.Key('MerakiNetworkList', orgId)
    networklist = key.get()
    if not networklist:
        logging.debug("network list not found in datastore, returning empty model")
        networklist= meraki_models.MerakiNetworkList(id=orgId)
    return networklist

def get_meraki_device(serial=None):
    if not serial:
        logging.debug("no serial passed")
        return None
    key = ndb.Key('MerakiDevice', serial)
    device = key.get()
    if not device:
        device= meraki_models.MerakiDevice(id=serial)
    return device

def get_meraki_device_list(networkId=None):
    if not networkId:
        logging.debug("no networkId passed")
        return None
    key = ndb.Key('MerakiDeviceList', networkId)
    deviceList = key.get()
    if not deviceList:
        deviceList= meraki_models.MerakiDeviceList(id=networkId)
    return deviceList


def get_meraki_client(client_id=None):
    if not client_id:
        logging.debug("no client_id passed")
        return None
    key = ndb.Key('MerakiClient', client_id)
    client = key.get()
    if not client:
        client = meraki_models.MerakiClient(id=client_id)
    return client


def get_meraki_client_list(deviceId=None):
    if not deviceId:
        logging.debug("no deviceId passed")
        return None
    key = ndb.Key('MerakiClientList', deviceId)
    clientList = key.get()
    if not clientList:
        clientList = meraki_models.MerakiClientList(id=deviceId)
    return clientList