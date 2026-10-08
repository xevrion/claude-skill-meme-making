# meme-maker

A Claude Code skill that turns a photo, a situation, or a topic into a meme that is actually
funny, and renders it to an image file in seconds.

Ask an AI for a meme and you usually get a famous template with something generic written on
it. The template was never the hard part; finding the specific joke is. This skill tells
Claude how to find that joke and match it to the format whose shape fits. It also bundles a
renderer, so you never have to explain fonts or text placement.

## What it does

- Picks the format from the shape of the joke (preference, temptation, escalation, false
  sameness, misidentification) using a reference of 40+ formats with what each one means
- Writes captions that are specific, short, in the audience's own words, with the punchline last
- Renders 200+ classic templates locally from [memegen](https://github.com/jacebrowning/memegen)'s
  open source template data, so text placement is correct and there is no watermark, ready
  to post
- Captions your own photos locally: Impact top and bottom text, modern white-bar captions,
  or labels placed on the people and objects in the picture
- Keeps animated GIFs animated, stacks panels, and falls back to imgflip blanks for formats
  memegen does not have
- Views every render before showing it, then fixes covered faces, unreadable text, or a
  caption in the wrong slot

## Install

In Claude Code:

```
/plugin marketplace add xevrion/claude-skill-meme-making
/plugin install meme-maker@xevrion-skills
```

Update later with `/plugin marketplace update xevrion-skills`.

Then just ask: "meme this" with a photo, "make a meme about our flaky CI", "roast my desk
setup". The skill triggers on requests for memes, reaction images, captioned photos, and joke
pictures.

The renderer is one Python script that runs with [uv](https://docs.astral.sh/uv/) and pulls in
Pillow automatically. Without uv, `pip install pillow` and it runs with `python3`. Template
rendering needs the internet; captioning and labelling local images works offline.

## Example

```bash
uv run skills/meme-maker/scripts/meme.py template drake \
  "fixing the bug" "renaming the variable so the bug feels different"
```

## Credits

Template images and text-box layouts come from
[memegen](https://github.com/jacebrowning/memegen) (MIT), fetched on first use and cached;
blanks for other formats come from [imgflip](https://imgflip.com). Bundled fonts are
[Anton](https://github.com/googlefonts/AntonFont), [Arimo](https://github.com/googlefonts/arimo)
and [Titillium Web](https://fonts.google.com/specimen/Titillium+Web), all under the SIL Open
Font License; licence texts are in `skills/meme-maker/assets/fonts/`.
