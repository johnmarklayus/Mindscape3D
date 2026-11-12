"use client"

import { Box, Button, CloseButton, Field, HStack, Icon, Stack, Text } from "@chakra-ui/react"
import Image from "next/image"
import { useEffect, useRef, useState } from "react"
import { LuImagePlus } from "react-icons/lu"
import { MAX_SHOTS, SHOT_MAX_BYTES, SHOT_MAX_SIDE, SHOT_TYPES } from "@/lib/contact"

export type Shot = { file: File; url: string }

// Shrinks a screenshot so the longest side is at most SHOT_MAX_SIDE px, as a JPEG.
async function shrink(file: File): Promise<File> {
  const bitmap = await createImageBitmap(file)
  const scale = Math.min(1, SHOT_MAX_SIDE / Math.max(bitmap.width, bitmap.height))
  const canvas = document.createElement("canvas")
  canvas.width = Math.round(bitmap.width * scale)
  canvas.height = Math.round(bitmap.height * scale)
  canvas.getContext("2d")!.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  bitmap.close()
  for (const quality of [0.85, 0.7, 0.55]) {
    const blob = await new Promise<Blob | null>((r) => canvas.toBlob(r, "image/jpeg", quality))
    if (blob && (blob.size <= SHOT_MAX_BYTES || quality === 0.55)) {
      return new File([blob], file.name.replace(/\.\w+$/, "") + ".jpg", { type: "image/jpeg" })
    }
  }
  throw new Error("Could not read that image.")
}

// Up to three screenshots for a bug report, with previews and a remove button on each.
export function ScreenshotPicker({ shots, onChange }: { shots: Shot[]; onChange: (shots: Shot[]) => void }) {
  const input = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const latest = useRef(shots)
  latest.current = shots
  useEffect(() => () => latest.current.forEach((s) => URL.revokeObjectURL(s.url)), [])

  async function add(list: FileList | null) {
    setError("")
    if (!list?.length) return
    const room = MAX_SHOTS - shots.length
    const picked = Array.from(list)
    if (picked.length > room) setError(`You can attach up to ${MAX_SHOTS} screenshots.`)
    setBusy(true)
    const added: Shot[] = []
    for (const file of picked.slice(0, room)) {
      if (!SHOT_TYPES.includes(file.type)) {
        setError("Please choose PNG, JPG or WebP images.")
        continue
      }
      try {
        const small = await shrink(file)
        added.push({ file: small, url: URL.createObjectURL(small) })
      } catch {
        setError(`"${file.name}" could not be read.`)
      }
    }
    setBusy(false)
    if (input.current) input.current.value = ""
    onChange([...shots, ...added])
  }

  function remove(i: number) {
    URL.revokeObjectURL(shots[i].url)
    onChange(shots.filter((_, j) => j !== i))
  }

  return (
    <Field.Root invalid={!!error}>
      <Field.Label>Screenshots (optional, up to {MAX_SHOTS})</Field.Label>
      <input ref={input} type="file" accept={SHOT_TYPES.join(",")} multiple hidden onChange={(e) => add(e.target.files)} />
      <HStack gap="3" flexWrap="wrap" align="stretch">
        {shots.map((s, i) => (
          <Box key={s.url} position="relative" w="28" h="20" rounded="md" overflow="hidden" borderWidth="1px" borderColor="border">
            <Image src={s.url} alt={`Screenshot ${i + 1}`} fill unoptimized style={{ objectFit: "cover" }} />
            <CloseButton
              size="2xs"
              position="absolute"
              top="1"
              right="1"
              bg="blackAlpha.700"
              color="white"
              _hover={{ bg: "blackAlpha.800" }}
              aria-label={`Remove screenshot ${i + 1}`}
              onClick={() => remove(i)}
            />
          </Box>
        ))}
        {shots.length < MAX_SHOTS && (
          <Button
            variant="outline"
            borderStyle="dashed"
            colorPalette="brass"
            w="28"
            h="20"
            flexDirection="column"
            gap="1"
            loading={busy}
            onClick={() => input.current?.click()}
          >
            <Icon boxSize="5">
              <LuImagePlus />
            </Icon>
            <Text fontSize="xs">Add image</Text>
          </Button>
        )}
      </HStack>
      <Stack gap="0">
        <Field.HelperText>PNG, JPG or WebP. Large images are resized before sending.</Field.HelperText>
        <Field.ErrorText>{error}</Field.ErrorText>
      </Stack>
    </Field.Root>
  )
}
