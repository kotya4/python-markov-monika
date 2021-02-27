import bpy
import json

data = { o.name : { k : o[k] for k in o.keys() if k not in '_RNA_UI' } for o in bpy.data.objects if o.type not in ('CAMERA', 'LAMP', 'ARMATURE') }

with open(bpy.data.filepath + '__' + 'props.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


