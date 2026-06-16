# Prompts

## Reference Analysis

```text
Analyze this reference video for our channel: <url>. Follow docs/REFERENCE_ANALYSIS.md. Run scripts/analyze-reference-video.py, inspect the frames from frames_manifest.json, read transcript.md, fill analysis.md, update channel/REFERENCES.md, and promote only reusable lessons to channel/STYLE_GUIDE.md.
```

## Extract Channel Style

```text
Read channel/PROFILE.md, channel/REFERENCES.md, all current channel/references/*/analysis.md files, DESIGN.md, and PROJECT_MEMORY.md. Condense the reusable hook, structure, visual, CTA, caption, and packaging patterns into channel/STYLE_GUIDE.md. Keep it concise and evidence-backed.
```

## Video Brief

```text
Run python3 scripts/new-video.py <slug> if the project is not scaffolded yet. Then read channel/PROFILE.md, channel/STYLE_GUIDE.md, DESIGN.md, PROJECT_MEMORY.md, and relevant reference analyses. Fill footage/<slug>/edit/video-brief.md for this video idea: <idea>. Include promise, audience shift, proof required, structure, packaging direction, and motion needs.
```

## Inventory And Strategy

```text
Use local Whisper transcripts from footage/<slug>/edit/takes_packed.md, then use video-use. Inventory footage/<slug>, propose an agentic video edit strategy, and include target runtime, structure, best takes, risky cuts, and where HyperFrames motion graphics would help. Save the approved plan to footage/<slug>/edit/cut-plan.md. Wait for my approval before cutting.
```

## Build Motion Graphics

```text
Use HyperFrames. In video-projects/<slug>-graphics, build a 9:16 motion graphics sequence for these beats: <beats>. Use DESIGN.md, run lint/inspect, preview it, and do not render final until the preview is checked.
```

## Final Assembly

```text
Use video-use. Assemble the approved EDL, include the HyperFrames assets from video-projects/<slug>-graphics/renders, burn readable captions, run self-eval on cut boundaries, and produce edit/final.mp4.
```

## Packaging Review

```text
Follow docs/PACKAGING.md. Read channel/PROFILE.md, channel/STYLE_GUIDE.md, channel/published-videos.csv, relevant reference analyses, and footage/<slug>/edit/cut-plan.md. Create footage/<slug>/edit/packaging-review.md from templates/packaging-review.md with title candidates, thumbnail concepts, scores, risks, and the recommended title/thumbnail pair.
```

## Final Review

```text
Follow docs/FINAL_REVIEW.md. Review footage/<slug>/edit/final.mp4 against DESIGN.md, PROJECT_MEMORY.md, MOTION_PHILOSOPHY.md, channel/STYLE_GUIDE.md, the cut plan, and packaging review. Create footage/<slug>/edit/final-review.md with scores, timestamped findings, publish readiness, and durable lessons.
```

## Agentic Workflow Video Brief

```text
Audience: operators and founders who want useful AI agents.
Tone: technical, direct, credible.
Structure: hook -> problem -> agent workflow -> proof/demo -> takeaway -> CTA.
Avoid: vague AI hype, generic b-roll, unreadable captions, and overexplaining setup.
```
