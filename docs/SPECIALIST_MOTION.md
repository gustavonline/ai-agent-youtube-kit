# Specialist code-motion route

Use upstream [HeyGen HyperFrames](https://github.com/heygen-com/hyperframes)
only when the requested deliverable is:

- an entire code-animated explainer or motion-graphics video; or
- one bounded overlay asset for the Diffusion timeline.

Do not use HyperFrames as a second editor for routine owner-recorded long-form,
shorts, cuts, audio, captions, or general overlays. Diffusion owns that work.

Start with the upstream `/hyperframes` router. Its current instructions and
workflow skills are installed from the upstream repository:

```text
npx hyperframes skills update
```

Follow the workflow selected there rather than copying a project or skill into
ACS. Keep the code-native project external. After review, copy only the final
video or overlay needed by the production and register it as a graph node with
hash, provenance, edges, and independent review.
