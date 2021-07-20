import requests
import json
import time
import random
import io
import re
import passwords
from serverutils import SERVER_RUNS_LOCALLY


PERMISSION_MANAGE = 262144
PERMISSION_MESSAGES = 4096
PERMISSIONS = PERMISSION_MANAGE | PERMISSION_MESSAGES
ACCESS_TOKEN = passwords.MONIKA_ACCESS_TOKEN
VERSION = '5.131'
GROUP_ID = 205848039
DEBUG_DUMP_LEN = 512
DEBUG_MODE = True
MY_ID = 663419118


def method ( name, params ) :
    return requests.get ( 'https://api.vk.com/method/' + name, params=params )


def poll ( server, key, ts, wait ) :
    return requests.get ( server, params=
        { 'act'  : 'a_check'
        , 'key'  : key
        , 'ts'   : ts
        , 'wait' : wait
        } )


def debug ( *v ) :
    if DEBUG_MODE :
        print ( *v )


def sprint ( *args, **kwargs ) :
    sio = io.StringIO ()
    print ( *args, **kwargs, file=sio )
    return sio.getvalue ()


log_random_id = random.randint ( 0, 0xffff ) # used to send messages

def log ( *v ) :
    global log_random_id
    msg = sprint ( '\n\n========== LOG MESSAGE ==========\n', *v )
    log_random_id += 1
    p = { 'random_id'    : log_random_id
        , 'peer_id'      : 2000000000 + 1
        , 'message'      : msg
        , 'group_id'     : GROUP_ID
        , 'access_token' : ACCESS_TOKEN
        , 'v'            : VERSION
        }
    r = method ( 'messages.send', p )
    debug ( msg, 'duplication status', r.text )




def destruct ( result, fields, dump=None ) :
    values = []
    for keys in fields :
        value = result
        parentkey = '<global>'
        for key in keys :
            try :
                value = value[ key ]
            except KeyError as e :
                if 'error' in value :
                    log ( f'Error responded; dump=', dump )
                    return []
                elif 'failed' in value :
                    value = None
                    break
                else :
                    log ( f'KeyError raised on destruct { parentkey }, missing { e }; dump=', dump )
                    value = None
                    break
        values += [ value ]
        parentkey = key
    return values


def parseraw ( text, *fields ) :
    try :
        result = json.loads ( text ) if type ( text ) == str else text
        dump = json.dumps ( result, indent=2, sort_keys=True )
        if len ( dump ) > DEBUG_DUMP_LEN : dump = dump[ :DEBUG_DUMP_LEN ] + ' ...'
        return destruct ( result, fields, dump )
    except ValueError :
        log ( 'ValueError raised while parsing', text )
        return None


def parse ( response, *fields ) :
    try :
        return parseraw ( response.text, *fields )
    except AttributeError as e :
        log ( f'AttributeError raised while parsing response: { e }' )
        return None




class Reaction :
    def __init__ ( self, type ):
        self.type = type




class User :
    random_id = random.randint ( 0, 0xffff ) # used to send messages

    def __init__ ( self, id ) :
        self.typing_message_was_at = 0
        self.typing_message_id = None # on typing monika will send message
        self.greeting_message_was_at = 0
        self.greeting_message_id = None # on resive monika will send message
        self.id = id
        self.name = None
        # self.reaction = None

    # loads name from page or returns existing one
    def get_name ( self ) :
        if self.name == None :
            p = { 'user_ids'     : self.id
                , 'access_token' : ACCESS_TOKEN
                , 'v'            : VERSION
                }
            r = method ( 'users.get', p )
            ( first_name, ) = parse ( r, [ 'response', 0, 'first_name' ] )
            self.name = first_name
            debug ( 'user name stolen for id', self.id, self.name )
        return self.name

    # creates or gives existing user from dictionary by id
    @classmethod
    def get ( cls, users, id ) :
        if not id in users : users[ id ] = cls ( id )
        return users[ id ]

    # sheduled events for users must be processed here.
    # evaluated every time before poll ( see var. poll_wait_secs in func. listen )
    @classmethod
    def update ( cls, users ) :
        posix = time.time ()
        for id in users :
            user = users[ id ]



            # remove waiting message when certain time pass
            wait_secs = 1
            if user.typing_message_id != None and posix - user.typing_message_was_at > wait_secs :
                p = { 'message_ids'    : user.typing_message_id
                    , 'spam'           : 0
                    , 'delete_for_all' : 1
                    , 'peer_id'        : id
                    , 'group_id'       : GROUP_ID
                    , 'access_token'   : ACCESS_TOKEN
                    , 'v'              : VERSION
                    }
                r = method ( 'messages.delete', p )
                debug ( 'typing message deleted for user', id, r.text )
                user.typing_message_id = None


            # remove greeting mesage and send some text
            wait_secs = 1
            if user.greeting_message_id != None and posix - user.greeting_message_was_at > wait_secs :
                p = { 'message_ids'    : user.greeting_message_id
                    , 'spam'           : 0
                    , 'delete_for_all' : 1
                    , 'peer_id'        : id
                    , 'group_id'       : GROUP_ID
                    , 'access_token'   : ACCESS_TOKEN
                    , 'v'              : VERSION
                    }
                r = method ( 'messages.delete', p )
                debug ( 'greeting message deleted for user', id, r.text )
                user.greeting_message_id = None
                user_name = user.get_name ()
                User.random_id += 1
                p = { 'random_id'    : User.random_id
                    , 'peer_id'      : id
                    , 'message'      : f'Привет, { user_name }'
                    , 'group_id'     : GROUP_ID
                    , 'access_token' : ACCESS_TOKEN
                    , 'v'            : VERSION
                    }
                r = method ( 'messages.send', p )
                debug ( 'greeting message text sent for user', id, r.text )








def receive_poll () :
    p = { 'group_id'     : GROUP_ID
        , 'access_token' : ACCESS_TOKEN
        , 'v'            : VERSION
        }
    r = method ( 'groups.getLongPollServer', p )
    f = ( [ 'response', 'server' ]
        , [ 'response', 'key' ]
        , [ 'response', 'ts' ]
        )
    return parse ( r, *f )





is_running = True


def listen () :


    ( server, key, ts ) = receive_poll ()


    print ( 'monika listening...' )

    users = {}

    devmode = False

    while is_running :

        # sheduled events for users must be processed here
        if not devmode : User.update ( users )





        need_to_poll = True
        while need_to_poll :
            need_to_poll = False # no need to repoll
            r = poll ( server, key, ts, wait=3 )
            f = ( [ 'ts' ]
                , [ 'updates' ]
                )
            ( ts, updates ) = parse ( r, *f )
            if ts == None or updates == None :
                poll_fail = parse ( r, [ 'failed' ] )
                failed = poll_fail[ 0 ]
                # checkout poll fail
                debug ( 'poll returns failed', poll_fail )
                # the event history went out of date or was partially lost
                if failed == 1 :
                    ts = poll_fail[ 1 ]
                    need_to_poll = True
                    continue
                # the key’s active period expired
                elif failed == 2 :
                    ( server, key, ts ) = receive_poll ()
                    need_to_poll = True
                    continue
                 # user information was lost
                elif failed == 3 :
                    ( server, key, ts ) = receive_poll ()
                    need_to_poll = True
                    continue
                # an invalid version number was passed
                elif failed == 4 :
                    log ( 'an invalid version number was passed to poll', poll_fail )
                    return
                # unknown fail
                else :
                    log ( 'unknown poll fail', poll_fail )
                    return





        for u in updates:
            f = ( [ 'type' ]
                , [ 'object' ]
                )
            ( type, object ) = parseraw ( u, *f )


            if type == 'message_typing_state' :

                if devmode : continue # no typing events on devmode

                f = ( [ 'state' ]
                    , [ 'from_id' ]
                    )
                ( state, peer_id ) = parseraw ( object, *f )
                debug ( f'state { state } from { peer_id }' )

                if peer_id < 0 : continue # groups are ignored
                if peer_id >= 2000000000 : continue # ignore chats
                # ignore other chats and users except me if server runs locally
                if SERVER_RUNS_LOCALLY and not ( peer_id == 2000000001 or peer_id == MY_ID ) : continue



                posix = time.time ()

                # +6 because i want to start day from 6 am
                # so from 6 am to 6 pm is day, utc +3
                is_day = ( posix / 60 / 60 + 3 + 6 ) % 24 > 12

                user = User.get ( users, peer_id )


                # send waiting message only if user not already start
                # typing or certain time from last typing event were past
                wait_secs = 60 * 60
                if user.typing_message_id == None and posix - user.typing_message_was_at > wait_secs :
                    User.random_id += 1
                    p = { 'random_id'    : User.random_id
                        , 'peer_id'      : peer_id
                        , 'attachment' : 'photo-205848039_457239017' if is_day else 'photo-205848039_457239018'
                        , 'group_id'     : GROUP_ID
                        , 'access_token' : ACCESS_TOKEN
                        , 'v'            : VERSION
                        }
                    r = method ( 'messages.send', p )
                    ( message_id, ) = parse ( r, [ 'response' ] )
                    user.typing_message_id = message_id
                    user.typing_message_was_at = posix






            elif type == 'message_new' :

                f = ( [ 'message', 'text' ]
                    , [ 'message', 'peer_id' ]
                    )
                ( text, peer_id ) = parseraw ( object, *f )
                debug ( f'new message { text } from { peer_id }' )

                if peer_id < 0 : continue # groups are ignored
                # ignore other chats and users except me if server runs locally
                if SERVER_RUNS_LOCALLY and not ( peer_id == 2000000001 or peer_id == MY_ID ) : continue



                # superuser commands
                if peer_id == MY_ID and text == 'realmode' :
                    devmode = False
                    User.random_id += 1
                    p = { 'random_id'    : User.random_id
                        , 'peer_id'      : peer_id
                        , 'message'      : 'devmode is off'
                        , 'group_id'     : GROUP_ID
                        , 'access_token' : ACCESS_TOKEN
                        , 'v'            : VERSION
                        }
                    r = method ( 'messages.send', p )
                    debug ( 'realmode', r.text )
                    continue
                if peer_id == MY_ID and text == 'devmode' :
                    devmode = True
                    User.random_id += 1
                    p = { 'random_id'    : User.random_id
                        , 'peer_id'      : peer_id
                        , 'message'      : 'devmode is on'
                        , 'group_id'     : GROUP_ID
                        , 'access_token' : ACCESS_TOKEN
                        , 'v'            : VERSION
                        }
                    r = method ( 'messages.send', p )
                    debug ( 'devmode', r.text )
                    continue
                if devmode :
                    continue



                user = User.get ( users, peer_id )
                posix = time.time ()



                # system logic
                if text == 'monika:peer_id' :
                    User.random_id += 1
                    p = { 'random_id'    : User.random_id
                        , 'peer_id'      : peer_id
                        , 'message'      : f'{ peer_id }'
                        , 'group_id'     : GROUP_ID
                        , 'access_token' : ACCESS_TOKEN
                        , 'v'            : VERSION
                        }
                    r = method ( 'messages.send', p )
                    debug ( 'peer id received', r.text )
                    continue
                elif text == 'monika:ping' :
                    User.random_id += 1
                    p = { 'random_id'    : User.random_id
                        , 'peer_id'      : peer_id
                        , 'message'      : 'pong'
                        , 'group_id'     : GROUP_ID
                        , 'access_token' : ACCESS_TOKEN
                        , 'v'            : VERSION
                        }
                    r = method ( 'messages.send', p )
                    debug ( 'status received', r.text )
                    continue



                # chat logics
                if peer_id >= 2000000000 :
                    if re.match ( r'(.*\s)?(юри)\b', text.lower (), flags=re.UNICODE ) != None :
                        User.random_id += 1
                        p = { 'random_id'    : User.random_id
                            , 'peer_id'      : peer_id
                            , 'attachment' : 'photo-205848039_457239021'
                            , 'group_id'     : GROUP_ID
                            , 'access_token' : ACCESS_TOKEN
                            , 'v'            : VERSION
                            }
                        r = method ( 'messages.send', p )
                        debug ( 'uri message received', r.text )




                # messages logic
                else :
                    # remove typing message if exists
                    if user.typing_message_id != None :
                        p = { 'message_ids'    : user.typing_message_id
                            , 'spam'           : 0
                            , 'delete_for_all' : 1
                            , 'peer_id'        : peer_id
                            , 'group_id'       : GROUP_ID
                            , 'access_token'   : ACCESS_TOKEN
                            , 'v'              : VERSION
                            }
                        r = method ( 'messages.delete', p )
                        debug ( 'at messaging typing message deleted for user', peer_id, r.text )
                        user.typing_message_id = None
                    # send greeting message
                    if user.greeting_message_id == None :
                        User.random_id += 1
                        p = { 'random_id'    : User.random_id
                            , 'peer_id'      : peer_id
                            , 'attachment' : 'photo-205848039_457239019'
                            , 'group_id'     : GROUP_ID
                            , 'access_token' : ACCESS_TOKEN
                            , 'v'            : VERSION
                            }
                        r = method ( 'messages.send', p )
                        ( message_id, ) = parse ( r, [ 'response' ] )
                        user.greeting_message_id = message_id
                        user.greeting_message_was_at = posix






            else :
                debug ( 'unparsed update type', type )
