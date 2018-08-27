# the api layer for the application, calls other
# services and provides data to the frontend graph

import logging
import os
from redis import Redis
import requests
import time

DEBUG = os.environ.get("DEBUG", "").lower().startswith("y")


def getService(serviceName):
    # for x in os.environ:
    #     print(x, '=', os.environ[x])
    print("-------> Service: {}".format(serviceName))
    name = serviceName.upper()
    print("=======> {}_SERVICE_HOST".format(name))
    service = {
        'NAME': name,
        'HOST': os.environ.get("{}_SERVICE_HOST".format(name)),
        'PORT': os.environ.get("{}_SERVICE_PORT".format(name)),
    }
    if 'PORT' in service:
        service['URL'] = 'http://{}'.format(service['HOST'])
    else:
        service['URL'] = 'http://{}:{}'.format(service['HOST'], service['PORT'])

    print('Service: ', name)
    for x in service:
        print(x, ':', service[x])
    return service


log = logging.getLogger(__name__)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)

redisService = getService('REDIS_SERVICE')
redis = Redis(
    host=os.environ.get('HOST', 'redis'),
    port=os.environ.get('PORT', 6379),
    password=os.environ.get('REDIS_PASSWORD')
)


def get_urandom():
    """calls rng to get 32 byte octet"""
    r = requests.get("{}/32".format(getService('RNG_SERVICE').get('URL', 'http://rng_service/')))
    return r.content


def get_hash(data):
    """calls hash_service to get a random SHA1 hash"""
    r = requests.post(getService('HASH_SERVICE').get('URL', 'http://hash_service/'),
                      data=data,
                      headers={"Content-Type": "application/octet-stream"})
    hex_hash = r.text
    return hex_hash


def driver_function(interval=1):
    """runs the loop until stopped"""
    deadline = 0
    loops_done = 0
    while True:
        if time.time() > deadline:
            log.info(" {} units of work done, updating hash counter"
                     .format(loops_done))
            redis.incrby("hashes", loops_done)
            loops_done = 0
            deadline = time.time() + interval
        run_once()
        loops_done += 1


def run_once():
    """runs the loop once"""
    log.debug("One unit of work")
    time.sleep(0.1)
    # gets random bytes
    urandom = get_urandom()
    # uses random bytes to create hash
    hex_hash = get_hash(urandom)
    # checks if hash starts with 1 (1/16 chance)
    if not hex_hash.startswith('a'):
        log.debug("No hash found")
        return
    log.info(" Hash found: {}".format(hex_hash))
    created = redis.hset("wallet", hex_hash, urandom)
    if not created:
        log.info("That hash was already in our wallet")


if __name__ == "__main__":
    while True:
        try:
            driver_function()
        except:
            log.exception("In driver loop:")
            log.error("Waiting 5 sec and restarting")
            time.sleep(5)
