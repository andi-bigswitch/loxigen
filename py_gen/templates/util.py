:: # Copyright 2013, Big Switch Networks, Inc.
:: #
:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
:: # the following special exception:
:: #
:: # LOXI Exception
:: #
:: # As a special exception to the terms of the EPL, you may distribute libraries
:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
:: # from the LoxiGen Libraries and the notice provided below is (i) included in
:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
:: # documentation for the LoxiGen Libraries, if distributed in binary form.
:: #
:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
:: #
:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
:: # a copy of the EPL at:
:: #
:: # http://www.eclipse.org/legal/epl-v10.html
:: #
:: # Unless required by applicable law or agreed to in writing, software
:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
:: # EPL for the specific language governing permissions and limitations
:: # under the EPL.
::
:: include('_copyright.py')
:: from loxi_globals import OFVersions
:: include('_autogen.py')

import struct
import loxi
import const
import common
import action
:: if version >= OFVersions.VERSION_1_1:
import instruction
:: #endif
:: if version >= OFVersions.VERSION_1_2:
import oxm
:: #endif
:: if version >= OFVersions.VERSION_1_3:
import meter_band
:: #endif

def pretty_mac(mac):
    return ':'.join(["%02x" % x for x in mac])

def pretty_ipv4(v):
    return "%d.%d.%d.%d" % ((v >> 24) & 0xFF, (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF)

def pretty_flags(v, flag_names):
    set_flags = []
    for flag_name in flag_names:
        flag_value = getattr(const, flag_name)
        if v & flag_value == flag_value:
            set_flags.append(flag_name)
        elif v & flag_value:
            set_flags.append('%s&%#x' % (flag_name, v & flag_value))
        v &= ~flag_value
    if v:
        set_flags.append("%#x" % v)
    return '|'.join(set_flags) or '0'

:: if version in (OFVersions.VERSION_1_0, OFVersions.VERSION_1_1):
def pretty_wildcards(v):
    if v == const.OFPFW_ALL:
        return 'OFPFW_ALL'
    flag_names = ['OFPFW_IN_PORT', 'OFPFW_DL_VLAN', 'OFPFW_DL_SRC', 'OFPFW_DL_DST',
                  'OFPFW_DL_TYPE', 'OFPFW_NW_PROTO', 'OFPFW_TP_SRC', 'OFPFW_TP_DST',
                  'OFPFW_NW_SRC_MASK', 'OFPFW_NW_DST_MASK', 'OFPFW_DL_VLAN_PCP',
                  'OFPFW_NW_TOS']
    return pretty_flags(v, flag_names)
:: #endif

def pretty_port(v):
    named_ports = [(k,v2) for (k,v2) in const.__dict__.iteritems() if k.startswith('OFPP_')]
    for (k, v2) in named_ports:
        if v == v2:
            return k
    return v

def pack_port_no(value):
:: if version == OFVersions.VERSION_1_0:
    return struct.pack("!H", value)
:: else:
    return struct.pack("!L", value)
:: #endif

def unpack_port_no(reader):
:: if version == OFVersions.VERSION_1_0:
    return reader.read("!H")[0]
:: else:
    return reader.read("!L")[0]
:: #endif

def pack_fm_cmd(value):
:: if version == OFVersions.VERSION_1_0:
    return struct.pack("!H", value)
:: else:
    return struct.pack("!B", value)
:: #endif

def unpack_fm_cmd(reader):
:: if version == OFVersions.VERSION_1_0:
    return reader.read("!H")[0]
:: else:
    return reader.read("!B")[0]
:: #endif

def init_wc_bmap():
:: if version <= OFVersions.VERSION_1_1:
    return const.OFPFW_ALL
:: else:
    return 0
:: #endif

def pack_wc_bmap(value):
:: if version <= OFVersions.VERSION_1_1:
    return struct.pack("!L", value)
:: else:
    return struct.pack("!Q", value)
:: #endif

def unpack_wc_bmap(reader):
:: if version <= OFVersions.VERSION_1_1:
    return reader.read("!L")[0]
:: else:
    return reader.read("!Q")[0]
:: #endif

def init_match_bmap():
:: if version <= OFVersions.VERSION_1_1:
    return const.OFPFW_ALL
:: else:
    return 0
:: #endif

def pack_match_bmap(value):
:: if version <= OFVersions.VERSION_1_1:
    return struct.pack("!L", value)
:: else:
    return struct.pack("!Q", value)
:: #endif

def unpack_match_bmap(reader):
:: if version <= OFVersions.VERSION_1_1:
    return reader.read("!L")[0]
:: else:
    return reader.read("!Q")[0]
:: #endif

def pack_list(values):
    return "".join([x.pack() for x in values])

MASK64 = (1 << 64) - 1

def pack_bitmap_128(value):
    x = 0l
    for y in value:
        x |= 1 << y
    return struct.pack("!QQ", (x >> 64) & MASK64, x & MASK64)

def unpack_bitmap_128(reader):
    hi, lo = reader.read("!QQ")
    x = (hi << 64) | lo
    i = 0
    value = set()
    while x != 0:
        if x & 1 == 1:
            value.add(i)
        i += 1
        x >>= 1
    return value

def unpack_list_hello_elem(reader):
    def deserializer(reader):
        typ, length, = reader.peek('!HH')
        reader = reader.slice(length)
        try:
            return common.hello_elem.unpack(reader)
        except loxi.ProtocolError:
            return None
    return [x for x in loxi.generic_util.unpack_list(reader, deserializer) if x != None]
