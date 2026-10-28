#!/bin/bash
# Generate narration segments for the dolphins video via z-ai TTS CLI
set -e
cd /home/z/my-project/studio/videos/dolphins/narration

declare -a TEXTS=(
  "Here's a puzzle. Dolphins are mammals, so they need air to breathe. But they live in the ocean. So how do they sleep without drowning?"
  "Humans breathe automatically. You never have to think about it. A dolphin's breath is voluntary. Every single breath is a conscious decision. Fall completely asleep, and a dolphin would stop breathing."
  "So dolphins evolved a clever workaround. They sleep with only half of their brain at a time. The other half stays awake. Scientists call it unihemispheric slow-wave sleep."
  "The sleeping half rests, while the awake half stays on duty. And here is the giveaway. A sleeping dolphin keeps one eye open. The eye on the opposite side of the sleeping half, watching for predators."
  "They drift near the surface, resting motionless or swimming slowly, and rise every few minutes for a calm, easy breath. Over a full day, each half of the brain gets about four hours of sleep."
  "New mothers do not get that luxury. For a whole month after a calf is born, mother and baby barely sleep at all."
  "Half a brain asleep. One eye open. And still breathing. That is how a dolphin sleeps without drowning."
)

rm -f test.wav
for i in "${!TEXTS[@]}"; do
  n=$((i+1))
  if [ -f "seg$n.wav" ] && [ -s "seg$n.wav" ]; then echo "seg$n.wav exists, skip"; continue; fi
  echo "--- seg$n: ${#TEXTS[$i]} chars"
  z-ai tts -i "${TEXTS[$i]}" -o "./seg$n.wav" --voice jam --speed 1.0 2>&1 | tail -1
done

echo "=== durations ==="
for f in seg*.wav; do d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"); echo "$f: $d s"; done
