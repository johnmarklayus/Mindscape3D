import { Box } from "@chakra-ui/react"
import Image from "next/image"

// The glowing MindScape 3D title, brought to life with CSS only (no extra downloads):
//  - it rises and fades in when the page opens, then floats gently;
//  - a warm light breathes behind the brain-tree (in for 4 s, out for 4 s, like the game's breathing exercise);
//  - a gold shimmer sweeps across the letters now and then (masked to the logo's own shape).
// Everything stops for visitors who ask their device to reduce motion.
export function AnimatedLogo({ width }: { width: Record<string, string> }) {
  return (
    <Box
      position="relative"
      w={width}
      maxW="90vw"
      mx="auto"
      aria-hidden
      css={{
        animation: "ms-logo-in 1.4s cubic-bezier(.2,.7,.2,1) both, ms-float 7s ease-in-out 1.4s infinite",
        "@media (prefers-reduced-motion: reduce)": { animation: "none" },
      }}
    >
      {/* the light behind the brain-tree */}
      <Box
        position="absolute"
        left="50%"
        top="2%"
        w="34%"
        aspectRatio={1}
        rounded="full"
        pointerEvents="none"
        bgGradient="radial"
        gradientFrom="rgba(255,226,160,0.75)"
        gradientVia="rgba(216,180,108,0.25)"
        gradientTo="transparent"
        filter="blur(18px)"
        css={{
          transform: "translateX(-50%)",
          animation: "ms-breathe 8s ease-in-out infinite",
          "@media (prefers-reduced-motion: reduce)": { animation: "none", opacity: 0.6 },
        }}
      />
      <Box
        position="relative"
        css={{
          animation: "ms-glow 8s ease-in-out infinite",
          "@media (prefers-reduced-motion: reduce)": { animation: "none" },
        }}
      >
        <Image
          src="/images/logo.png"
          alt=""
          width={1200}
          height={450}
          priority
          sizes="(max-width: 768px) 90vw, 620px"
          style={{ width: "100%", height: "auto", display: "block" }}
        />
      </Box>
      {/* shimmer, cut to the logo's shape */}
      <Box
        position="absolute"
        inset="0"
        pointerEvents="none"
        css={{
          backgroundImage:
            "linear-gradient(105deg, transparent 38%, rgba(255,236,190,0.0) 42%, rgba(255,236,190,0.65) 50%, rgba(255,236,190,0.0) 58%, transparent 62%)",
          backgroundSize: "250% 100%",
          backgroundRepeat: "no-repeat",
          mixBlendMode: "screen",
          maskImage: "url(/images/logo-mask.png)",
          WebkitMaskImage: "url(/images/logo-mask.png)",
          maskSize: "100% 100%",
          WebkitMaskSize: "100% 100%",
          animation: "ms-shimmer 7s ease-in-out 2s infinite",
          "@media (prefers-reduced-motion: reduce)": { display: "none" },
        }}
      />
    </Box>
  )
}

// Gold fireflies drifting up through the hero.
const flies = [
  [8, 0, 11], [17, 3.5, 14], [26, 7, 12], [35, 1.5, 16], [44, 5, 13], [53, 9, 15],
  [62, 2.5, 12], [71, 6, 17], [80, 0.8, 13], [89, 4.2, 15], [94, 8.5, 12], [3, 10, 16],
]

export function Fireflies() {
  return (
    <Box position="absolute" inset="0" overflow="hidden" pointerEvents="none" aria-hidden css={{ "@media (prefers-reduced-motion: reduce)": { display: "none" } }}>
      {flies.map(([left, delay, duration], i) => (
        <Box
          key={i}
          position="absolute"
          bottom="-10px"
          left={`${left}%`}
          boxSize={i % 3 === 0 ? "6px" : "4px"}
          rounded="full"
          bg="#ffe2a0"
          boxShadow="0 0 10px 3px rgba(255,214,140,0.7)"
          opacity={0}
          css={{ animation: `ms-firefly ${duration}s ease-in ${delay}s infinite` }}
        />
      ))}
    </Box>
  )
}
