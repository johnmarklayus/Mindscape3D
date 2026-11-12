"""Run in Blender: transfer shared animation objects without changing model data."""
import copy
import json
from pathlib import Path
from io_scene_fbx import parse_fbx, encode_bin, data_types

ROOT = Path('/Users/arieljerickogacilo/mindscape-3d')
SOURCE = Path('/private/tmp/mindscape-updated-npcs/NPC_01_Maya.fbx')
ANIMATION = {b'AnimationStack', b'AnimationLayer', b'AnimationCurveNode', b'AnimationCurve'}


def child(e, name):
    return next(x for x in e.elems if x.id == name)


def model_name(e):
    return e.props[1].split(b'\x00')[0]


def convert(e):
    out = encode_bin.FBXElem(e.id)
    methods = {
        data_types.BOOL: 'add_bool', data_types.CHAR: 'add_char',
        data_types.INT8: 'add_int8', data_types.INT16: 'add_int16',
        data_types.INT32: 'add_int32', data_types.INT64: 'add_int64',
        data_types.FLOAT32: 'add_float32', data_types.FLOAT64: 'add_float64',
        data_types.STRING: 'add_string', data_types.BYTES: 'add_bytes',
        data_types.INT32_ARRAY: 'add_int32_array', data_types.INT64_ARRAY: 'add_int64_array',
        data_types.FLOAT32_ARRAY: 'add_float32_array', data_types.FLOAT64_ARRAY: 'add_float64_array',
        data_types.BOOL_ARRAY: 'add_bool_array', data_types.BYTE_ARRAY: 'add_byte_array',
    }
    for typ, value in zip(e.props_type, e.props):
        getattr(out, methods[typ])(value)
    out.elems = [convert(x) for x in e.elems]
    return out


src, _ = parse_fbx.parse(str(SOURCE))
source_objects = child(src, b'Objects').elems
source_animations = [e for e in source_objects if e.id in ANIMATION]
source_models = {e.props[0]: model_name(e) for e in source_objects if e.id == b'Model'}
# Preview placement belongs to the scene, never to a reusable animation clip.
# Blender may evaluate the rig's saved transform while baking all actions even
# after the exporter temporarily assigns location=(0, 0, 0).
source_connections = child(src, b'Connections').elems
armature_id = next(i for i, name in source_models.items() if name == b'Armature_NPC_01_Maya')
translation_nodes = {c.props[1] for c in source_connections
                     if c.props[2] == armature_id and c.props[0] == b'OP' and c.props[3] == b'Lcl Translation'}
translation_curves = {c.props[1] for c in source_connections if c.props[2] in translation_nodes}
for e in source_animations:
    if e.id == b'AnimationCurve' and e.props[0] in translation_curves:
        values = child(e, b'KeyValueFloat').props[0]
        for i in range(len(values)):
            values[i] = 0.0
        child(e, b'Default').props[0] = 0.0
report = []
for path in sorted((ROOT / 'Assets/Characters/NPCs').rglob('*.fbx')):
    dst, version = parse_fbx.parse(str(path))
    objects = child(dst, b'Objects')
    old_ids = {e.props[0] for e in objects.elems if e.id in ANIMATION}
    dest_models = {model_name(e): e.props[0] for e in objects.elems if e.id == b'Model'}
    rig = next(n for n in dest_models if n.startswith(b'Armature_NPC_'))
    stacks = {model_name(e).split(b'|')[-1]: model_name(e) for e in objects.elems if e.id == b'AnimationStack'}
    next_id = max(e.props[0] for e in objects.elems) + 1
    mapping = {e.props[0]: next_id + i for i, e in enumerate(source_animations)}
    for ident, name in source_models.items():
        if name == b'Armature_NPC_01_Maya':
            name = rig
        elif name == b'Mesh_NPC_01_Maya':
            name = b'Mesh_' + rig.removeprefix(b'Armature_')
        if name in dest_models:
            mapping[ident] = dest_models[name]
    new_objects = []
    for original in source_animations:
        e = copy.deepcopy(original)
        e.props[0] = mapping[e.props[0]]
        if e.id == b'AnimationStack':
            short = model_name(e).split(b'|')[-1]
            name = stacks.get(short, rig + b'|' + short)
            e.props[1] = name + b'\x00\x01AnimStack'
        new_objects.append(e)
    objects.elems[:] = [e for e in objects.elems if e.id not in ANIMATION] + new_objects
    connections = child(dst, b'Connections')
    connections.elems[:] = [e for e in connections.elems if e.props[1] not in old_ids and e.props[2] not in old_ids]
    source_ids = {e.props[0] for e in source_animations}
    for original in child(src, b'Connections').elems:
        if original.props[1] in source_ids or original.props[2] in source_ids:
            e = copy.deepcopy(original)
            e.props[1] = mapping[e.props[1]]
            e.props[2] = mapping[e.props[2]]
            connections.elems.append(e)
    definitions = child(dst, b'Definitions')
    for e in definitions.elems:
        if e.id == b'ObjectType' and e.props[0] in ANIMATION:
            child(e, b'Count').props[0] = sum(x.id == e.props[0] for x in new_objects)
    child(definitions, b'Count').props[0] = len(objects.elems)
    # FBX time unit metadata must match the new 48 FPS sample grid.
    src_settings = child(child(src, b'GlobalSettings'), b'Properties70')
    dst_settings = child(child(dst, b'GlobalSettings'), b'Properties70')
    for p in dst_settings.elems:
        if p.props[0] in (b'TimeMode', b'CustomFrameRate', b'TimeSpanStart', b'TimeSpanStop'):
            p.props[:] = next(q.props[:] for q in src_settings.elems if q.props[0] == p.props[0])
    takes = next((e for e in dst.elems if e.id == b'Takes'), None)
    if takes:
        for take in takes.elems:
            if take.id != b'Take':
                continue
            short = take.props[0].split(b'|')[-1]
            original = next((t for t in child(src, b'Takes').elems if t.id == b'Take' and t.props[0].split(b'|')[-1] == short), None)
            if original:
                for e in take.elems:
                    if e.id in (b'LocalTime', b'ReferenceTime'):
                        e.props[:] = child(original, e.id).props[:]
    encode_bin.write(str(path), convert(dst), version)
    check, _ = parse_fbx.parse(str(path))
    assert len([e for e in child(check, b'Objects').elems if e.id == b'AnimationStack']) == 8
    report.append(str(path.relative_to(ROOT)))
print(json.dumps({'updated_fbx': report}))
