# Packaging and publisher handoff

Packaging is editorial: title, thumbnail/frame choice, description/copy, CTA,
captions, and selected approved artifacts. Use the packaging-review template
to compare those choices with the final bytes.

ACS does not build a publish package. The content graph records every artifact;
`publisher-handoff.json` selects the exact independently approved node versions
and hashes a supervised publisher may later use.

Optional channel targets are node-local stable IDs. A target may narrow a
handoff selection only when the node declares it. No predefined platform list
or enabled-channel count is required.

The handoff always remains awaiting separate authorization, supervised,
not-posted, and unable to post externally. Scheduling notes are human context,
not authority.
