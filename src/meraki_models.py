from google.appengine.ext import ndb


_NETWORK_TYPES = ['wireless','wired']




class MerakiNetworkList(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now=True)
    networkIdList = ndb.StringProperty(repeated=True)
    networkNameList = ndb.StringProperty(repeated=True)
    networkList = ndb.JsonProperty(repeated=True)


class MerakiDeviceList(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now=True)
    deviceSerialList = ndb.StringProperty(repeated=True)
    deviceList = ndb.JsonProperty(repeated=True)

class MerakiClientList(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now=True)
    clientList = ndb.StringProperty(repeated=True)


class MerakiOrganisation(ndb.Model):
    orgId = ndb.StringProperty(default="")
    timestamp = ndb.DateTimeProperty(auto_now=True)


class MerakiNetwork(ndb.Model):
    orgId = ndb.StringProperty(default="")
    networkId = ndb.StringProperty(default="")
    type = ndb.StringProperty(default="")
    name = ndb.StringProperty(default="")
    timeZone = ndb.StringProperty(default="")
    tags = ndb.StringProperty(default="")
    timestamp = ndb.DateTimeProperty(auto_now=True)


class MerakiDevice(ndb.Model):
    name = ndb.StringProperty(default="")
    serial = ndb.StringProperty(default="")
    mac = ndb.StringProperty(default="")
    model = ndb.StringProperty(default="")
    lanIp = ndb.StringProperty(default="")
    networkId = ndb.StringProperty(default="")
    networkName = ndb.StringProperty(default="")


class MerakiClient(ndb.Model):
    description = ndb.StringProperty(default="")
    mdnsName = ndb.StringProperty(default="")
    dhcpHostname = ndb.StringProperty(default="")
    mac = ndb.StringProperty(default="")
    ip = ndb.StringProperty(default="")
    client_id = ndb.StringProperty(default="")
    switchport = ndb.StringProperty(default="")
    usage_sent = ndb.StringProperty(default="")
    usage_recv = ndb.StringProperty(default="")
    networkName = ndb.StringProperty(default="")
    networkId = ndb.StringProperty(default="")
    timestamp = ndb.DateTimeProperty(auto_now=True)