import requests
import simplejson
import datetime
from functools import wraps
from bson import json_util
from metadataservice.client import conf

# READ THE DOCS and COMMENTS before grabbing your pitchforks and torches. A lot going on here!!
# The client lives in the service for now. I will move it to separate repo once ready for alpha release

# TODO: Find a way to handle auth with each request. Policy decision, tell me what to do people


def server_connect(host, port, protocol='http'):
    # Do not gasp yet! I copied w/e mongoengine did for global connections
    # Tbh, works pretty neatly and it is quite intuitive
    global _server_path
    _server_path = protocol + '://' + host + ':' + str(port)
    return _server_path


def _ensure_connection(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # TODO: Fix load_configuration()
        protocol = conf.connection_config['protocol']
        host = conf.connection_config['host']
        port = conf.connection_config['port']
        server_connect(host=host, port=port, protocol=protocol)
        return func(*args, **kwargs)
    return inner


@_ensure_connection
def find_run_starts(**kwargs):
    """Given search criteria, locate RunStart Documents.
    As we describe in design document, time here is strictly the time
    server entry was created, not IOC timestamp. For the difference, refer
    to: nsls-ii.github.io
    Parameters
    ----------
    start_time : time-like, optional
        time-like representation of the earliest time that a RunStart
        was created. Valid options are:
           - timestamps --> time.time()
           - '2015'
           - '2015-01'
           - '2015-01-30'
           - '2015-03-30 03:00:00'
           - datetime.datetime.now()
    stop_time : time-like, optional
        timestamp of the latest time that a RunStart was created. See
        docs for `start_time` for examples.
    `beamline_id : str, optional
        String identifier for a specific beamline
    project : str, optional
        Project name
    owner : str, optional
        The username of the logged-in user when the scan was performed
    scan_id : int, optional
        Integer scan identifier
    uid : str, optional
        Globally unique id string provided to metadatastore
    _id : str or ObjectId, optional
        The unique id generated by mongo

    Returns
    -------
    content : iterable of list of json documents
        We need lists to be able to JSON encode multiple dicts. We can return an iterator of
         iterator?

    Note
    ----
    All documents that the RunStart Document points to are dereferenced.
    These include RunStop, BeamlineConfig, and Sample.

    Examples
    --------
    >>> find_run_starts(scan_id=123)
    >>> find_run_starts(owner='arkilic')
    >>> find_run_starts(start_time=1421176750.514707, stop_time=time.time()})
    >>> find_run_starts(start_time=1421176750.514707, stop_time=time.time())
    >>> find_run_starts(owner='arkilic', start_time=1421176750.514707,
    ...                stop_time=time.time())
    """
    _format_time(kwargs)
    range_floor = 0
    range_ceil = 50
    query = kwargs
    while True:
        query['range_floor'] = range_floor
        query['range_ceil'] = range_ceil
        r = requests.get(_server_path + "/run_start", params=simplejson.dumps(query))
        content = json_util.loads(r.text)
        if not content:
            StopIteration()
            break
        else:
            yield content
            range_ceil += 50
            range_floor += 50


@_ensure_connection
def find_run_stops(**kwargs):
    """Given search criteria, query for RunStop Documents.
    Parameters
    ----------
    run_start : metadatastore.document.Document or str, optional
        The metadatastore run start document or the metadatastore uid to get
        the corresponding run end for
    start_time : time-like, optional
        time-like representation of the earliest time that a RunStop
        was created. Valid options are:
           - timestamps --> time.time()
           - '2015'
           - '2015-01'
           - '2015-01-30'
           - '2015-03-30 03:00:00'
           - datetime.datetime.now()
    stop_time : time-like, optional
        timestamp of the latest time that a RunStop was created. See
        docs for `start_time` for examples.
    exit_status : {'success', 'fail', 'abort'}, optional
        provides information regarding the run success.
    reason : str, optional
        Long-form description of why the run was terminated.
    uid : str, optional
        Globally unique id string provided to metadatastore
    _id : str or ObjectId, optional
        The unique id generated by mongo

    Returns
    -------
    content : iterable of list of json documents
        We need lists to be able to JSON encode multiple dicts. We can return an iterator of
         iterator?
    """
    _format_time(kwargs)
    range_floor = 0
    range_ceil = 50
    query = kwargs
    while True:
        query['range_floor'] = range_floor
        query['range_ceil'] = range_ceil
        r = requests.get(_server_path + "/run_stop", params=simplejson.dumps(query))
        content = json_util.loads(r.text)
        if not content:
            StopIteration()
            break
        else:
            yield content
            range_ceil += 50
            range_floor += 50


@_ensure_connection
def find_events(**kwargs):
    """Given search criteria, locate Event Documents.

    Parameters
    -----------
    start_time : time-like, optional
        time-like representation of the earliest time that an Event
        was created. Valid options are:
           - timestamps --> time.time()
           - '2015'
           - '2015-01'
           - '2015-01-30'
           - '2015-03-30 03:00:00'
           - datetime.datetime.now()
    stop_time : time-like, optional
        timestamp of the latest time that an Event was created. See
        docs for `start_time` for examples.
    descriptor : metadatastore.document.Document or uid, optional
        if Document:
            The metadatastore run start document or the metadatastore uid to get
            the corresponding run end for
        if uid:
            Globally unique id string provided to metadatastore for the
            EventDescriptor Document.
    uid : str, optional
        Globally unique id string provided to metadatastore
    _id : str or ObjectId, optional
        The unique id generated by mongo

    Returns
    -------
    content : iterable of list of json documents
        We need lists to be able to JSON encode multiple dicts. We can return an iterator of
         iterator?
    """
    _format_time(kwargs)
    range_floor = 0
    range_ceil = 1000
    query = kwargs
    while True:
        query['range_floor'] = range_floor
        query['range_ceil'] = range_ceil
        r = requests.get(_server_path + "/event", params=simplejson.dumps(query))
        content = json_util.loads(r.text)
        if not content:
            StopIteration()
            break
        else:
            yield content
            range_ceil += 1000
            range_floor += 1000


@_ensure_connection
def find_last():
    pass


@_ensure_connection
def find_beamline_configs(**kwargs):
    """Given search criteria, locate BeamlineConfig Documents.

    Parameters
    ----------
    start_time : time-like, optional
        time-like representation of the earliest time that a BeamlineConfig
        was created. Valid options are:
           - timestamps --> time.time()
           - '2015'
           - '2015-01'
           - '2015-01-30'
           - '2015-03-30 03:00:00'
           - datetime.datetime.now()
    stop_time : time-like, optional
        timestamp of the latest time that a BeamlineConfig was created. See
            docs for `start_time` for examples.
    uid : str, optional
        Globally unique id string provided to metadatastore
    _id : str or ObjectId, optional
        The unique id generated by mongo

    Returns
    -------
    content : iterable of list of json documents
        We need lists to be able to JSON encode multiple dicts. We can return an iterator of
         iterator?
    """
    _format_time(kwargs)
    range_floor = 0
    range_ceil = 50
    query = kwargs
    while True:
        query['range_floor'] = range_floor
        query['range_ceil'] = range_ceil
        r = requests.get(_server_path + "/beamline_config", params=simplejson.dumps(query))
        content = json_util.loads(r.text)
        if not content:
            StopIteration()
            break
        else:
            yield content
            range_ceil += 50
            range_floor += 50


@_ensure_connection
def find_event_descriptors(**kwargs):
    """Given search criteria, locate EventDescriptor Documents.

    Parameters
    ----------
    run_start : metadatastore.document.Document or uid, optional
        The metadatastore run start document or the metadatastore uid to get
        the corresponding run end for
    run_start_uid : str
        Globally unique id string provided to metadatastore for the
        RunStart Document.
    start_time : time-like, optional
        time-like representation of the earliest time that an EventDescriptor
        was created. Valid options are:
           - timestamps --> time.time()
           - '2015'
           - '2015-01'
           - '2015-01-30'
           - '2015-03-30 03:00:00'
           - datetime.datetime.now()
    stop_time : time-like, optional
        timestamp of the latest time that an EventDescriptor was created. See
        docs for `start_time` for examples.
    uid : str, optional
        Globally unique id string provided to metadatastore
    _id : str or ObjectId, optional
        The unique id generated by mongo

    Returns
    -------
    content : iterable of list of json documents
        We need lists to be able to JSON encode multiple dicts. We can return an iterator of
         iterator?
    """
    _format_time(kwargs)
    range_floor = 0
    range_ceil = 50
    query = kwargs
    while True:
        query['range_floor'] = range_floor
        query['range_ceil'] = range_ceil
        r = requests.get(_server_path + '/event_descriptor', params=simplejson.dumps(query))
        content = json_util.loads(r.text)
        if not content:
            StopIteration()
            break
        else:
            yield content
            range_ceil += 50
            range_floor += 50


@_ensure_connection
def insert_event():
    pass


@_ensure_connection
def insert_event_descriptor():
    pass


@_ensure_connection
# def insert_run_start(time, scan_id, beamline_id, beamline_config, uid=None,
#                      owner=None, group=None, project=None, custom=None):
def insert_run_start(time, scan_id, uid, custom={}):
    """Provide a head for a sequence of events. Entry point for an
    experiment's run.

    Parameters
    ----------
    time : float
        The date/time as found at the client side when an event is
        created.
    scan_id : int
        Unique scan identifier visible to the user and data analysis
    beamline_id : str
        Beamline String identifier. Not unique, just an indicator of
        beamline code for multiple beamline systems
    beamline_config : metadatastore.documents.Document or str
        if Document:
            The metadatastore beamline config document
        if str:
            uid of beamline config corresponding to a given run
    uid : str, optional
        Globally unique id string provided to metadatastore
    owner : str, optional
        A username associated with the entry
    group : str, optional
        A group (e.g., UNIX group) associated with the entry
    project : str, optional
        Any project name to help users locate the data
    custom: dict, optional
        Any additional information that data acquisition code/user wants
        to append to the Header at the start of the run.

    """
    # TODO: See what @tacaswell's pr has done for this...
    # 1. Get all related documents
    # 2. Get their uids?
    # 3. Convert to dict
    # 4. validate
    # 5. json encode
    # 6. across the wire
    
    data = {'time': time, 'scan_id': scan_id, 'uid': uid}
    data.update(custom)
    payload = json_util.dumps(data)
    r = requests.post(_server_path + '/run_start', data=payload)
    return r.status_code
@_ensure_connection
def insert_run_stop():
    pass


@_ensure_connection
def insert_beamline_config():
    pass


@_ensure_connection
def format_events():
    pass


def format_data_keys():
    pass


def _format_time(search_dict):
    """Helper function to format the time arguments in a search dict

    Expects 'start_time' and 'stop_time'

    ..warning: Does in-place mutation of the search_dict
    """
    time_dict = {}
    start_time = search_dict.pop('start_time', None)
    stop_time = search_dict.pop('stop_time', None)
    if start_time:
        time_dict['$gte'] = _normalize_human_friendly_time(start_time)
    if stop_time:
        time_dict['$lte'] = _normalize_human_friendly_time(stop_time)
    if time_dict:
        search_dict['time'] = time_dict


def _normalize_human_friendly_time(val):
    """Given one of :
    - string (in one of the formats below)
    - datetime (eg. datetime.datetime.now()), with or without tzinfo)
    - timestamp (eg. time.time())
    return a timestamp (seconds since jan 1 1970 UTC).

    Non string/datetime.datetime values are returned unaltered.
    Leading/trailing whitespace is stripped.
    Supported formats:
    {}
    """
    # {} is placeholder for formats; filled in after def...

    tz = conf.connection_config['timezone']  # e.g., 'US/Eastern'
    zone = pytz.timezone(tz)  # tz as datetime.tzinfo object
    epoch = pytz.UTC.localize(datetime.datetime(1970, 1, 1))
    check = True

    if isinstance(val, six.string_types):
        # unix 'date' cmd format '%a %b %d %H:%M:%S %Z %Y' works but
        # doesn't get TZ?

        # Could cleanup input a bit? remove leading/trailing [ :,-]?
        # Yes, leading/trailing whitespace to match pandas behavior...
        # Actually, pandas doesn't ignore trailing space, it assumes
        # the *current* month/day if they're missing and there's
        # trailing space, or the month is a single, non zero-padded digit.?!
        val = val.strip()

        for fmt in _TS_FORMATS:
            try:
                ts = datetime.datetime.strptime(val, fmt)
                break
            except ValueError:
                pass

        try:
            if isinstance(ts, datetime.datetime):
                val = ts
                check = False
            else:
                raise TypeError('expected datetime.datetime,'
                                ' got {:r}'.format(ts))

        except NameError:
            raise ValueError('failed to parse time: ' + repr(val))

    if check and not isinstance(val, datetime.datetime):
        return val

    if val.tzinfo is None:
        # is_dst=None raises NonExistent and Ambiguous TimeErrors
        # when appropriate, same as pandas
        val = zone.localize(val, is_dst=None)

    return (val - epoch).total_seconds()


# human friendly timestamp formats we'll parse
_TS_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',  # these 2 are not as originally doc'd,
    '%Y-%m-%d %H',  # but match previous pandas behavior
    '%Y-%m-%d',
    '%Y-%m',
    '%Y']

# build a tab indented, '-' bulleted list of supported formats
# to append to the parsing function docstring below
_doc_ts_formats = '\n'.join('\t- {}'.format(_) for _ in _TS_FORMATS)

# fill in the placeholder we left in the previous docstring
_normalize_human_friendly_time.__doc__ = (
    _normalize_human_friendly_time.__doc__.format(_doc_ts_formats)
)

