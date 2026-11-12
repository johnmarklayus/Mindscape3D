"""Replace only Walk/Run in the Unity GLB with a fresh Blender GLB export."""
import copy
import json
import pathlib
import struct
import sys


def read(path):
    data = pathlib.Path(path).read_bytes()
    assert data[:4] == b"glTF"
    size = struct.unpack_from("<I", data, 12)[0]
    doc = json.loads(data[20:20 + size])
    offset = 20 + size
    length, kind = struct.unpack_from("<II", data, offset)
    assert kind == 0x004E4942
    return doc, bytearray(data[offset + 8:offset + 8 + length])


def update(source, destination, all_actions=False):
    src, src_bin = read(source)
    dst, dst_bin = read(destination)
    original = copy.deepcopy(dst)
    node_map = {n['name']: i for i, n in enumerate(dst['nodes'])}
    accessors = {}

    def accessor(index, time=False):
        key = (index, time)
        if key in accessors:
            return accessors[key]
        a = copy.deepcopy(src['accessors'][index])
        assert 'sparse' not in a
        view = src['bufferViews'][a['bufferView']]
        assert view['buffer'] == 0 and 'byteStride' not in view
        start = view.get('byteOffset', 0)
        payload = bytearray(src_bin[start:start + view['byteLength']])
        if time:
            assert a['componentType'] == 5126 and a['type'] == 'SCALAR'
            offset = a.get('byteOffset', 0)
            values = list(struct.unpack_from('<' + 'f' * a['count'], payload, offset))
            origin = values[0]
            values = [v - origin for v in values]
            struct.pack_into('<' + 'f' * len(values), payload, offset, *values)
            a['min'], a['max'] = [min(values)], [max(values)]
        dst_bin.extend(b'\0' * (-len(dst_bin) % 4))
        a['bufferView'] = len(dst['bufferViews'])
        dst['bufferViews'].append({'buffer': 0, 'byteOffset': len(dst_bin), 'byteLength': len(payload)})
        dst_bin.extend(payload)
        accessors[key] = len(dst['accessors'])
        dst['accessors'].append(a)
        return accessors[key]

    report = []
    clips = [('Walk', 49, 1.0), ('Run', 37, .75)]
    if all_actions:
        clips = [(a['name'], src['accessors'][a['samplers'][0]['input']]['count'],
                  (src['accessors'][a['samplers'][0]['input']]['count'] - 1) / 48)
                 for a in src['animations']]
    for name, count, seconds in clips:
        animation = copy.deepcopy(next(a for a in src['animations'] if a['name'] == name))
        for channel in animation['channels']:
            node = src['nodes'][channel['target']['node']]
            assert node['name'] in node_map
            target = dst['nodes'][node_map[node['name']]]
            for transform in ('translation', 'rotation', 'scale', 'matrix'):
                assert node.get(transform) == target.get(transform), (node['name'], transform)
            channel['target']['node'] = node_map[node['name']]
        for sampler in animation['samplers']:
            sampler['input'] = accessor(sampler['input'], time=True)
            sampler['output'] = accessor(sampler['output'])
            times = dst['accessors'][sampler['input']]
            assert times['count'] == count
            assert abs(times['max'][0] - seconds) < 1e-5
        index = next((i for i, a in enumerate(dst['animations']) if a['name'] == name), None)
        if index is None:
            dst['animations'].append(animation)
        else:
            dst['animations'][index] = animation
        report.append({'clip': name, 'samples': count, 'duration': seconds})
    for key in original:
        if key not in ('animations', 'accessors', 'bufferViews', 'buffers'):
            assert dst[key] == original[key], key
    for before, after in zip(original['animations'], dst['animations']):
        if not all_actions and before['name'] not in ('Walk', 'Run'):
            assert before == after
    dst['buffers'][0]['byteLength'] = len(dst_bin)
    text = json.dumps(dst, separators=(',', ':')).encode()
    text += b' ' * (-len(text) % 4)
    dst_bin.extend(b'\0' * (-len(dst_bin) % 4))
    data = struct.pack('<4sII', b'glTF', 2, 28 + len(text) + len(dst_bin))
    data += struct.pack('<II', len(text), 0x4E4F534A) + text
    data += struct.pack('<II', len(dst_bin), 0x004E4942) + dst_bin
    pathlib.Path(destination).write_bytes(data)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    update(sys.argv[1], sys.argv[2], '--all' in sys.argv[3:])
