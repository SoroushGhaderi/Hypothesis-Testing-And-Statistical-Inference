# Course image art direction

## Shared style and atmosphere

All course imagery should feel like a carefully designed university textbook: calm, precise, warm, and quietly expressive. Use restrained ink illustration, subtle print character, disciplined typography, and generous empty space. The goal is an authored editorial appearance without the visual clichés of mass-produced generated artwork.

Use warm ivory paper (`#f8f5ee`), dark graphite (`#263849`), muted ink blue (`#285777`), and a small ochre accent (`#b4874b`). Blue carries the main structure; ochre highlights the one relationship the learner should notice. Avoid decorative scenes and props that do not explain the lesson.

Use this direction across the entire placement plan in `review.md`, rather than inventing a different style for each subject. Treat each figure as part of the same visual language: consistent line weight, paper tone, label treatment, margins, and accent usage.

## Information budget

Each image should teach **one idea**. A caption and the surrounding lesson carry the explanation.

- Default to one diagram, rather than a dashboard or montage.
- Use at most four short labels and approximately twelve words inside the image.
- Use one highlight treatment, with shape or hatching alongside color.
- Leave roughly a quarter of the canvas free of information; avoid filling every corner.
- Use at most two tightly related panels only when their comparison is the concept.
- Prefer three to five illustrative records over dozens of tiny marks. State that the records are schematic.
- If a proposed image exceeds this budget, split it into separate figures or remove secondary content. The earlier placement table describes conceptual scope, not a requirement to fit everything into one bitmap.

Avoid in-image titles, captions, paragraphs, legends with many entries, decorative icons, elaborate arrows, multiple unrelated charts, and repeated labels. Remove visual clutter before enlarging the canvas.

## Authored appearance

Keep lines intentional and relationships geometrically correct. A slight ink or screen-print texture may soften the illustration, but must not interfere with an axis, interval, boundary, or label. Use clean typeset labels, rather than simulated handwriting.

Avoid glossy 3D objects, glow, dramatic lighting, saturated gradients, excessive symmetry for decoration, cartoon scientists, floating symbols, stock business illustrations, and ornamental flourishes. Do not use distressing or paper noise as a substitute for thoughtful composition.

Preserve generation provenance and prompts in the production notes. The aesthetic objective is a natural textbook appearance; the production record remains accurate.

## Scientific accuracy

Concept illustrations and numerical figures have different accuracy requirements.

Concept illustrations may use schematic curves, intervals, or a few invented example records, with an explicit “schematic” statement in their caption or accompanying text. Do not let a schematic imply measured data, exact probabilities, effect sizes, sample counts, or statistical significance.

Plots that communicate actual ANES, RAND, Grunfeld, Spector, or survival results must be generated from verified data with standard plotting tools. Numerical scales, intervals, p-values, and labels must be checked against the analysis. Apply the same palette and editorial restraint to those plots; do not ask image generation to invent data geometry.

For a two-sided p-value illustration, shade equally extreme areas in both tails under the null. For power, identify a specified alternative and the decision boundary. For a benchmark comparison, distinguish the estimate and its uncertainty from individual variation. Independent groups must contain separate records; paired diagrams must preserve identity across measurements.

## Mobile, themes, and language

The first previews use a landscape 3:2 paper panel that can remain the same deliberate neutral surface in both light and night mode. This keeps scientific colors stable. The inserted images use a theme-aware frame and caption surface; do not invert the bitmap.

Inspect each figure at 320–390 CSS pixels. Labels must remain readable, with no tiny legends or essential detail confined to a corner. If the diagram only works at desktop width, simplify it or produce a separate mobile composition. Keep full-resolution originals.

Keep captions and descriptions in HTML, so they can inherit the website theme and be localized. The first previews have sparse English labels; the bilingual site supplies localized captions, alt text, and a text legend translating each English label. Mathematical direction and numerical axes remain left-to-right.

Alt text should state the teaching relationship, rather than listing decorative details. Values essential to a data plot also need a readable textual summary or data table. Use direct labels, line styles, and hatching so that color does not carry meaning alone.

## First preview batch: Lessons 1–5

This batch follows lesson order, rather than the priority order of the earlier A/B recommendation list. There is one image per lesson. These are concept illustrations for quality review, not replacements for the numerical plots listed in the full review.

| Lesson | Single teaching idea | Exact proposed insertion point | Caption | Alt text |
|---|---|---|---|---|
| 1 | Both equally extreme tails contribute to a two-sided p-value | After **1.2 What a p-value is—and is not**, before **1.3 Test statistics, confidence intervals, and effect sizes** | “Under the assumed null model, both equally extreme tails contribute to the two-sided p-value. Schematic illustration.” | “A symmetric null distribution has matching shaded outer tails beyond two equally extreme thresholds; the right threshold marks the observed statistic.” |
| 2 | Power is the chance of detection under a specified alternative | After the power paragraph in **2.1 Two kinds of decision error**, before **2.2 Planning before data collection** | “For a specified alternative and testing procedure, outcomes beyond the decision boundary are detections; the remaining outcomes are misses. One-sided schematic.” | “An alternative distribution is divided by a decision boundary into a smaller missed-effect area and a larger detection area.” |
| 3 | A mean interval can sit entirely above a benchmark | After **Mean benchmark** in the worked example, before **Proportion benchmark** | “The interval describes uncertainty about the population mean, not the spread of individual ages. The ANES example’s mean interval lies above its teaching benchmark; this drawing is schematic.” | “An estimate and its horizontal uncertainty interval are entirely to the right of a separate benchmark line.” |
| 4 | Independent groups contain different observational units | After **4.1 Design and estimand**, before the worked example | “Each record belongs to one comparison group. Group labels do not create pairing. Schematic records.” | “Two separate groups contain distinct record marks; none is connected or repeated across groups.” |
| 5 | Pairing preserves identity before comparing change | After **5.1 Pairing changes the unit of analysis**, before **5.2 Rank-based and binary paired tests** | “Each line connects two measurements from the same unit. The paired analysis studies within-unit change. Schematic records, not the eleven observed firms.” | “Five lines connect five earlier measurements to their matching later measurements, preserving each unit’s identity.” |

## Production checks and current integration

Check the single teaching idea, statistical geometry, exact label spelling, consistency with the series, and phone-size readability. Reject unexplained symbols, merged records, ambiguous boundaries, mismatched pair counts, extraneous objects, or falsely precise numerical markings.

The user approved the first five images and requested insertion and completion of the remaining lessons. All 15 are now integrated through `tools/course_illustrations.json`; the generator checks exact insertion headings and asset existence. The HTML validator permits only registered instructional figures, while still excluding notebook plots. Captions and label explanations remain readable, localized HTML; illustrations remain inline without redundant image controls. Images load lazily, retain their 3:2 proportions without cropping, and preserve their paper colors in both themes.

The [complete catalogue](../../../../assets/illustrations/readme.md) records all 15 placements and descriptions. Generation used the built-in image tool with the first approved image as the visual style reference. The Lesson 13 diagram was revised to remove connected left endpoints, making the four independent follow-up records clear. Exact prompts and the Lesson 13 revision prompt are consolidated in [prompts.json](prompts.json). Final assets live in `assets/illustrations/lessons/`; the obsolete preview gallery and superseded draft are removed. Numerical plots of actual study results remain a separate data-derived task.
