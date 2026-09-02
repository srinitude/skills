# Coordinates

## Contents

- Four coordinates
- The 35 categories
- The eight lenses
- Why the widening ladder exists
- Reading the widening report

## Where the questions live

Resource gate: run `mise run validate` before using package files named here.

All 16,112 questions sit in `assets/questions/`, one file per category, ordered by identifier. `assets/index.yaml` maps every category name to its file. A query reads one category file, so the cost stays flat no matter how large the library grows.

## Four coordinates

A slice is located by four values, and `mise run slice` takes one flag for each. Category is required, because it selects the file to read.

| Coordinate    | Flag           | Values                                                         |
| ------------- | -------------- | -------------------------------------------------------------- |
| category      | `--category`   | one of the 35 names below, matched exactly                     |
| stage         | `--stage`      | concept, exploration, refinement, pre-ship, post-ship          |
| artifact type | `--applies-to` | screen, flow, component, copy, system, brand, artifact, motion |
| lens          | `--lens`       | one of the eight tags below                                    |

Two more flags narrow further. `--seniority` takes IC, senior, or director. `--match` takes free text checked against the question, its trade-off, and its failure.

Set category first. It carries the most signal, it selects the file, and the widening ladder never drops it.

## The 35 categories

Accessibility · Accounts, security and admin · Acquisition, marketing surfaces and growth loops · AI honesty, provenance and disclosure · AI interaction, agents and personalization · Brand distinctiveness and positioning · Collaboration, community and safety · Color, theming and dark mode · Design process, stakeholders and journeys · Design systems and developer surfaces · Empty, loading, error and edge states · Forms and input · Game feel, teaching and difficulty · Habit, retention and churn · Handoff, spec and design QA · Icons, illustration and photography · Internationalization and locale · Keyboard, commands and power surfaces · Layout, grid, hierarchy and density · Motion, film and moving image · Naming and brand architecture · Navigation, IA and search · Notifications, email and interruption · Onboarding, activation and first run · Performance, weight and network reality · Persuasion, defaults and dark patterns · Physical product, packaging and print · Platform conventions and responsive fit · Pricing, checkout and billing · Privacy, consent and compliance · Sound and haptics · Spatial, ambient and built space · Tables, charts and dashboards · Typography and editorial typesetting · Voice, tone and UI copy

Sizes run from 222 to 790 questions. An unknown name exits 2 rather than returning nothing, so a typo fails loudly.

## The eight lenses

A lens is a filter, never a mode. Accessibility review, ethics check, longevity test, and internationalization pressure test are the same retrieval with one tag pinned.

| Lens          | Questions | Categories reached |
| ------------- | --------- | ------------------ |
| trust         | 3507      | 35 of 35           |
| ethics        | 2108      | 35 of 35           |
| long-term     | 2044      | 35 of 35           |
| brand         | 1881      | 35 of 35           |
| accessibility | 1644      | 34 of 35           |
| performance   | 1070      | 34 of 35           |
| ai-native     | 942       | 34 of 35           |
| i18n          | 558       | 35 of 35           |

Each lens reaches almost every category, which is the point. An ethics question about a paywall and an ethics question about a push notification sit on different shelves and answer to the same lens.

## Why the widening ladder exists

Pinned to two coordinates the corpus is dense. All 175 category and stage pairs hold at least five questions.

Pinned to three it is not. Of the 1400 category, stage, and artifact type cells, 786 hold fewer than 12 questions and some hold none. Nothing is filed under artifact plus concept plus colour and theming. A tool that pinned three coordinates and reported whatever came back would return a near empty shelf more than half the time and call it a review.

So `slice.py` widens instead of failing, in fixed order, stopping the moment it reaches 12 rows.

1. category, stage, artifact type, and lens together
2. drop the lens
3. drop the artifact type, which recovers 778 of the 786 thin cells
4. drop the stage, which recovers all 786
5. category alone

## Reading the widening report

Every widening prints one line to stderr, such as `widened: dropped lens, applies-to`. Read it before trusting the result. A widened slice looks the same as a precise one and answers a broader question, which is the failure this report exists to prevent. Say so in the reply when it happens.

## Output normalization

Resource gate: run `mise run validate` before using package files named here.

Both output formats replace em and en dashes in the question, trade-off, failure, subcategory, and source name with a comma or a colon. The stored corpus keeps its original punctuation. This makes any slice safe to paste into a plain markdown document without a punctuation cleanup pass, and it means a quoted run in examples/ matches what the script prints today.
