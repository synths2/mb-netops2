import logging
import meraki
import meraki_models
import json

from flask import Response
from settings import API_KEY as apikey
from settings import CLIENT_TIMESPAN as timespan
from settings import BLOCK_MESSAGE as blockmsg

class Bot(object):
    def __init__(self, slack_client, user_id=None):
        self.slack_client = slack_client
        self.user_id = user_id

    def get_user_id(self):
        response = self.slack_client.auth_test()
        if not response['ok']:
            logging.error("Unable to retrieve bot id due to %s",
                          response['error'])
        else:
            user_id = response['user_id']
            logging.info("Retrieved user_id: '%s'", user_id)
            return user_id

    def handle_event(self, event):
        if event.type == 'message':
            self.__handle_message_event(event)
        else:
            logging.debug("Ignoring unknown event type {}".format(event.type))


    def handle_action(self, action):
        if action.type == 'interactive_message':
            self.__handle_message_action(action)
        else:
            logging.debug("Ignoring unknown event type {}".format(action.type))


    def __handle_message_action(self, action):
        if not self.user_id:
            self.user_id = self.get_user_id()
        if action.user_id == self.user_id:
            logging.debug("Ignoring own message")
            return

        act = unicode.split(action.action_value)

        if act[-2] == "block":
            clientresult = meraki_models.MerakiClient.query().filter(meraki_models.MerakiClient.mac == act[-1])
            result = clientresult.fetch(1)
            logging.debug(result[0])

            if result:
                tempclient = {
                    'mac': result[0].mac,
                    'ip': result[0].ip,
                    'networkName': result[0].networkName,
                    'description': result[0].description,
                    'client_id': result[0].client_id
                }
                logging.debug(tempclient)
                result = meraki.updateclientpolicy(apikey, result[0].networkId,
                                                   result[0].mac, policy='blocked')
                logging.debug(result)
                msg = "client ID {} blocked ".format(tempclient['client_id'])
                logging.debug(msg)
                self.slack_client.post_message(channel=action.channel, text=msg)
                ret = {
                    'replace_original': 'false',
                    'text': msg
                }
                return Response(json.dumps(ret), status=200, mimetype='application/json')

        if act[-2] == "unblock":
            clientresult = meraki_models.MerakiClient.query().filter(meraki_models.MerakiClient.mac == act[-1])
            result = clientresult.fetch(1)
            logging.debug(result[0])

            if result:
                tempclient = {
                    'mac': result[0].mac,
                    'ip': result[0].ip,
                    'networkName': result[0].networkName,
                    'description': result[0].description,
                    'client_id': result[0].client_id
                }
                logging.debug(tempclient)
                result = meraki.updateclientpolicy(apikey, result[0].networkId,
                                                   result[0].mac, policy='normal')
                logging.debug(result)
                msg = "client ID {} unblocked ".format(tempclient['client_id'])
                logging.debug(msg)
                self.slack_client.post_message(channel=action.channel, text=msg)
                ret = {
                    'replace_original': 'false',
                    'text': msg
                }
                return Response(json.dumps(ret), status=200, mimetype='application/json')

        if act[-2] == "de-authorize":
            clientresult = meraki_models.MerakiClient.query().filter(meraki_models.MerakiClient.mac == act[-1])
            result = clientresult.fetch(1)

            if result:
                tempclient = {
                    'mac': result[0].mac,
                    'ip': result[0].ip,
                    'networkName': result[0].networkName,
                    'description': result[0].description,
                    'client_id': result[0].client_id
                }

                #current = meraki.getclientsplash(apikey,result[0].networkId,result[0].mac)
                #logging.debug(current)

                ssid_authorization = {'ssids': {'1': {'isAuthorized': False}, '2': {'isAuthorized': False}}}
                res = meraki.updateclientsplash(apikey, result[0].networkId, result[0].mac, ssid_authorization)
                msg = "client ID {} de-authorized \n{}".format(tempclient['client_id'], res)

                logging.debug(msg)
                self.slack_client.post_message(channel=action.channel, text=msg)
                ret = {
                    'replace_original': 'false',
                    'text': msg
                }
                return Response(json.dumps(ret), status=200, mimetype='application/json')

        if act[-2] == "re-authorize":
            clientresult = meraki_models.MerakiClient.query().filter(meraki_models.MerakiClient.mac == act[-1])
            result = clientresult.fetch(1)

            if result:
                tempclient = {
                    'mac': result[0].mac,
                    'ip': result[0].ip,
                    'networkName': result[0].networkName,
                    'description': result[0].description,
                    'client_id': result[0].client_id
                }

                #current = meraki.getclientsplash(apikey,result[0].networkId,result[0].mac)
                #logging.debug(current)#
                ssid_authorization = {'ssids': {'1': {'isAuthorized': True}, '2': {'isAuthorized': True}}}
                res = meraki.updateclientsplash(apikey,result[0].networkId,result[0].mac,ssid_authorization)
                msg = "client ID {} re-authorized \n{}".format(tempclient['client_id'], res)
                logging.debug(msg)
                self.slack_client.post_message(channel=action.channel, text=msg)
                ret = {
                    'replace_original': 'false',
                    'text': msg
                }
                return Response(json.dumps(ret), status=200, mimetype='application/json')

        return


    def __handle_message_event(self, event):
        if not self.user_id:
            self.user_id = self.get_user_id()
        if event.user_id == self.user_id:
            logging.debug("Ignoring own message")
            return

        if 'meraki' in unicode.lower(event.text):
            orgID = meraki.myorgaccess(apikey=apikey)
            #logging.debug("Your Meraki orgId is {}".format(str(orgID)))

            if 'get networks' in unicode.lower(event.text):
                networkList= meraki.getnetworklist(apikey,orgID)
                #logging.debug(networkList.networkList)

                text = 'you have {} networks in your organisation:\n{}'.format(len(networkList.networkIdList), networkList.networkNameList)

                self.slack_client.post_message(channel=event.channel, text=text)

            elif 'get devices' in unicode.lower(event.text):
                network = unicode.split(unicode.lower(event.text))
                if 'devices' in network[-1]:
                    text = "either put 'all' or the name of the network at the end\n e.g. 'meraki get devices london'"
                    self.slack_client.post_message(channel=event.channel, text=text)
                elif 'all' in network[-1]:
                    networkList = meraki.getnetworklist(apikey, orgID)
                    for net in networkList.networkIdList:
                        devices = meraki.getnetworkdevices(apikey,net,suppressprint=True)
                    text = "gathered {} devices for all networks".format(len(devices))
                    self.slack_client.post_message(channel=event.channel, text=text)
                else:
                    networkList = meraki.getnetworklist(apikey, orgID)
                    #logging.debug("trying to find network '{}' in list {}".format(network[-1].lower(), networkList.networkList))
                    net = [x for x in networkList.networkList if network[-1].lower() in x['name'].lower()]
                    if not net:
                        logging.debug("couldn't find network, aborting")
                        text = "couldn't find network '{}' in our list, please choose from:\n{}".format(network[-1],networkList.networkNameList)
                        self.slack_client.post_message(channel=event.channel, text=text)
                        return
                    else:
                        #logging.debug("found index {} of type {}".format(net, type(net)))
                        networkID = net[0]['id']
                        #logging.debug("found ID {}".format(networkID))
                        devices = meraki.getnetworkdevices(apikey, networkID, suppressprint=True)
                        text = "gathered {} devices for network {} ({})".format(len(devices), net[0]['name'],networkID)
                        self.slack_client.post_message(channel=event.channel, text=text)
                        return

            elif 'get clients' in unicode.lower(event.text):
                if 'force' in unicode.lower(event.text):
                    force=True
                else:
                    force=False
                client = unicode.split(unicode.lower(event.text))

                if 'clients' in client[-1]:
                    text = "either put 'all' or the name of a network or WAP at the end\n" \
                           "e.g. 'meraki get clients network london' or 'merakit get clients WAP11_BSG"
                    self.slack_client.post_message(channel=event.channel, text=text)

                elif 'all' in client[-1]:
                    networkList = meraki.getnetworklist(apikey, orgID)
                    numberClients = 0
                    for net in networkList.networkList:
                        networkID = net['id']
                        networkName = net['name']
                        devices = meraki.getnetworkdevices(apikey, net['id'], suppressprint=True)
                        for device in devices:
                            clientList = meraki.getclients(apikey,device['serial'], timestamp=timespan, force=force,
                                                           networkId=networkID, networkName=networkName)
                            if clientList.clientList:
                                numberClients += len(clientList.clientList)

                    text = "gathered {} clients for all devices".format(numberClients)
                    self.slack_client.post_message(channel=event.channel, text=text)
                    return

                elif 'network' in client:
                    networkList = meraki.getnetworklist(apikey, orgID)
                    #logging.debug("networkList is {}".format(networkList))
                    #if networkList.networkList:
                        #logging.debug(
                        #"trying to find network '{}' in list {}".format(client[-1].lower(), networkList.networkList))
                    net = [x for x in networkList.networkList if client[-1].lower() in x['name'].lower()]

                    if not net:
                        logging.debug("couldn't find network, aborting")
                        text = "couldn't find network '{}' in our list, please choose from:\n{}".format(client[-1],
                                                                                                        networkList.networkNameList)
                        self.slack_client.post_message(channel=event.channel, text=text)
                    else:
                        #logging.debug("found index {} of type {}".format(net, type(net)))
                        networkID = net[0]['id']
                        networkName = net[0]['name']
                        logging.debug("found ID {} with name {}".format(networkID, net[0]['name']))
                        devices = meraki.getnetworkdevices(apikey, networkID, suppressprint=True)
                        #text = "gathering clients from {} devices for network {} ({})".format(len(devices), net[0]['name'], networkID)
                        #self.slack_client.post_message(channel=event.channel, text=text)
                        clientListLen = 0
                        for device in devices:
                            clientList = meraki.getclients(apikey, device['serial'], timestamp=timespan, force=force,
                                                           networkId=networkID, networkName=networkName)
                            if clientList.clientList:
                                clientListLen += len(clientList.clientList)
                        self.slack_client.post_message(channel=event.channel, text=
                            "gathered {} clients for {}".format(str(clientListLen),networkName))
                        return

            elif 'get client' in unicode.lower(event.text):
                client = unicode.split(unicode.lower(event.text))

                if 'client' in client[-1]:
                    text = "either put 'ip x.x.x.x' or 'mac xxxx.xxxx.xxxx.xxxx'"
                    self.slack_client.post_message(channel=event.channel, text=text)

                elif 'mac' in client[-2]:

                    clientresult = meraki_models.MerakiClient.query().filter(meraki_models.MerakiClient.mac == client[-1])
                    result = clientresult.fetch(1)


                    if len(result) > 0:
                        logging.debug(result[0])
                        tempclient = {
                            'mac': result[0].mac,
                            'ip': result[0].ip,
                            'networkName': result[0].networkName,
                            'description': result[0].description,
                            'client_id': result[0].client_id
                        }
                        msg="client ID {} found in network {}\nwith IP address {}\n" \
                            "the description is {}".format(tempclient['client_id'],
                                                                                          tempclient['networkName'],
                                                                                          tempclient['ip'],
                                                                                          tempclient['description'])
                        buttons = [
                            {
                                "text": "Choose an action for this client",
                                "fallback": "Couldn't display action buttons",
                                "callback_id": "client_action",
                                "attachment_type": "default",
                                "actions": [
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "block",
                                        "style": "danger",
                                        "value": "block {}".format(result[0].mac),
                                        "confirm": {
                                            "title": "Are you sure?",
                                            "text": "Really block {}?".format(result[0].mac),
                                            "ok_text": "Yes",
                                            "dismiss_text": "No"
                                        }
                                    },
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "unblock",
                                        "value": "unblock {}".format(result[0].mac)
                                    },
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "de-authorize",
                                        "style": "danger",
                                        "value": "de-authorize {}?".format(result[0].mac),
                                        "confirm": {
                                            "title": "Are you sure?",
                                            "text": "Really de-auth {}".format(result[0].mac),
                                            "ok_text": "Yes",
                                            "dismiss_text": "No"
                                        }
                                    },
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "re-authorize",
                                        "value": "re-authorize {}".format(result[0].mac)
                                    }
                                ]
                            }
                        ]
                        logging.debug(json.loads(json.dumps(buttons)))
                        self.slack_client.post_message(channel=event.channel, text=msg,
                                                       attachments=json.dumps(buttons))
                        return
                    else:
                        msg = "Sorry I couldn't find client with MAC {}".format(client[-1])
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return

                elif 'ip' in client[-2]:

                    clientresult = meraki_models.MerakiClient.query().filter(
                        meraki_models.MerakiClient.ip == client[-1]).order(meraki_models.MerakiClient.timestamp)
                    result = clientresult.fetch(20)
                    logging.debug(result)
                    clientresult2 = meraki_models.MerakiClient.query().filter(
                        meraki_models.MerakiClient.ip == client[-1]).order(-meraki_models.MerakiClient.timestamp)
                    result2 = clientresult2.fetch(20)
                    logging.debug(result2)

                    if len(result) > 0:
                        tempclient = {
                            'mac': result[0].mac,
                            'ip': result[0].ip,
                            'networkName': result[0].networkName,
                            'description': result[0].description,
                            'client_id': result[0].client_id
                        }
                        msg="client ID {} found in network {}\nwith MAC address {}\n" \
                            "the description is {}".format(tempclient['client_id'], tempclient['networkName'],
                                                           tempclient['mac'], tempclient['description'])
                        buttons = [
                            {
                                "text": "Choose an action for this client",
                                "fallback": "Couldn't display action buttons",
                                "callback_id": "client_action",
                                "attachment_type": "default",
                                "actions": [
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "block",
                                        "style": "danger",
                                        "value": "block {}".format(result[0].mac),
                                        "confirm": {
                                            "title": "Are you sure?",
                                            "text": "Really block {}?".format(result[0].mac),
                                            "ok_text": "Yes",
                                            "dismiss_text": "No"
                                        }
                                    },
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "unblock",
                                        "value": "unblock {}".format(result[0].mac)
                                    },
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "de-authorize",
                                        "style": "danger",
                                        "value": "de-authorize {}".format(result[0].mac),
                                        "confirm": {
                                            "title": "Are you sure?",
                                            "text": "Really de-auth {}?".format(result[0].mac),
                                            "ok_text": "Yes",
                                            "dismiss_text": "No"
                                        }
                                    },
                                    {
                                        "name": "action",
                                        "type": "button",
                                        "text": "re-authorize",
                                        "value": "re-authorize {}".format(result[0].mac)
                                    }
                                ]
                            }
                        ]
                        #logging.debug(json.loads(json.dumps(buttons)))
                        self.slack_client.post_message(channel=event.channel, text=msg,
                                                       attachments=json.dumps(buttons))
                        return
                    else:
                        msg = "Sorry I couldn't find client with IP {}".format(client[-1])
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return
            elif 'unblock client' in unicode.lower(event.text):
                client = unicode.split(unicode.lower(event.text))
                if 'client' in client[-1]:
                    text = "put 'unblock client mac xxxx.xxxx.xxxx.xxxx'"
                    self.slack_client.post_message(channel=event.channel, text=text)
                    return
                elif 'mac' in client[-2]:
                    clientresult = meraki_models.MerakiClient.query().filter(
                        meraki_models.MerakiClient.mac == client[-1])
                    result = clientresult.fetch(1)
                    logging.debug(result[0])

                    if result:
                        tempclient = {
                            'mac': result[0].mac,
                            'ip': result[0].ip,
                            'networkName': result[0].networkName,
                            'description': result[0].description,
                            'client_id': result[0].client_id
                        }
                        result = meraki.updateclientpolicy(apikey,result[0].networkId,
                                                               result[0].mac,policy='normal')
                        logging.debug(result)
                        msg = "client ID {} unblocked ".format(tempclient['client_id'])
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return
                        #    msg = "Sorry something went wrong with unblocking the client"
                        #    self.slack_client.post_message(channel=event.channel, text=msg)
                        #    return

                    else:
                        msg = "Sorry I couldn't find client with MAC {}".format(client[-1])
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return
                else:
                    msg = "Couldn't understand the unblock request"
                    logging.debug(msg)
                    self.slack_client.post_message(channel=event.channel, text=msg)
                    return


            elif 'block client' in unicode.lower(event.text):
                client = unicode.split(unicode.lower(event.text))
                logging.debug("{}{}{}{}".format(client[-1],client[-2],client[-3],client[-4]))
                if 'client' in client[-1]:
                    text = "put 'mac xxxx.xxxx.xxxx.xxxx ticket yyyyy'"
                    self.slack_client.post_message(channel=event.channel, text=text)
                    return
                elif 'mac' in client[-4]:
                    clientresult = meraki_models.MerakiClient.query().filter(
                        meraki_models.MerakiClient.mac == client[-3])
                    result = clientresult.fetch(1)
                    logging.debug(result[0])

                    if result:
                        tempclient = {
                            'mac': result[0].mac,
                            'ip': result[0].ip,
                            'networkName': result[0].networkName,
                            'description': result[0].description,
                            'client_id': result[0].client_id
                        }
                        splashblock = blockmsg + client[-1]
                        logging.debug(splashblock)
                        result = meraki.updateclientpolicy(apikey,result[0].networkId,
                                                           result[0].mac,policy='blocked')
                        logging.debug(result)
                        msg = "client ID {} blocked ".format(tempclient['client_id'])
                        logging.debug(msg)
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return
                        # msg = "Sorry something went wrong with blocking the client"
                        #    self.slack_client.post_message(channel=event.channel, text=msg)
                        #    return

                    else:
                        msg = "Sorry I couldn't find client with MAC {}".format(client[-1])
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return
                else:
                    msg = "Couldn't understand the block request"
                    logging.debug(msg)
                    self.slack_client.post_message(channel=event.channel, text=msg)
                    return

            elif 'unauthorize client' in unicode.lower(event.text):
                client = unicode.split(unicode.lower(event.text))
                if 'client' in client[-1]:
                    text = "put 'unauthorize client mac xxxx.xxxx.xxxx.xxxx'"
                    self.slack_client.post_message(channel=event.channel, text=text)
                    return
                elif 'mac' in client[-2]:
                    clientresult = meraki_models.MerakiClient.query().filter(
                        meraki_models.MerakiClient.mac == client[-1])
                    result = clientresult.fetch(1)
                    logging.debug(result[0])

                    if result:
                        tempclient = {
                            'mac': result[0].mac,
                            'ip': result[0].ip,
                            'networkName': result[0].networkName,
                            'description': result[0].description,
                            'client_id': result[0].client_id
                        }
                        result = meraki.updateclientpolicy(apikey,result[0].networkId,
                                                               result[0].mac,policy='normal')
                        logging.debug(result)
                        msg = "client ID {} unblocked ".format(tempclient['client_id'])
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return
                        #    msg = "Sorry something went wrong with unblocking the client"
                        #    self.slack_client.post_message(channel=event.channel, text=msg)
                        #    return

                    else:
                        msg = "Sorry I couldn't find client with MAC {}".format(client[-1])
                        self.slack_client.post_message(channel=event.channel, text=msg)
                        return
                else:
                    msg = "Couldn't understand the unblock request"
                    logging.debug(msg)
                    self.slack_client.post_message(channel=event.channel, text=msg)
                    return

        else:
            msg = 'Hi, I did not understand your message ' + event.text
            #self.slack_client.post_message(channel=event.channel, text=msg)
