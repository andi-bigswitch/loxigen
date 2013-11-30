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
:: import itertools
:: from loxi_globals import OFVersions
:: import py_gen.util as util
:: include('_copyright.py')

:: include('_autogen.py')

import struct
import const
import util
import loxi.generic_util
import loxi
:: if version >= OFVersions.VERSION_1_2:
import oxm # for unpack
:: #endif

def unpack_list(reader):
    def deserializer(reader, typ):
        parser = parsers.get(typ)
        if not parser: raise loxi.ProtocolError("unknown action type %d" % typ)
        return parser(reader)
    return loxi.generic_util.unpack_list_tlv16(reader, deserializer)

:: for ofclass in ofclasses:
:: if ofclass.virtual:
:: include('_virtual_ofclass.py', ofclass=ofclass)
:: else:
:: include('_ofclass.py', ofclass=ofclass)
:: #endif

:: #endfor

def parse_experimenter(reader):
    experimenter, = reader.peek("!4xL")
    if experimenter == 0x005c16c7: # Big Switch Networks
        subtype, = reader.peek("!8xL")
    elif experimenter == 0x00002320: # Nicira
        subtype, = reader.peek("!8xH")
    else:
        raise loxi.ProtocolError("unexpected experimenter id %#x" % experimenter)

    if subtype in experimenter_parsers[experimenter]:
        return experimenter_parsers[experimenter][subtype](reader)
    else:
        raise loxi.ProtocolError("unexpected BSN experimenter subtype %#x" % subtype)

parsers = {
:: concrete_ofclasses = [x for x in ofclasses if not x.virtual]
:: sort_key = lambda x: x.member_by_name('type').value
:: msgtype_groups = itertools.groupby(sorted(concrete_ofclasses, key=sort_key), sort_key)
:: for (k, v) in msgtype_groups:
:: k = util.constant_for_value(version, "ofp_action_type", k)
:: v = list(v)
:: if len(v) == 1:
    ${k} : ${v[0].pyname}.unpack,
:: else:
    ${k} : parse_${k[12:].lower()},
:: #endif
:: #endfor
}

:: experimenter_ofclasses = [x for x in concrete_ofclasses if x.member_by_name('type').value == 0xffff]
:: sort_key = lambda x: x.member_by_name('experimenter').value
:: experimenter_ofclasses.sort(key=sort_key)
:: grouped = itertools.groupby(experimenter_ofclasses, sort_key)
experimenter_parsers = {
:: for (experimenter, v) in grouped:
    ${experimenter} : {
:: for ofclass in v:
        ${ofclass.member_by_name('subtype').value}: ${ofclass.pyname}.unpack,
:: #endfor
    },
:: #endfor
}
