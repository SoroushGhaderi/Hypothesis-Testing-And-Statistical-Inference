# Course illustration previews: Lessons 1–5

These five 1536 × 1024 PNGs establish the course’s shared image style: warm paper, restrained ink-blue linework, a small ochre highlight, sparse typeset labels, and generous empty space. Each explains one concept. They are schematic concept illustrations, not numerical charts of the source datasets.

Open [the comparison gallery](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/preview.html) to review the images with captions against light or night backgrounds. Each image opens at full resolution for inspection. The neutral paper panel retains its original colors in both themes.

The files are listed in lesson order.

| Lesson | Asset | Concept | Labels |
|---|---|---|---|
| 1 | [Two-sided p-value](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/lesson_01_two_sided_p_value.png) | Equal outer tails under the assumed null | Under the null; Observed; Both tails |
| 2 | [Power and detection](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/lesson_02_power_and_detection.png) | Detection and misses under a specified alternative, for a one-sided procedure | Specified effect; Missed; Detected; Decision boundary |
| 3 | [Mean interval and benchmark](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/lesson_03_mean_interval_and_benchmark.png) | A mean’s uncertainty interval lies entirely above a fixed reference | Benchmark; Estimate; Interval |
| 4 | [Independent groups](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/lesson_04_independent_groups.png) | Distinct records belong to separate groups | Group A; Group B |
| 5 | [Paired measurements](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/lesson_05_paired_measurements.png) | Five schematic units retain identity across two measurements | Before; After; Same unit |

## Style and placement

The [image art direction](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/docs/maintenance/website_review/image_art_direction.md) defines the palette, atmosphere, density budget, scientific accuracy rules, mobile/theme considerations, exact insertion boundaries, captions, and alt text. It applies to all future images in the [website placement plan](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/docs/maintenance/website_review/review.md).

This first batch follows Lessons 1–5, rather than the A/B priority order of the full plan. It deliberately simplifies the earlier multi-part proposals into one idea per picture. Keep actual-data plots separate and generate them from verified data with standard plotting tools.

## Production record

All five assets were created with the built-in `image_gen` tool. The first image established the visual reference; the other four used that image as a style reference. Original full-resolution outputs were copied into this folder without resizing, recoloring, or other bitmap post-processing. No existing images were overwritten.

[Exact prompts](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/prompts.json) are preserved, including the reference-image instruction. A temporary connection failure on the first request was resolved by retrying the same prompt.

Visual inspection checked label spelling, curve/tail meaning, decision-boundary placement, the benchmark remaining outside the interval, separate group records, and five complete before/after pairs. The [gallery validation record](/Users/soroush/Desktop/Personal/Projects/hypothesis_testing_and_statistical_inference/assets/illustrations/preview_set_01/preview_validation.json) checks loading, alt-text presence, and absence of page overflow at desktop and phone widths in both themes. It does not measure contrast or typography inside rasterized labels.

These approved images are now included in Lessons 1–5 of `course.html`. Their PNG labels stay in English; the course provides English/Persian captions, alt text, and translated label explanations. The remaining ten lessons follow the same art direction. See the [complete catalogue](../readme.md).
