import logging
import settings
import datetime
import urlparse
import json

from flask import Flask, request, jsonify, abort

from event import Event
from action import Action
from bot import Bot
from slack_web_api_client import SlackWebAPIClient
from settings import API_KEY as apikey, CLIENT_TIMESPAN as timespan
import meraki

app = Flask(__name__)

verification_token = settings.VERIFICATION_TOKEN

slack_client = SlackWebAPIClient(settings.BOT_ACCESS_TOKEN)
bot = Bot(slack_client)


@app.route('/')
def root():
    text = "Hello from Google App Engine!"
    slack_client.post_message(channel='#general',
                              text=text)
    return text


@app.route('/slack/event', methods=['POST'])
def slack_event():
    logging.debug("Request payload: %s", request.data)
    event = request.get_json()
    if 'token' not in event:
        logging.error(
            "There is no verification token in the JSON, discarding event")
        abort(401)
    if event['token'] != verification_token:
        logging.error("Wrong verification token in JSON, discarding event")
        abort(403)
    if 'challenge' in event:
        return jsonify({'challenge': event['challenge']})
    else:
        bot.handle_event(Event(event))
        return jsonify({})


@app.route('/slack/action-endpoint', methods=['POST'])
def slack_action():
    logging.debug(request.get_data())
    logging.debug(request.headers)
    #logging.debug("Request payload: %s", request.data)
    data = request.data
    #logging.debug(data)
    blob = urlparse.parse_qs(data)
    #logging.debug(blob)
    dic = dict(blob)
    act = dic['payload'][0]
    action = json.loads(act)
    #logging.debug(action)
    # action = request.get_json()
    #logging.debug(type(action))
    if 'token' not in action:
        logging.error(
            "There is no verification token in the JSON, discarding event")
        abort(401)
    if action['token'] != verification_token:
        logging.error("Wrong verification token in JSON, discarding event")
        abort(403)
    if 'challenge' in action:
        return jsonify({'challenge': action['challenge']})
    else:
        bot.handle_action(Action(action))
        return jsonify({})


@app.route('/cron/refreshNetworks')
def refresh_Networks():
    logging.debug("Cron job to refresh networks was triggered")

    orgID = meraki.myorgaccess(apikey=apikey)
    networkList = meraki.getnetworklist(apikey, orgID)
    if networkList.networkList:

        text = "Refreshed {} networks from a cron job".format(len(networkList.networkList))
        #slack_client.post_message(channel='#general', text=text)
        logging.debug(text)
        return 'Finished refreshing networks', 200
    else:
        text = "Something went wrong refreshing networks from a cron job".format(len(networkList.networkList))
        #slack_client.post_message(channel='#general', text=text)
        logging.debug(text)
        return 'Failed to refresh networks', 500


@app.route('/cron/refreshDevices')
def refresh_Devices():
    logging.debug("Cron job to refresh networks was triggered")

    orgID = meraki.myorgaccess(apikey=apikey)
    networkList = meraki.getnetworklist(apikey, orgID)

    if networkList.networkList:
        logging.debug("network ID list is {}".format(len(networkList.networkIdList)))
        numberDevices = 0
        for net in networkList.networkIdList:
            logging.debug("fetching devices for {}".format(net))
            try:
                devices = meraki.getnetworkdevices(apikey, net, suppressprint=True)
                numberDevices += len(devices)
            except:
                logging.debug("Cron job to refresh devices failed")
                return 'Failed to refresh devices', 500
        text = "gathered {} devices for all networks in a cron job".format(numberDevices)
        #slack_client.post_message(channel='#general', text=text)
        logging.debug(text)
        return 'Finished refreshing devices', 200

    else:
        text = "Something went wrong refreshing networks from a cron job".format(len(networkList.networkList))
        #slack_client.post_message(channel='#general', text=text)
        logging.debug("Cron job to refresh networks has finished in failure")
        return 'Failed to refresh networks', 500

@app.route('/cron/refreshClients')
def refresh_Clients():
    logging.debug("Cron job to refresh clients was triggered at {}".format(datetime.datetime.now()))

    orgID = meraki.myorgaccess(apikey=apikey)
    networkList = meraki.getnetworklist(apikey, orgID)

    if networkList.networkList:
        logging.debug("network ID list is {}".format(len(networkList.networkIdList)))
        numberDevices = 0
        numberClients = 0
        for net in networkList.networkList:
            logging.debug("fetching devices for {}".format(net))
            networkID = net['id']
            networkName = net['name']
            logging.debug("{} - {}".format(networkID,networkName))
            try:
                devices = meraki.getnetworkdevices(apikey, net['id'], suppressprint=True)
                numberDevices += len(devices)
                logging.debug(len(devices))
                for device in devices:

                    try:
                        logging.debug(device['serial'])
                        clientList = meraki.getclients(apikey, device['serial'], timestamp=timespan, force=True,
                                                       networkId=networkID, networkName=networkName)
                        if clientList.clientList:
                            numberClients += len(clientList.clientList)
                    except:
                        logging.debug("Cron job to refresh clients failed for device {}".format(device['name']))
                        pass
            except:
                logging.debug("Cron job to refresh clients failed on getting devices")
                return 'Failed to refresh clients', 500

        text = "gathered {} clients for all networks in a cron job".format(numberClients)
        #slack_client.post_message(channel='#general', text=text)
        logging.debug(text)
        return 'Finished refreshing clients', 200

    else:
        text = "Something went wrong refreshing clients from a cron job"
        slack_client.post_message(channel='#general',
                                  text=text)
        logging.debug("Cron job to refresh clients has finished in failure")
        return 'Failed to refresh clients ', 500

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

