import bpy
scene = bpy.data.scenes['House_Room_Shell']
bpy.context.window.scene = scene
scene.display.shading.show_shadows = False
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.show_shadows = False
            area.spaces.active.shading.show_cavity = True
scene.camera = bpy.data.objects['House_Camera_Overview']
scene.render.filepath = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/house-shell-preview.png'
bpy.ops.render.render(write_still=True)
scene.camera = bpy.data.objects['House_Camera_Floor_Plan']
scene.render.filepath = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/house-floor-plan.png'
bpy.ops.render.render(write_still=True)
scene.camera = bpy.data.objects['House_Camera_Overview']
scene.render.filepath = '/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/house-shell-preview.png'
bpy.ops.wm.save_as_mainfile(filepath='/Users/arieljerickogacilo/mindscape-3d/GeneratedAssets/house-shell.blend')
result = {'saved': bpy.data.filepath}
