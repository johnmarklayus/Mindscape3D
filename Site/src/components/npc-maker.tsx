"use client"

import {
  Box,
  Button,
  Field,
  Flex,
  Heading,
  Input,
  NativeSelect,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useCallback, useEffect, useRef, useState } from "react"
import { LuDownload, LuFileJson, LuRotateCcw } from "react-icons/lu"
import * as THREE from "three"
import { GLTFExporter } from "three/examples/jsm/exporters/GLTFExporter.js"
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js"
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js"

type AnimationName = "Idle" | "Walk" | "Run" | "Wave"

type NpcConfig = {
  name: string
  baseModel: "Boy" | "Girl"
  hair: "Short" | "Bob" | "Spiky" | "Bun"
  top: "T-shirt" | "Polo" | "Hoodie" | "Jacket"
  bottom: "Shorts" | "Trousers" | "Skirt"
  shoes: "Sneakers" | "Boots" | "Loafers"
  skinColor: string
  hairColor: string
  topColor: string
  bottomColor: string
  shoeColor: string
}

type Rig = {
  root: THREE.Group
  leftArm: THREE.Group
  rightArm: THREE.Group
  leftLeg: THREE.Group
  rightLeg: THREE.Group
}

const defaults: NpcConfig = {
  name: "New Boy NPC",
  baseModel: "Boy",
  hair: "Short",
  top: "T-shirt",
  bottom: "Shorts",
  shoes: "Sneakers",
  skinColor: "#b95a32",
  hairColor: "#4b321c",
  topColor: "#168b91",
  bottomColor: "#575c65",
  shoeColor: "#23272e",
}

const girlDefaults: NpcConfig = {
  ...defaults,
  name: "New Girl NPC",
  baseModel: "Girl",
  skinColor: "#f6e3d5",
  hairColor: "#3e281f",
  topColor: "#f8adbf",
  bottomColor: "#afcddc",
  shoeColor: "#d3484d",
}

function recolorModel(root: THREE.Object3D, config: NpcConfig) {
  root.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return
    const materials = Array.isArray(object.material) ? object.material : [object.material]
    for (const mat of materials) {
      if (!(mat instanceof THREE.MeshStandardMaterial)) continue
      const name = mat.name.toLowerCase()
      const color = /skin|ear inner|seam/.test(name) ? config.skinColor
        : /hair|ponytail/.test(name) ? config.hairColor
        : /shirt/.test(name) ? config.topColor
        : /shorts/.test(name) ? config.bottomColor
        : /boots|shoes|soles/.test(name) ? config.shoeColor : null
      if (color) mat.color.set(color)
    }
  })
}

const skinTones = ["#f2c7a5", "#dfad83", "#c98f68", "#a96f4e", "#825039", "#5b382b"]
const hairColors = ["#211814", "#3a261d", "#6c4027", "#a96d3c", "#d5b36a", "#7c3044"]
const clothingColors = ["#4d8e8a", "#315f8c", "#8d4b57", "#bf7c3f", "#67734c", "#e9e2d3", "#272a31"]

function material(color: string, roughness = 0.82) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness: 0.02 })
}

function mesh(
  geometry: THREE.BufferGeometry,
  mat: THREE.Material,
  position: [number, number, number],
  scale?: [number, number, number],
) {
  const item = new THREE.Mesh(geometry, mat)
  item.position.set(...position)
  if (scale) item.scale.set(...scale)
  item.castShadow = true
  item.receiveShadow = true
  return item
}

function buildCharacter(config: NpcConfig): Rig {
  const root = new THREE.Group()
  root.name = "NPC_Root"
  const skin = material(config.skinColor)
  const hair = material(config.hairColor)
  const top = material(config.topColor)
  const bottom = material(config.bottomColor)
  const shoes = material(config.shoeColor, 0.58)
  const dark = material("#252930")

  const torsoWidth = config.top === "Hoodie" ? 1.28 : 1.16
  root.add(mesh(new THREE.BoxGeometry(torsoWidth, 1.2, 0.66), top, [0, 2.05, 0]))
  root.add(mesh(new THREE.CylinderGeometry(0.24, 0.26, 0.22, 16), skin, [0, 2.77, 0]))
  root.add(mesh(new THREE.SphereGeometry(0.52, 24, 18), skin, [0, 3.22, 0]))

  // Simple face details make front/back orientation obvious in the preview and exported model.
  root.add(mesh(new THREE.SphereGeometry(0.045, 12, 8), dark, [-0.18, 3.3, 0.48]))
  root.add(mesh(new THREE.SphereGeometry(0.045, 12, 8), dark, [0.18, 3.3, 0.48]))
  root.add(mesh(new THREE.BoxGeometry(0.18, 0.025, 0.025), dark, [0, 3.08, 0.515]))

  const leftArm = new THREE.Group()
  leftArm.name = "Arm_L"
  leftArm.position.set(-0.72, 2.55, 0)
  leftArm.add(mesh(new THREE.CapsuleGeometry(0.16, 0.72, 6, 12), skin, [0, -0.5, 0]))
  leftArm.add(mesh(new THREE.BoxGeometry(0.35, 0.45, 0.5), top, [0, -0.17, 0]))
  root.add(leftArm)

  const rightArm = new THREE.Group()
  rightArm.name = "Arm_R"
  rightArm.position.set(0.72, 2.55, 0)
  rightArm.add(mesh(new THREE.CapsuleGeometry(0.16, 0.72, 6, 12), skin, [0, -0.5, 0]))
  rightArm.add(mesh(new THREE.BoxGeometry(0.35, 0.45, 0.5), top, [0, -0.17, 0]))
  root.add(rightArm)

  const leftLeg = new THREE.Group()
  leftLeg.name = "Leg_L"
  leftLeg.position.set(-0.31, 1.48, 0)
  const rightLeg = new THREE.Group()
  rightLeg.name = "Leg_R"
  rightLeg.position.set(0.31, 1.48, 0)

  const legMat = config.bottom === "Shorts" || config.bottom === "Skirt" ? skin : bottom
  leftLeg.add(mesh(new THREE.CapsuleGeometry(0.21, 0.72, 6, 12), legMat, [0, -0.56, 0]))
  rightLeg.add(mesh(new THREE.CapsuleGeometry(0.21, 0.72, 6, 12), legMat, [0, -0.56, 0]))
  root.add(leftLeg, rightLeg)

  if (config.bottom === "Skirt") {
    root.add(mesh(new THREE.CylinderGeometry(0.55, 0.72, 0.78, 18), bottom, [0, 1.45, 0]))
  } else {
    const height = config.bottom === "Shorts" ? 0.52 : 0.92
    root.add(mesh(new THREE.BoxGeometry(0.55, height, 0.61), bottom, [-0.3, 1.47 - height / 2, 0]))
    root.add(mesh(new THREE.BoxGeometry(0.55, height, 0.61), bottom, [0.3, 1.47 - height / 2, 0]))
  }

  const shoeHeight = config.shoes === "Boots" ? 0.48 : 0.24
  const shoeDepth = config.shoes === "Loafers" ? 0.72 : 0.78
  leftLeg.add(mesh(new THREE.BoxGeometry(0.5, shoeHeight, shoeDepth), shoes, [0, -1.12 + shoeHeight / 2, 0.12]))
  rightLeg.add(mesh(new THREE.BoxGeometry(0.5, shoeHeight, shoeDepth), shoes, [0, -1.12 + shoeHeight / 2, 0.12]))

  if (config.hair === "Short") {
    root.add(mesh(new THREE.SphereGeometry(0.54, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), hair, [0, 3.27, 0]))
  } else if (config.hair === "Bob") {
    root.add(mesh(new THREE.SphereGeometry(0.56, 24, 16), hair, [0, 3.32, -0.05], [1, 0.82, 0.98]))
    root.add(mesh(new THREE.BoxGeometry(1.02, 0.6, 0.42), hair, [0, 3.03, -0.18]))
  } else if (config.hair === "Spiky") {
    root.add(mesh(new THREE.SphereGeometry(0.53, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), hair, [0, 3.28, 0]))
    for (let i = -2; i <= 2; i++) {
      const spike = mesh(new THREE.ConeGeometry(0.14, 0.45, 10), hair, [i * 0.2, 3.78 - Math.abs(i) * 0.04, -0.02])
      spike.rotation.z = i * 0.12
      root.add(spike)
    }
  } else {
    root.add(mesh(new THREE.SphereGeometry(0.54, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), hair, [0, 3.27, 0]))
    root.add(mesh(new THREE.SphereGeometry(0.25, 18, 12), hair, [0, 3.74, -0.18]))
  }

  if (config.top === "Polo") {
    root.add(mesh(new THREE.BoxGeometry(0.28, 0.28, 0.08), material("#f3efe7"), [-0.16, 2.58, 0.37]))
    root.add(mesh(new THREE.BoxGeometry(0.28, 0.28, 0.08), material("#f3efe7"), [0.16, 2.58, 0.37]))
  } else if (config.top === "Hoodie") {
    const hood = mesh(new THREE.TorusGeometry(0.38, 0.12, 10, 24, Math.PI), top, [0, 2.68, -0.22])
    hood.rotation.x = Math.PI / 2
    root.add(hood)
  } else if (config.top === "Jacket") {
    root.add(mesh(new THREE.BoxGeometry(0.05, 1.08, 0.05), material("#eee8dc"), [0, 2.04, 0.36]))
  }

  return { root, leftArm, rightArm, leftLeg, rightLeg }
}

function disposeCharacter(root: THREE.Object3D) {
  root.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return
    object.geometry.dispose()
    const mats = Array.isArray(object.material) ? object.material : [object.material]
    mats.forEach((item) => item.dispose())
  })
}

function animationClips() {
  const track = (target: string, times: number[], values: number[]) => new THREE.NumberKeyframeTrack(target, times, values)
  return [
    new THREE.AnimationClip("Idle", 2, [
      track("NPC_Root.position[y]", [0, 1, 2], [0, 0.035, 0]),
      track("Arm_L.rotation[z]", [0, 1, 2], [0.04, 0.08, 0.04]),
      track("Arm_R.rotation[z]", [0, 1, 2], [-0.04, -0.08, -0.04]),
    ]),
    new THREE.AnimationClip("Walk", 1, [
      track("Arm_L.rotation[x]", [0, 0.25, 0.5, 0.75, 1], [-0.55, 0, 0.55, 0, -0.55]),
      track("Arm_R.rotation[x]", [0, 0.25, 0.5, 0.75, 1], [0.55, 0, -0.55, 0, 0.55]),
      track("Leg_L.rotation[x]", [0, 0.25, 0.5, 0.75, 1], [0.45, 0, -0.45, 0, 0.45]),
      track("Leg_R.rotation[x]", [0, 0.25, 0.5, 0.75, 1], [-0.45, 0, 0.45, 0, -0.45]),
    ]),
    new THREE.AnimationClip("Run", 0.65, [
      track("Arm_L.rotation[x]", [0, 0.325, 0.65], [-0.9, 0.9, -0.9]),
      track("Arm_R.rotation[x]", [0, 0.325, 0.65], [0.9, -0.9, 0.9]),
      track("Leg_L.rotation[x]", [0, 0.325, 0.65], [0.75, -0.75, 0.75]),
      track("Leg_R.rotation[x]", [0, 0.325, 0.65], [-0.75, 0.75, -0.75]),
    ]),
    new THREE.AnimationClip("Wave", 1.2, [
      track("Arm_R.rotation[z]", [0, 0.2, 0.45, 0.7, 0.95, 1.2], [0, -2.65, -2.25, -2.65, -2.25, 0]),
    ]),
  ]
}

function NpcPreview({ config, animation, onReady }: { config: NpcConfig; animation: AnimationName; onReady: (rig: Rig | null) => void }) {
  const hostRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const rigRef = useRef<Rig | null>(null)
  const animationRef = useRef<AnimationName>(animation)
  const configRef = useRef(config)

  useEffect(() => {
    animationRef.current = animation
  }, [animation])

  useEffect(() => {
    configRef.current = config
    if (rigRef.current) recolorModel(rigRef.current.root, config)
  }, [config])

  useEffect(() => {
    const host = hostRef.current
    if (!host) return
    const scene = new THREE.Scene()
    scene.background = new THREE.Color("#edf3f1")
    sceneRef.current = scene
    const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100)
    camera.position.set(5.4, 3.3, 7.6)
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    renderer.outputColorSpace = THREE.SRGBColorSpace
    host.appendChild(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.target.set(0, 1.4, 0)
    controls.enableDamping = true
    controls.minDistance = 4.5
    controls.maxDistance = 12
    controls.maxPolarAngle = Math.PI / 2.02
    controls.update()

    scene.add(new THREE.HemisphereLight("#ffffff", "#9aa7a2", 2.2))
    const sun = new THREE.DirectionalLight("#fff7e8", 3.2)
    sun.position.set(4, 8, 5)
    sun.castShadow = true
    sun.shadow.mapSize.set(1024, 1024)
    scene.add(sun)
    const floor = new THREE.Mesh(new THREE.CircleGeometry(5.4, 64), new THREE.MeshStandardMaterial({ color: "#dce8e4", roughness: 1 }))
    floor.rotation.x = -Math.PI / 2
    floor.position.y = -0.02
    floor.receiveShadow = true
    scene.add(floor)
    const grid = new THREE.GridHelper(8, 16, "#b4c7c0", "#cedbd6")
    grid.position.y = 0.005
    scene.add(grid)

    const resize = () => {
      const width = host.clientWidth
      const height = host.clientHeight
      renderer.setSize(width, height, false)
      camera.aspect = width / Math.max(height, 1)
      camera.updateProjectionMatrix()
    }
    const observer = new ResizeObserver(resize)
    observer.observe(host)
    resize()

    let frame = 0
    const clock = new THREE.Clock()
    const render = () => {
      clock.getElapsedTime()
      controls.update()
      renderer.render(scene, camera)
      frame = requestAnimationFrame(render)
    }
    render()

    return () => {
      cancelAnimationFrame(frame)
      observer.disconnect()
      controls.dispose()
      if (rigRef.current) disposeCharacter(rigRef.current.root)
      renderer.dispose()
      renderer.domElement.remove()
      sceneRef.current = null
      rigRef.current = null
      onReady(null)
    }
  }, [onReady])

  useEffect(() => {
    const scene = sceneRef.current
    if (!scene) return
    let active = true
    if (rigRef.current) {
      scene.remove(rigRef.current.root)
      disposeCharacter(rigRef.current.root)
      rigRef.current = null
    }
    onReady(null)
    new GLTFLoader().load(`/models/npc-maker/${config.baseModel.toLowerCase()}-default.glb`, (gltf) => {
      if (!active) { disposeCharacter(gltf.scene); return }
      const root = gltf.scene
      root.name = "NPC_Root"
      root.traverse((object) => { if (object instanceof THREE.Mesh) object.castShadow = true })
      recolorModel(root, configRef.current)
      const next = { root, leftArm: new THREE.Group(), rightArm: new THREE.Group(), leftLeg: new THREE.Group(), rightLeg: new THREE.Group() }
      rigRef.current = next
      scene.add(root)
      onReady(next)
    })
    return () => { active = false }
  }, [config.baseModel, onReady])

  return <Box ref={hostRef} position="absolute" inset="0" aria-label="Interactive 3D NPC preview" />
}

function ChoiceField<T extends string>({ label, value, options, onChange }: { label: string; value: T; options: readonly T[]; onChange: (value: T) => void }) {
  return (
    <Field.Root>
      <Field.Label color="#34413d" fontSize="sm" fontWeight="700">
        {label}
      </Field.Label>
      <NativeSelect.Root>
        <NativeSelect.Field
          value={value}
          onChange={(event) => onChange(event.currentTarget.value as T)}
          bg="white"
          borderColor="#cbd7d2"
          color="#19231f"
        >
          {options.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </NativeSelect.Field>
        <NativeSelect.Indicator color="#52645d" />
      </NativeSelect.Root>
    </Field.Root>
  )
}

function ColorRow({ label, value, colors, onChange }: { label: string; value: string; colors: string[]; onChange: (value: string) => void }) {
  return (
    <Stack gap="2">
      <Text color="#34413d" fontSize="sm" fontWeight="700">
        {label}
      </Text>
      <Flex gap="2" flexWrap="wrap">
        {colors.map((color) => (
          <Button
            type="button"
            key={color}
            aria-label={`Use ${color} for ${label}`}
            onClick={() => onChange(color)}
            w="30px"
            h="30px"
            minW="30px"
            p="0"
            rounded="full"
            bg={color}
            border="3px solid"
            borderColor={value === color ? "#166b57" : "white"}
            boxShadow={value === color ? "0 0 0 2px #8eb9ad" : "0 0 0 1px #bdcbc6"}
            transition="transform 120ms ease"
            _hover={{ transform: "scale(1.08)" }}
          />
        ))}
        <Input
          aria-label={`Custom ${label}`}
          type="color"
          value={value}
          onChange={(event) => onChange(event.currentTarget.value)}
          p="1"
          w="42px"
          h="32px"
          bg="white"
          borderColor="#bdcbc6"
          cursor="pointer"
        />
      </Flex>
    </Stack>
  )
}

function downloadBlob(data: BlobPart, type: string, filename: string) {
  const url = URL.createObjectURL(new Blob([data], { type }))
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = filename
  anchor.click()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export function NpcMaker() {
  const [config, setConfig] = useState<NpcConfig>(defaults)
  const [animation, setAnimation] = useState<AnimationName>("Idle")
  const [exporting, setExporting] = useState(false)
  const rigRef = useRef<Rig | null>(null)
  const onRigReady = useCallback((rig: Rig | null) => {
    rigRef.current = rig
  }, [])

  const update = <K extends keyof NpcConfig>(key: K, value: NpcConfig[K]) => setConfig((current) => ({ ...current, [key]: value }))
  const filename = (config.name.trim() || "New NPC").replace(/[^a-z0-9-_]+/gi, "-")

  const exportRecipe = () => {
    downloadBlob(JSON.stringify({ format: "mindscape-npc", version: 1, ...config }, null, 2), "application/json", `${filename}.npc.json`)
  }

  const exportGlb = async () => {
    const rig = rigRef.current
    if (!rig) return
    setExporting(true)
    try {
      const exporter = new GLTFExporter()
      const result = await exporter.parseAsync(rig.root, { binary: true, onlyVisible: true })
      downloadBlob(result as ArrayBuffer, "model/gltf-binary", `${filename}.glb`)
    } finally {
      setExporting(false)
    }
  }

  return (
    <Box as="main" minH="100svh" bg="#f5f7f6" color="#19231f" style={{ colorScheme: "light" }}>
      <Flex
        as="header"
        minH="68px"
        px={{ base: "4", md: "7" }}
        py="3"
        align="center"
        justify="space-between"
        gap="4"
        bg="white"
        borderBottom="1px solid #dce4e1"
      >
        <Box>
          <Flex align="center" gap="3">
            <Heading as="h1" fontFamily="body" fontSize={{ base: "lg", md: "xl" }} color="#17211e">
              MindScape NPC Maker
            </Heading>
          </Flex>
          <Text display={{ base: "none", md: "block" }} color="#66756f" fontSize="sm">
            Customize the game’s default boy or girl model for a new NPC.
          </Text>
        </Box>
        <Flex gap="2">
          <Button variant="outline" borderColor="#b9c8c3" color="#34413d" bg="white" onClick={exportRecipe}>
            <LuFileJson /> JSON
          </Button>
          <Button bg="#176b57" color="white" _hover={{ bg: "#105443" }} onClick={exportGlb} disabled={exporting}>
            <LuDownload /> {exporting ? "Exporting…" : "Export GLB"}
          </Button>
        </Flex>
      </Flex>

      <Flex direction={{ base: "column", lg: "row" }} minH="calc(100svh - 68px)">
        <Box
          as="aside"
          order={{ base: 2, lg: 1 }}
          w={{ base: "full", lg: "340px" }}
          flexShrink="0"
          bg="white"
          borderRight={{ lg: "1px solid #dce4e1" }}
          borderTop={{ base: "1px solid #dce4e1", lg: "none" }}
          p={{ base: "5", md: "6" }}
          overflowY="auto"
        >
          <Stack gap="6">
            <ChoiceField label="Start from" value={config.baseModel} options={["Boy", "Girl"]} onChange={(value) => setConfig(value === "Boy" ? defaults : girlDefaults)} />
            <Field.Root>
              <Field.Label color="#34413d" fontSize="sm" fontWeight="700">
                NPC name
              </Field.Label>
              <Input value={config.name} onChange={(event) => update("name", event.currentTarget.value)} bg="white" borderColor="#cbd7d2" color="#19231f" />
            </Field.Root>

            <Box h="1px" bg="#e1e7e5" />
            <ColorRow label="Skin tone" value={config.skinColor} colors={skinTones} onChange={(value) => update("skinColor", value)} />
            <ColorRow label="Hair color" value={config.hairColor} colors={hairColors} onChange={(value) => update("hairColor", value)} />
            <ColorRow label="Top color" value={config.topColor} colors={clothingColors} onChange={(value) => update("topColor", value)} />
            <ColorRow label="Bottom color" value={config.bottomColor} colors={clothingColors} onChange={(value) => update("bottomColor", value)} />
            <ColorRow label="Shoe color" value={config.shoeColor} colors={clothingColors} onChange={(value) => update("shoeColor", value)} />

            <Flex gap="2">
              <Button aria-label="Reset NPC" variant="outline" borderColor="#b9c8c3" color="#34413d" bg="white" onClick={() => setConfig(config.baseModel === "Boy" ? defaults : girlDefaults)}>
                <LuRotateCcw />
              </Button>
            </Flex>
          </Stack>
        </Box>

        <Box order={{ base: 1, lg: 2 }} flex="1" minW="0" p={{ base: "3", md: "5" }}>
          <Box position="relative" h={{ base: "55svh", lg: "calc(100svh - 108px)" }} minH="420px" rounded="xl" overflow="hidden" border="1px solid #d4dfdb" bg="#edf3f1">
            <NpcPreview config={config} animation={animation} onReady={onRigReady} />
            <Box position="absolute" top="4" left="4" bg="rgba(255,255,255,.9)" px="3" py="2" rounded="lg" boxShadow="sm" pointerEvents="none">
              <Text fontWeight="700" color="#1c2b26">
                {config.name || "Untitled NPC"}
              </Text>
              <Text fontSize="xs" color="#65736e">
                Drag to rotate · Scroll to zoom
              </Text>
            </Box>
          </Box>
          <Text mt="3" color="#67756f" fontSize="xs">
            GLB exports include the edited game model and armature. Import into Unity, then assign your NPC component and animation controller.
          </Text>
        </Box>
      </Flex>
    </Box>
  )
}
