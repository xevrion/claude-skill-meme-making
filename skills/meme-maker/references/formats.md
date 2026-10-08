# Meme formats by joke shape

Pick the format from the structure of the joke, not from popularity. Every format below is
listed with what it means, because a format used against its meaning reads as a mistake rather
than a joke. Slot order was checked by rendering each template with numbered text; pass the
text arguments in exactly this order.

`memegen` ids render with `meme.py template <id> ...` and get correct placement for free.
`imgflip` formats exist only as blank images: `meme.py blank "<name>"`, then `grid` and `label`.

## Preference: one thing rejected, another chosen

| Format | Id | Slots | Use it for |
|---|---|---|---|
| Drake | `drake` | 1 rejected, 2 preferred | The preferred option should be the worse or funnier one. Drake picking the obviously good option is not a joke. |
| Tuxedo Winnie the Pooh | `pooh` | 1 plain version, 2 fancy version | The same thing said pretentiously. Slot 2 is a needlessly elevated rewording of slot 1. |
| Left Exit 12 | `exit` | 1 the sensible road ahead, 2 the exit, 3 the car | Swerving away from the obvious choice at the last moment. Slot 3 is who is swerving. |
| Two Buttons | imgflip `Two Buttons` | two button labels, then the sweating man | Two options the person cannot choose between, usually because both are bad or both are tempting. |
| Bus | `bus` | 1 sad guy on the dark side, 2 happy guy on the sunny side | Two views of the same situation, one gloomy and one oblivious. |

## Temptation and betrayal

| Format | Id | Slots | Use it for |
|---|---|---|---|
| Distracted Boyfriend | `db` | 1 the tempting new thing (woman in red), 2 the subject, 3 what they are neglecting | Abandoning a commitment for something shinier. |
| Mother ignoring kid drowning | `pool` | 1 the favoured kid on mom's shoulders, 2 the drowning kid, 3 the mother | Lavishing attention on one thing while another is dying. |
| Woman yelling at cat | `woman-cat` | 1 the woman yelling, 2 the cat | Someone furious and the unbothered target of the fury. The cat side should be smug or nonsensically calm. |
| Running away balloon | `balloon` | 1 the goal, 2 the goal again, 3 the thing pulling you away | Being dragged away from what you want by your own habit or flaw. |
| Grant Gustin at grave | `grave` | 1 the gravestone, 2 the grave, 3 the man posing | Cheerfully posing over something that died, often something you killed. |

## Escalation and irony

| Format | Id | Slots | Use it for |
|---|---|---|---|
| Galaxy Brain | `gb` | 4 stages, small brain to glowing brain | Ideas getting dumber while presented as getting smarter. The last panel must be the most absurd. |
| Vince McMahon | `vince` | 3 escalating options | Rising excitement over increasingly specific or ridiculous things. |
| Gru's Plan | `gru` | 4 panels: step, step, the flaw, the flaw again | A plan whose third step reveals the problem, repeated in panel 4 as Gru realises. Slots 3 and 4 are usually identical. |
| Anakin and Padme | `right` | 1 Anakin, 2 Padme, 3 Anakin's line, 4 Padme's hopeful question, 5 the same question again | Padme's question is repeated in slot 5 because Anakin's silence answers it. Slots 4 and 5 should match. |
| Panik Kalm Panik | `panik-kalm-panik` | 3 panels | Alarm, false relief, then a detail that makes it worse than before. |
| Midwit | `midwit` | 1 simple person, 2 overthinker in the middle, 3 genius | Slots 1 and 3 say the same plain thing; slot 2 is the anxious overcomplication. |
| Expectation vs reality | `dbg` | 1 smiling expectation, 2 disappointed reality | A hopeful setup followed by the deflating truth. |
| Always Has Been | `astronaut` | 1 first astronaut's realisation, 2 "always has been", 3 label on first astronaut, 4 label on the gunman | A discovery that was obvious all along. Slot 1 usually starts "wait, it's ...?" |
| Scooby Doo reveal | `reveal` | 1 the masked villain, 2 "let's see who you really are", 3 the unmasked face, 4 the reaction | Something that looked new turning out to be an old thing in disguise. |
| Stonks | `stonks` | 1 caption on top, 2 label at the bottom | Celebrating a bad financial or life decision as genius. Misspelling the label is part of the format. |
| This is Fine | `fine` | 1 top, 2 bottom | Calm acceptance of an obvious disaster. Use `--animated` for the gif. |

## Sameness and misidentification

| Format | Id | Slots | Use it for |
|---|---|---|---|
| Is this a pigeon? | `pigeon` | 1 the person, 2 the butterfly, 3 the wrong question | Confidently misidentifying something. Slot 3 is "is this ...?" |
| They're the same picture | `same` | 1 left paper, 2 right paper, 3 Pam's line | Two things presented as different that are identical. |
| Spider-Man pointing | `spiderman` | 1 left, 2 right | Two parties accusing each other of the same thing. |
| Epic Handshake | `handshake` | 1 left arm, 2 right arm, 3 the clasp | Two unlikely groups united by one shared thing in slot 3. |
| Three-Headed Dragon | `3hd` | three heads left to right | Two serious options and a third derpy one. The derp goes in slot 3. |
| Are you two friends? | `friends` | 1 the question, 2 left guy's answer, 3 right guy's answer | One side denies the relationship, the other claims it. |

## Reaction captions

These have one image and the joke is the caption. Use the modern `caption` command on the blank
when the format has no text of its own, or `template` with the top slot empty.

| Format | Id | Use it for |
|---|---|---|
| Change my mind | `cmm` | A confidently held opinion, written on the sign. One slot. |
| Hide the Pain Harold | `harold` | Smiling through something painful. |
| Roll Safe | `rollsafe` | Bad logic presented as a clever loophole: "can't X if you Y". |
| Mocking Spongebob | `spongebob` | Repeating someone's words back in alternating caps. Write slot 2 in aLtErNaTiNg CaSe yourself. |
| Futurama Fry | `fry` | "not sure if X / or Y". |
| Kombucha girl | `kombucha` | Disgust turning into reluctant approval. |
| Khaby Lame | `khaby-lame` | 1 the overcomplicated approach, 2 the obvious simple fix. |
| Will Smith slap | `slap` | 1 the one getting slapped, 2 the slapper. |
| Elmo choosing cocaine | `elmo` | 1 the sensible option, 2 the subject, 3 the bad option, 4 sensible again, 5 bad again. Choosing the bad thing. |
| Patrick's wallet | `wallet` | 8 slots, a conversation where logic fails at the last line. |
| American Chopper | `chair` | 6 slots, a heated argument that escalates panel by panel. |

## imgflip-only formats

These are not on memegen. Download the blank, overlay `grid` to read coordinates, then `label`.

- `Two Buttons`, `UNO Draw 25 Cards` (do the thing or draw 25; the person draws 25)
- `Trade Offer` (i receive / you receive)
- `Monkey Puppet` (awkwardly looking away from something said)
- `Buff Doge vs. Cheems` (strong past version vs weak present version)
- `Sleeping Shaq` (ignoring the big thing, waking for the small thing)
- `Batman Slapping Robin` (Robin says something, Batman shuts it down)
- `Waiting Skeleton` (still waiting for something that never comes)
- `They don't know` (party guy in the corner thinking about his niche thing)
- `Boardroom Meeting Suggestion` (the one sensible idea gets thrown out the window)
- `Bernie I Am Once Again Asking For Your Support`
- `Sad Pablo Escobar`, `Clown Applying Makeup`, `Flex Tape`, `Surprised Pikachu`, `Squidward window`

The imgflip list is its top 100 at fetch time and drifts. If `search` misses a format, any
image URL works as input to `classic`, `caption`, and `label`.
