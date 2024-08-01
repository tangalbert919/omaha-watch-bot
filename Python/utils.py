from checkin import checkin_generator_pb2
import binascii, os, random

def generateImei():
    imei = [random.randint(0,9) for _ in range(15)]
    return ''.join(map(str, imei))

def generateMac():
    return binascii.b2a_hex(os.urandom(6))

def generateSerial():
    serial = [random.choice('0123456789abcdef') for _ in range(8)]
    return ''.join(serial)

def generateDigest():
    digest = [random.choice('0123456789abcdef') for _ in range(40)]
    return '1-' + ''.join(digest)

def construct_payload(fingerprint: str):
    # <oem>/<product>/<device>:<android_version>/<build_tag>/<incremental>:user/release-keys
    # TODO: implement
    prop_list = fingerprint.split('/')
    device_ver = prop_list[2].split(':')[1]

    # Create the headers
    headers = {
    'accept-encoding': 'gzip, deflate',
    'content-encoding': 'gzip',
    'content-type': 'application/x-protobuffer',
    'user-agent': f'Dalvik/2.1.0 (Linux; U; Android {device_ver}; {prop_list[1]} Build/{prop_list[3]})'
    }

    # Create needed proto objects
    checkinproto = checkin_generator_pb2.AndroidCheckinProto()
    payload = checkin_generator_pb2.AndroidCheckinRequest()
    build = checkin_generator_pb2.AndroidBuildProto()

    # Start adding properties
    build.id = fingerprint
    build.timestamp = 0
    build.device = prop_list[2][:-3]

    checkinproto.build.CopyFrom(build)
    checkinproto.lastCheckinMsec = 0
    checkinproto.roaming = "WIFI::"
    checkinproto.userNumber = 0
    checkinproto.deviceType = 2
    checkinproto.voiceCapable = False
    checkinproto.unknown19 = "WIFI"

    payload.imei = generateImei()
    payload.id = 0
    payload.digest = generateDigest()
    payload.checkin.CopyFrom(checkinproto)
    payload.locale = 'en-US'
    payload.macAddr.append(generateMac())
    payload.timeZone = 'America/New_York'
    payload.version = 3
    payload.serialNumber = generateSerial()
    payload.macAddrType.append('wifi')
    payload.fragment = 0
    payload.userSerialNumber = 0
    payload.fetchSystemUpdates = 1
    payload.unknown30 = 0
    return (payload.SerializeToString(), headers)