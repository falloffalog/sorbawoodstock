import urllib2
import json
from datetime import date, timedelta
from HTMLParser import HTMLParser

def lambda_handler(event, context):
  print("event.session.application.applicationId=" + event['session']['application']['applicationId'])

  if (event['session']['application']['applicationId'] != "amzn1.ask.skill.730afb9b-d402-45ca-888f-5b08bdd9459b"):
    raise ValueError("Invalid Application ID")

  if event['session']['new']:
    on_session_started({'requestId': event['request']['requestId']}, event['session'])

  if event['request']['type'] == "LaunchRequest":
    return on_launch(event['request'], event['session'])
  elif event['request']['type'] == "IntentRequest":
    return on_intent(event['request'], event['session'])
  elif event['request']['type'] == "SessionEndedRequest":
    return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
  print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
  print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
  return get_welcome_response()

def on_intent(intent_request, session):
  print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])

  intent = intent_request['intent']
  intent_name = intent_request['intent']['name']

  if intent_name == "TrailStatus":
    return get_trail_status()
  elif intent_name == "RainTotals":
    return get_rainfall_totals()
  elif intent_name == "AMAZON.HelpIntent":
    return get_welcome_response()
  else:
    raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
  print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])

class MyParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.in_h1 = [ ]

  def handle_starttag(self, tag, attrs):
    if tag == 'h1':
      self.in_h1.append(tag)

  def handle_endtag(self, tag):
    if (tag == 'h1'):
      self.in_h1.pop()

  def handle_data(self, data):
    if self.in_h1:
      self.message = data

def get_trail_status():
  parser = MyParser()
  source = urllib2.urlopen('http://sorbawoodstock.org/trail-status/').read()
  parser.feed(source)
  card_title = "Trail Status"
  speech_output = parser.message
  reprompt_text = "You can ask for trail status, or rainfall totals."
  should_end_session = False
  return build_response(None, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def get_rainfall_totals():
  yesterday = (date.today() - timedelta(1)).strftime('%Y%m%d')
  url = "http://api.wunderground.com/api/bebd5daf809b5428/history_{0}/q/GA/Woodstock.json".format(yesterday)
  response = urllib2.urlopen(url)
  data = json.loads(response.read())
  total = float(data['history']['dailysummary'][0]['precipi'])
  text = "Rainfall total for yesterday was {0} inches.".format(total)
  card_title = "Rainfall Totals"
  speech_output = text
  reprompt_text = "You can ask for trail status, or rainfall totals."
  should_end_session = False
  return build_response(None, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def get_welcome_response():
  session_attributes = {}
  card_title = "Welcome"
  speech_output = "Welcome to the SORBA Woodstock Alexa Skill. You can ask for trail status, or rainfall totals."
  reprompt_text = "You can ask for trail status, or rainfall totals."
  should_end_session = False
  return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
  return {
    'outputSpeech': {
      'type': 'PlainText',
      'text': output
    },
    'card': {
      'type': 'Simple',
      'title': title,
      'content': output
    },
    'reprompt': {
      'outputSpeech': {
        'type': 'PlainText',
        'text': reprompt_text
      }
    },
    'shouldEndSession': should_end_session
  }

def build_response(session_attributes, speechlet_response):
  return {
    'version': '1.0',
    'sessionAttributes': session_attributes,
    'response': speechlet_response
  }
