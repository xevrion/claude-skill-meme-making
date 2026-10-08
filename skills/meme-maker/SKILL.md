---
name: meme-maker
description: Make memes that are actually funny, from a photo, a screenshot, a situation, or just a topic, and render them to image files in seconds. Use whenever the user asks for a meme, a reaction image, a captioned photo, "make this a meme", "meme this", a roast image, or a joke picture about their code, team, exam, friends, or life. Covers picking the right format for the joke, writing captions, 200+ classic templates with correct text placement (Drake, Distracted Boyfriend, Gru's Plan, Galaxy Brain, Two Buttons and more), Impact top/bottom text, modern white-bar captions, labels placed on objects in the user's own photos, multi-panel stacks, and animated GIFs.
---

# Making memes

A meme is a joke with a fixed shape. The image supplies the shape and the reader already knows
it, so the caption only has to supply the specific thing. That is why most AI memes are not
funny: they pick a famous template, then write something generic into it. The work in this
skill is in finding the specific thing. The rendering is one command.

## Speed is part of the job

Do not interview the user. If they gave a photo, a situation, or even just a topic, that is
enough to make something. Make one strong meme and show it; offer variants after. Ask a
question only when there is genuinely nothing to work from ("make me a meme" with no context),
and even then offer two or three concrete directions rather than an open question.

If the user asks for "some memes" or "a few", make three in different formats, not three
captions on the same template.

## The renderer

Everything goes through `scripts/meme.py` in this skill's directory. Run it with `uv run`,
which installs Pillow automatically; fall back to `python3` with Pillow installed. Each
render command prints the path it wrote. Output defaults to `./memes/` in the working
directory, named from the caption; pass `-o` to choose.

```bash
M="uv run <skill-dir>/scripts/meme.py"

$M search distracted                       # find a template id
$M template drake "fixing the bug" "renaming the variable so the bug feels different"
$M template db "a new side project" "me" "the four side projects i already have"
$M template fine "" "the CI has been red since tuesday" --animated   # '' leaves a slot empty

$M classic photo.jpg --top "when the build passes" --bottom "and you changed nothing"
$M caption photo.jpg "me after saying 'quick fix' in standup"        # white bar above
$M caption reaction.gif "..."                                         # gifs stay animated

$M grid photo.jpg -o /tmp/grid.png          # 10% grid overlay, for reading coordinates
$M label photo.jpg "0.32,0.45:the deadline" "0.7,0.4,0.25:me, watching youtube"
$M blank "two buttons"                      # a blank imgflip format, then grid + label
$M stack before.png after.png               # vertical panels; --horizontal for side by side
```

- `template` sends text to memegen.link, which knows where every slot goes on 200+ templates.
  Use it whenever the format exists there; the placement will be better than anything you
  estimate by hand. Slots are positional. Check the order in
  [references/formats.md](references/formats.md) for multi-panel templates, because getting it
  wrong puts the punchline on the wrong character. Templates carry a small memegen.link
  watermark.
- `classic` is white Impact-style capitals with a black outline, top and bottom. Right for
  photos where the text can sit on the image.
- `caption` is the modern format: black text on a white bar above the image. Right for
  reaction photos, screenshots, and anything where text on the picture would cover the subject.
  `--font anton` gives the bold condensed caption look; `--align left` reads like a tweet.
- `label` places text centred at fractional coordinates `X,Y`, inside an optional box `W,H`
  (default 0.4 x 0.2 of the image), shrinking the text to fit. `--style impact` (default) reads
  on any background; `--style plain` is black sans for white areas like signs and papers;
  `--style plain-white` for dark areas.
- `stack` joins panels for formats the user builds from their own images: before and after,
  expectation and reality, a four-panel escalation.

## Workflow

1. **Look at what you were given.** If there is a photo, view it before thinking about
   formats. Expressions, posture, and objects in the photo are usually funnier than any
   template, and the user sent it because something in it is already funny to them.
2. **Find the joke.** Name the specific truth in one sentence: the gap between how things are
   supposed to go and how they go. "Deploying on Friday is risky" is a topic. "We keep a
   rollback script named `oops.sh` and it has more commits than the app" is a joke.
3. **Pick the format whose shape is that joke.** Preference, temptation, escalation, false
   sameness, misidentification, smug calm in a disaster: see
   [references/formats.md](references/formats.md), organised by joke shape. With a user's
   photo, the format is usually `caption` or `label` on their image, not a template.
4. **Write three candidate captions in your head and keep the one with a surprise.** The first
   idea is the one everyone has.
5. **Render.**
6. **View the output with the Read tool before showing it.** Check that text is readable, does
   not cover faces or the thing the joke depends on, is not shrunk into illegibility, and that
   each caption landed in the right slot. Fix and re-render; this takes seconds and is the
   difference between a meme and a broken image.
7. **Deliver** the file path (and the image itself, where the interface can show files) with at
   most a one-line note. Do not explain the joke.

## Writing captions

- **Specific beats general, every time.** Use the real names: the framework, the professor's
  course code, the friend's actual excuse, the exact error message. Specificity is what makes
  a reader feel seen. "Studying" is nothing; "rewatching lecture 3 at 2x the night before" is
  a meme.
- **Use the audience's own words.** Developers say "it works on my machine", students say
  "attendance", gamers say "one more match". Write in their vocabulary and register, lowercase
  and casual for modern formats.
- **Short.** Most slots want under eight words. If a caption needs a second sentence, the joke
  is not found yet. The renderer shrinks long text to fit, which is a sign the text is too long,
  not a solution.
- **Punchline last.** The bottom text, the last panel, the final slot. Setups go first.
- **Parallel structure across panels.** In Drake, Galaxy Brain, Gru, or Vince, keep the panels
  grammatically alike so only the important word changes. The contrast is the joke.
- **Don't caption what the image already shows.** If Harold is visibly hiding pain, the caption
  says what the pain is, not that he is in pain.
- **Respect the format's meaning.** Drake rejects the top option. The Distracted Boyfriend
  looks at the woman in red. "Is this a pigeon?" is a wrong guess. Swapping these produces
  something that looks like a misunderstanding of the meme rather than a joke.
- **No decoration.** No emoji, hashtags, "lol", or exclamation marks unless the format itself
  uses them. No "when you..." prefix on formats that are not reaction captions.

## Photos of real people

The user's own photos of themselves and their friends are fair game for affectionate roasting:
that is what most people want this for. Keep it to the kind of joke the friend would laugh at
in the group chat. Do not make memes that mock someone for their race, religion, gender,
sexuality, disability, or body; that sexualize anyone; or that put invented quotes or claims
in a real, identifiable person's mouth as if they were real.

Famous meme templates featuring public figures (Drake, Vince McMahon, the slap) are the
format itself and fine to use.

## When things fail

- **No network.** `template`, `search`, and `blank` need the internet; `classic`, `caption`,
  `label`, `stack`, and `grid` work fully offline on local images. The template catalogues are
  cached for a week in `~/.cache/meme-maker/`.
- **Unknown template id.** Run `search` with one distinctive word. If memegen does not have the
  format, `blank` fetches it from imgflip's top 100; if neither has it, find the image URL and
  use `label`.
- **Text placed wrong on a blank.** Render `grid` on the image, read the coordinates off it,
  and re-run `label`. Give `W,H` explicitly for narrow areas like a sign or a button.
- **Text too small.** The box is too small or the text is too long. Cut words first, enlarge the
  box second.
