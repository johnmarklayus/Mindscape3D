import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js'
import './style.css'

const presets = {
  boy: { name: 'New Boy NPC', hairStyle: 'default', hat: 'none', eyes: 'default', nose: 'default', mouth: 'default', shirtDesign: 'default', design: '#f4f1e8', skin: '#b95a32', hair: '#4b321c', shirt: '#168b91', shorts: '#575c65', shoes: '#23272e' },
  girl: { name: 'New Girl NPC', hairStyle: 'default', hat: 'none', eyes: 'default', nose: 'default', mouth: 'default', shirtDesign: 'default', design: '#ffffff', skin: '#f6e3d5', hair: '#3e281f', shirt: '#f8adbf', shorts: '#afcddc', shoes: '#d3484d' },
}
const parts = [ ['skin', 'Skin'], ['hair', 'Hair'], ['shirt', 'Shirt'], ['shorts', 'Shorts'], ['shoes', 'Shoes'] ]
const hairstyles = {
  boy: [ ['default', 'Game default'], ['Boy_Hair_1_Crew.glb', 'Crew'], ['Boy_Hair_2_Cornrows.glb', 'Cornrows'], ['Boy_Hair_3_Curly.glb', 'Curly'] ],
  girl: [ ['default', 'Game default'], ['Girl_Hair_1_Long.glb', 'Long'], ['Girl_Hair_2_Bob.glb', 'Bob'], ['Girl_Hair_3_Pigtails.glb', 'Pigtails'] ],
}
// Pieces bound to the head bone, from Blender/Npc-maker (Face, Hats, Hair). The face and hat files fit the boy and the girl.
const pieceSlots = {
  hair: { key: 'hairStyle', dir: 'hair', label: 'hair', options: () => hairstyles[base] },
  hat: { key: 'hat', dir: 'hats', label: 'hat', options: () => [ ['none', 'No hat'], ['Hat_1_Chef.glb', "Chef's hat"], ['Hat_2_Baseball_Cap.glb', 'Baseball cap'], ['Hat_3_Beret.glb', 'Beret'] ] },
  eyes: { key: 'eyes', dir: 'face', label: 'eyes', options: () => [ ['default', 'Game default'], ['Eyes_1_Big.glb', 'Big'], ['Eyes_2_Sleepy.glb', 'Sleepy'], ['Eyes_3_Dot.glb', 'Dot'] ] },
  nose: { key: 'nose', dir: 'face', label: 'nose', options: () => [ ['default', 'Game default'], ['Nose_1_Button.glb', 'Button'], ['Nose_2_Wide.glb', 'Wide'], ['Nose_3_Long.glb', 'Long'] ] },
  shirt: { key: 'shirtDesign', dir: 'shirts', label: 'shirt design', options: () => [ ['default', 'Plain'], ['Shirt_1_Stripes.glb', 'Stripes'], ['Shirt_2_Raglan.glb', 'Raglan'], ['Shirt_3_Ringer.glb', 'Ringer'], ['Shirt_4_Star.glb', 'Star'], ['Shirt_5_Chest_Band.glb', 'Chest band'] ] },
  mouth: { key: 'mouth', dir: 'face', label: 'mouth', options: () => [ ['default', 'Game default'], ['Mouth_1_Grin.glb', 'Grin'], ['Mouth_2_O.glb', 'Surprised'], ['Mouth_3_Smirk.glb', 'Smirk'] ] },
}
const $ = (id) => document.getElementById(id)
let base = 'boy'
let config = { ...presets.boy }
let model = null
let loadToken = 0
const changedParts = new Set()
let animationMode = 'idle'
let animationPlaying = true
let lastFrame = performance.now()
let mixer = null
let activeAction = null
let gameClips = new Map()
const pieceTokens = { hair: 0, hat: 0, eyes: 0, nose: 0, mouth: 0, shirt: 0 }
const addedPieces = { hair: [], hat: [], eyes: [], nose: [], mouth: [], shirt: [] }
let piecesLoading = 0
let originalHair = []
let originalEyes = []
let originalShirts = []
let faceCuts = { nose: [], mouth: [] }
let centerBone = null
const previousCenter = new THREE.Vector3()
const currentCenter = new THREE.Vector3()

const scene = new THREE.Scene()
scene.background = new THREE.Color('#dfe8e4')
const camera = new THREE.PerspectiveCamera(36, 1, 0.01, 100)
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true })
renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
renderer.outputColorSpace = THREE.SRGBColorSpace
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap
$('canvas').appendChild(renderer.domElement)

const controls = new OrbitControls(camera, renderer.domElement)
controls.enableDamping = true
controls.enablePan = false
controls.minDistance = 1.5
controls.maxDistance = 12
controls.maxPolarAngle = Math.PI / 2.03
scene.add(new THREE.HemisphereLight('#ffffff', '#95a39d', 2.4))
const key = new THREE.DirectionalLight('#fff5e8', 3.4)
key.position.set(3, 7, 5)
key.castShadow = true
key.shadow.mapSize.set(1024, 1024)
scene.add(key)
const floor = new THREE.Mesh(new THREE.CircleGeometry(5, 72), new THREE.MeshStandardMaterial({ color: '#d0ded8', roughness: 1 }))
floor.rotation.x = -Math.PI / 2
floor.receiveShadow = true
scene.add(floor)
const grid = new THREE.GridHelper(8, 20, '#a8bfb5', '#c6d5ce')
grid.position.y = 0.005
scene.add(grid)

function resize() {
  const host = $('canvas')
  renderer.setSize(host.clientWidth, host.clientHeight, false)
  camera.aspect = host.clientWidth / Math.max(1, host.clientHeight)
  camera.updateProjectionMatrix()
}
new ResizeObserver(resize).observe($('canvas'))
resize()
function playClip() {
  if (!mixer) return
  if (activeAction) activeAction.stop()
  activeAction = null
  if (animationMode === 'tpose') {
    mixer.update(0)
    $('toggle-animation').disabled = true
    return
  }
  $('toggle-animation').disabled = false
  activeAction = mixer.clipAction(gameClips.get(animationMode))
  activeAction.reset().play()
  activeAction.paused = !animationPlaying
  mixer.update(0)
}

function retargetClip(clip, target) {
  const tracks = clip.tracks.flatMap((track) => {
    const separator = track.name.lastIndexOf('.')
    if (separator < 0) return []
    const nodeName = track.name.slice(0, separator)
    const property = track.name.slice(separator + 1)
    const node = target.getObjectByName(nodeName)
    if (!node) return []
    const copy = track.clone()
    copy.name = `${node.uuid}.${property}`
    return [copy]
  })
  return new THREE.AnimationClip(clip.name, clip.duration, tracks)
}

function draw(now) {
  requestAnimationFrame(draw)
  const delta = Math.min((now - lastFrame) / 1000, 0.1)
  lastFrame = now
  if (animationPlaying && mixer) mixer.update(delta)
  if (centerBone) {
    model.updateMatrixWorld(true)
    centerBone.getWorldPosition(currentCenter)
    const movement = currentCenter.sub(previousCenter)
    camera.position.add(movement)
    controls.target.add(movement)
    previousCenter.add(movement)
  }
  controls.update()
  renderer.render(scene, camera)
}
requestAnimationFrame(draw)

function partFor(name) {
  const n = name.toLowerCase()
  if (/skin|ear inner|seam/.test(n)) return 'skin'
  if (/band|hair_tie/.test(n)) return null
  if (/hair|ponytail/.test(n)) return 'hair'
  if (/shirt/.test(n)) return 'shirt'
  if (/shorts/.test(n)) return 'shorts'
  if (/boots|shoes|soles/.test(n)) return 'shoes'
  return null
}

function applyAppearance() {
  if (!model) return
  model.traverse((object) => {
    if (!object.isMesh) return
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      const part = partFor(material.name)
      if (part && changedParts.has(part) && material.color && !material.userData.designMask) material.color.set(config[part])
    }
  })
  paintShirtDesigns()
}

// A shirt design carries a black-and-white mask (white = the design). It is painted with the shirt colour and the
// design colour into a texture, so the exported GLB keeps the design.
function paintShirtDesigns() {
  for (const mesh of addedPieces.shirt) {
    const material = mesh.material
    const mask = material.userData.designMask
    if (!mask) continue
    const canvas = material.userData.canvas || document.createElement('canvas')
    canvas.width = mask.width; canvas.height = mask.height
    const context = canvas.getContext('2d', { willReadFrequently: true })
    context.drawImage(mask, 0, 0)
    const image = context.getImageData(0, 0, canvas.width, canvas.height)
    const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16))   // the canvas is sRGB, like the pickers
    const b = rgb(config.shirt), d = rgb(config.design)
    const px = image.data
    for (let i = 0; i < px.length; i += 4) {
      const t = px[i] / 255
      px[i] = b[0] + (d[0] - b[0]) * t; px[i + 1] = b[1] + (d[1] - b[1]) * t; px[i + 2] = b[2] + (d[2] - b[2]) * t; px[i + 3] = 255
    }
    context.putImageData(image, 0, 0)
    if (!material.userData.canvas) {
      material.userData.canvas = canvas
      const texture = new THREE.CanvasTexture(canvas)
      texture.flipY = false
      texture.colorSpace = THREE.SRGBColorSpace
      material.map = texture
      material.color.set('#ffffff')
      material.needsUpdate = true
    } else material.map.needsUpdate = true
  }
}

function frameModel() {
  if (!model) return
  model.updateMatrixWorld(true)
  const box = new THREE.Box3().setFromObject(model)
  const center = box.getCenter(new THREE.Vector3())
  const size = box.getSize(new THREE.Vector3())
  const radius = Math.max(size.y, size.x * 1.8, 1)
  controls.target.set(center.x, center.y, center.z)
  camera.position.set(center.x + radius * 0.8, center.y + radius * 0.35, center.z + radius * 1.55)
  if (centerBone) centerBone.getWorldPosition(previousCenter)
  controls.update()
}

function centerOnModel() {
  if (!model) return
  model.updateMatrixWorld(true)
  const center = new THREE.Box3().setFromObject(model).getCenter(new THREE.Vector3())
  camera.position.add(center.clone().sub(controls.target))
  controls.target.copy(center)
  if (centerBone) centerBone.getWorldPosition(previousCenter)
  controls.update()
}

function disposeModel(root) {
  root.traverse((object) => {
    if (!object.isMesh) return
    object.geometry.dispose()
    for (const mat of Array.isArray(object.material) ? object.material : [object.material]) mat.dispose()
  })
}

function clearPiece(slot) {
  for (const mesh of addedPieces[slot]) {
    mesh.removeFromParent()
    mesh.geometry.dispose()
    for (const material of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) if (!material.userData.shared) material.dispose()
  }
  addedPieces[slot] = []
}

// The default face is part of the game model: the eyes are their own meshes, but the nose sits in the skin and the
// mouth shares a mesh with the brows, so those are hidden by leaving their triangles out of the index.
// Positions are measured from the head bone in Blender's axes (x right, y back, z up), the space the pieces are built in.
function headSpace(mesh) {
  const head = mesh.skeleton.bones.findIndex((bone) => bone.name === 'head')
  if (head < 0) return null
  const toHead = mesh.skeleton.boneInverses[head].clone().multiply(mesh.bindMatrix)
  const scale = 1 / new THREE.Vector3().setFromMatrixScale(toHead.clone().invert()).x
  const position = mesh.geometry.attributes.position
  const v = new THREE.Vector3()
  return (i) => {
    v.fromBufferAttribute(position, i).applyMatrix4(toHead).multiplyScalar(scale)
    return { x: v.x, y: -v.z, z: v.y }   // bone Y points up the head, bone Z faces forward
  }
}
function prepareFaceCut(mesh, test) {
  const at = headSpace(mesh)
  const geometry = mesh.geometry
  if (!at || !geometry.index) return null
  const index = geometry.index.array
  const kept = []
  let removed = 0
  for (let t = 0; t < index.length; t += 3) {
    if (test([at(index[t]), at(index[t + 1]), at(index[t + 2])])) { removed++; continue }
    kept.push(index[t], index[t + 1], index[t + 2])
  }
  if (!removed) return null
  return { geometry, full: geometry.index, cut: new THREE.BufferAttribute(new (index.constructor)(kept), 1), removed }
}
const isDefaultNose = (tri) => tri.every((v) => Math.abs(v.x) < 0.0285 && v.z > 0.16 && v.z < 0.24) && Math.min(...tri.map((v) => v.y)) < -0.37
const isDefaultMouth = (tri) => tri.every((v) => v.z < 0.2 && v.y < -0.25)
function showDefaultPiece(slot, visible) {
  if (slot === 'hair') for (const mesh of originalHair) mesh.visible = visible
  if (slot === 'eyes') for (const mesh of originalEyes) mesh.visible = visible
  if (slot === 'shirt') for (const mesh of originalShirts) mesh.visible = visible
  for (const cut of faceCuts[slot] || []) cut.geometry.setIndex(visible ? cut.full : cut.cut)
}
function skinMaterial() {
  let found
  model.traverse((object) => {
    if (found || !object.isMesh) return
    for (const material of Array.isArray(object.material) ? object.material : [object.material])
      if (!found && partFor(material.name) === 'skin' && !/seam|ear inner/i.test(material.name)) found = material
  })
  return found
}
function updateExportButton() { $('export-glb').disabled = !model || piecesLoading > 0 }

function loadPiece(slot) {
  const { key, dir, label } = pieceSlots[slot]
  const token = ++pieceTokens[slot]
  clearPiece(slot)
  if (!model) return
  showDefaultPiece(slot, true)
  const file = config[key]
  if (file === 'default' || file === 'none') return
  const selectedModel = model
  $('status').textContent = `Loading ${label}…`
  piecesLoading++
  updateExportButton()
  const done = (message) => { piecesLoading = Math.max(0, piecesLoading - 1); if (message) $('status').textContent = message; updateExportButton() }
  new GLTFLoader().load(`/models/${dir}/${file}`, (gltf) => {
    if (token !== pieceTokens[slot] || selectedModel !== model) { disposeModel(gltf.scene); done(''); return }
    const sourceMeshes = []
    gltf.scene.traverse((object) => { if (object.isSkinnedMesh) sourceMeshes.push(object) })
    const gameSkinnedMesh = (() => { let found; model.traverse((object) => { if (!found && object.isSkinnedMesh) found = object }); return found })()
    if (!gameSkinnedMesh || !sourceMeshes.length) { disposeModel(gltf.scene); done(`The ${label} does not fit this model`); return }
    const gameSkeleton = gameSkinnedMesh.skeleton
    const rigRoot = gameSkeleton.bones[0].parent
    const skin = skinMaterial()
    for (const mesh of sourceMeshes) {
      const bones = mesh.skeleton.bones.map((bone) => gameSkeleton.bones.find((gameBone) => gameBone.name === bone.name))
      if (bones.some((bone) => !bone)) continue
      const inverseMatrices = mesh.skeleton.boneInverses.map((matrix) => matrix.clone())
      mesh.removeFromParent()
      rigRoot.add(mesh)
      mesh.bind(new THREE.Skeleton(bones, inverseMatrices), mesh.bindMatrix.clone())
      mesh.castShadow = true
      // A nose uses the character's own skin material, so it matches and follows the skin colour.
      if (skin && !Array.isArray(mesh.material) && /skin/i.test(mesh.material.name)) { mesh.material.dispose(); mesh.material = skin; skin.userData.shared = true }
      if (slot === 'shirt' && mesh.material.map) mesh.material.userData.designMask = mesh.material.map.image
      addedPieces[slot].push(mesh)
    }
    disposeModel(gltf.scene)
    if (!addedPieces[slot].length) { done(`The ${label} rig did not match the game model`); return }
    showDefaultPiece(slot, false)
    applyAppearance()
    done(`${label[0].toUpperCase() + label.slice(1)} ready`)
  }, undefined, (error) => {
    if (token !== pieceTokens[slot]) return
    console.error(error)
    done(`The ${label} failed to load`)
  })
}
function loadPieces() { for (const slot of Object.keys(pieceSlots)) loadPiece(slot) }

function loadModel() {
  const token = ++loadToken
  for (const slot of Object.keys(pieceSlots)) { pieceTokens[slot]++; clearPiece(slot) }
  piecesLoading = 0
  $('status').textContent = 'Loading model…'
  $('export-glb').disabled = true
  if (mixer) { mixer.stopAllAction(); mixer.uncacheRoot(model); mixer = null }
  if (model) { scene.remove(model); disposeModel(model); model = null }
  originalHair = []
  originalEyes = []
  originalShirts = []
  faceCuts = { nose: [], mouth: [] }
  centerBone = null
  gameClips = new Map()
  new GLTFLoader().load(`/models/${base}-default.glb`, (gltf) => {
    if (token !== loadToken) { disposeModel(gltf.scene); return }
    model = gltf.scene
    model.name = 'NPC_Root'
    centerBone = model.getObjectByName('hips') || model.getObjectByName('root') || model
    model.traverse((object) => {
      if (object.isMesh && (Array.isArray(object.material) ? object.material : [object.material]).every((material) => /hair|ponytail/i.test(material.name))) originalHair.push(object)
      if (object.isMesh && !Array.isArray(object.material) && /(^|_)Eyes\b|catchlights/i.test(object.material.name)) originalEyes.push(object)
      if (object.isMesh && !Array.isArray(object.material) && partFor(object.material.name) === 'shirt') originalShirts.push(object)
    })
    model.updateMatrixWorld(true)
    model.traverse((object) => {
      if (!object.isSkinnedMesh || Array.isArray(object.material)) return
      const name = object.material.name
      const cut = partFor(name) === 'skin' && !/seam|ear inner/i.test(name) ? ['nose', isDefaultNose] : /smile and brows/i.test(name) ? ['mouth', isDefaultMouth] : null
      const prepared = cut && prepareFaceCut(object, cut[1])
      if (prepared) faceCuts[cut[0]].push(prepared)
    })
    model.traverse((object) => { if (object.isMesh) object.castShadow = true })
    const originalColors = new Map()
    model.traverse((object) => {
      if (!object.isMesh) return
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        const part = partFor(material.name)
        if (part && material.color && !originalColors.has(part) && !/seam|ear inner|soles|band/i.test(material.name))
          originalColors.set(part, `#${material.color.getHexString()}`)
      }
    })
    for (const [part, color] of originalColors) config[part] = color
    syncControls()
    scene.add(model)
    applyAppearance()
    frameModel()
    loadPieces()
    $('status').textContent = 'Loading game animations…'
    updateExportButton()
    new GLTFLoader().load(`/models/${base}-animations.glb`, (animationFile) => {
      if (token !== loadToken) { disposeModel(animationFile.scene); return }
      for (const clip of animationFile.animations) {
        const mapped = retargetClip(clip, model)
        if (mapped.tracks.length) gameClips.set(clip.name.toLowerCase(), mapped)
      }
      disposeModel(animationFile.scene)
      if (gameClips.size < 4) {
        $('status').textContent = 'Some game clips are missing'
        return
      }
      mixer = new THREE.AnimationMixer(model)
      playClip()
      // The imported boy clip changes the rig's authored offset on its first frame.
      // Frame the animated pose after that change, not the unanimated GLB pose.
      frameModel()
      $('status').textContent = 'Game animations ready'
    }, undefined, (error) => {
      if (token !== loadToken) return
      console.error(error)
      $('status').textContent = 'Game animations failed to load'
    })
  }, undefined, (error) => {
    if (token !== loadToken) return
    console.error(error)
    $('status').textContent = 'Model failed to load'
  })
}

function syncControls() {
  $('name').value = config.name
  $('base-model-label').textContent = base === 'boy' ? 'Boy' : 'Girl'
  for (const [slot, { key, options }] of Object.entries(pieceSlots))
    $(`${slot}-label`).textContent = options().find(([value]) => value === config[key])?.[1] || options()[0][1]
  for (const [key] of parts) {
    $(`color-${key}`).value = config[key]
    $(`value-${key}`).textContent = config[key].toUpperCase()
  }
  $('color-design').value = config.design
  $('value-design').textContent = config.design.toUpperCase()
  $('model-label').textContent = `DEFAULT ${base.toUpperCase()}`
  applyAppearance()
}

$('colors').innerHTML = parts.map(([key, label]) => `<label class="color-row" for="color-${key}"><span>${label}</span><span class="color-control"><span id="value-${key}"></span><input id="color-${key}" type="color" aria-label="${label} color"></span></label>`).join('')
for (const [key] of parts) $('color-' + key).addEventListener('input', (event) => {
  config[key] = event.target.value
  changedParts.add(key)
  $('value-' + key).textContent = config[key].toUpperCase()
  applyAppearance()
})
$('color-design').addEventListener('input', (event) => {
  config.design = event.target.value
  $('value-design').textContent = config.design.toUpperCase()
  paintShirtDesigns()
})
$('name').addEventListener('input', (event) => { config.name = event.target.value })
function stepPiece(slot, direction) {
  const { key, options } = pieceSlots[slot]
  const list = options()
  const current = list.findIndex(([value]) => value === config[key])
  config[key] = list[(current + direction + list.length) % list.length][0]
  $(`${slot}-label`).textContent = list.find(([value]) => value === config[key])[1]
  loadPiece(slot)
}
for (const slot of Object.keys(pieceSlots)) {
  $(`previous-${slot}`).addEventListener('click', () => stepPiece(slot, -1))
  $(`next-${slot}`).addEventListener('click', () => stepPiece(slot, 1))
}
function stepModel() {
  base = base === 'boy' ? 'girl' : 'boy'
  changedParts.clear()
  config = { ...presets[base] }
  syncControls()
  loadModel()
}
$('previous-model').addEventListener('click', stepModel)
$('next-model').addEventListener('click', stepModel)
$('reset-character').addEventListener('click', () => { changedParts.clear(); config = { ...presets[base] }; syncControls(); loadModel() })
$('reset-view').addEventListener('click', frameModel)
document.querySelectorAll('.animation-mode').forEach((button) => button.addEventListener('click', () => {
  animationMode = button.dataset.animation
  document.querySelectorAll('.animation-mode').forEach((item) => item.classList.toggle('active', item === button))
  if (mixer && (animationMode === 'tpose' || gameClips.has(animationMode))) { playClip(); centerOnModel() }
}))
$('toggle-animation').addEventListener('click', () => {
  animationPlaying = !animationPlaying
  $('toggle-animation').textContent = animationPlaying ? 'Ⅱ' : '▶'
  $('toggle-animation').setAttribute('aria-label', animationPlaying ? 'Pause animation' : 'Play animation')
  if (activeAction) activeAction.paused = !animationPlaying
})

function download(data, type, extension) {
  const filename = (config.name.trim() || 'New NPC').replace(/[^a-z0-9-_]+/gi, '-')
  const url = URL.createObjectURL(new Blob([data], { type }))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `${filename}.${extension}`
  anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
$('export-json').addEventListener('click', () => download(JSON.stringify({ format: 'mindscape-npc', version: 3, baseModel: base, ...config }, null, 2), 'application/json', 'npc.json'))
$('export-glb').addEventListener('click', async () => {
  if (!model) return
  $('export-glb').disabled = true
  $('status').textContent = 'Exporting…'
  const wasPlaying = animationPlaying
  animationPlaying = false
  try {
    if (activeAction) activeAction.stop()
    const data = await new GLTFExporter().parseAsync(model, { binary: true, onlyVisible: true })
    download(data, 'model/gltf-binary', 'glb')
    $('status').textContent = 'Model exported'
  } catch (error) {
    console.error(error)
    $('status').textContent = 'Export failed'
  } finally { animationPlaying = wasPlaying; if (mixer) playClip(); updateExportButton() }
})

syncControls()
loadModel()
