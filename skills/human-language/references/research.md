# Research and limits

This supports [human-language](../SKILL.md). Sources were checked on September 15, 2026. Read this file when reviewing the skill's basis or updating its rules. Normal use needs no web search or installed tool.

Resource gate: for package maintenance, run `mise run validate` first; ordinary use reads these files directly.

## What the evidence supports

The skill combines plain-language guidance with agent-context guidance. That combination is a design choice tested on finite cases, not a published finding that one prompt controls every agent. The user chose the sixth-grade target.

| Source | Finding used | Limit or contrary case |
| --- | --- | --- |
| [Agent Skills specification](https://agentskills.io/specification) | A portable skill uses a directory with `SKILL.md`, YAML metadata, and optional resources. | Format validation does not prove writing quality or activation. |
| [Agent Skills client support](https://agentskills.io/client-implementation/adding-skills-support) | Hosts discover and load skills; they also manage them after compaction and delegation. `.agents/skills/` is a shared convention. | The format does not mandate an install path or an always-on hook. Each host must support loading. |
| [Digital.gov: write for the reader](https://digital.gov/guides/plain-language/principles/write-for-reader) | Use readers' real questions and needs. Keep different audiences clear. | A generic reading level does not replace knowledge of the actual reader. |
| [Digital.gov: test for understanding](https://digital.gov/guides/plain-language/test) | Test early, revise, and test again. Paraphrase and task tests can reveal what readers understand. | Asking whether text sounds nice is not the same as testing understanding. Model review is not reader testing. |
| [CDC Clear Communication Index](https://www.cdc.gov/ccindex/tool/index.html) | Communication can be reviewed with research-based criteria beyond word choice. | It was made for public communication. This skill does not claim an Index score without using the full method. |
| [W3C: use clear words](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o3p01-clear-words/) | Use familiar words and explain unusual terms. Apply this to labels, instructions, and errors too. | This is added accessibility guidance, not a stand-alone WCAG pass. Familiarity varies by reader. |
| [W3C: writing for web access](https://www.w3.org/WAI/tips/writing/) | Clear headings, useful link text, and short blocks help people use content. | Prose alone cannot prove an interface is accessible. |
| [W3C: reading level](https://www.w3.org/WAI/WCAG22/Understanding/reading-level.html) | Complex text may need a simpler version. Proper names and titles need special care in measurement. | WCAG's cited level is lower secondary, not grade 6. No wording suits every reader. English scores do not apply to every language. |
| [EPA: readability and pretesting](https://www.epa.gov/choose-fish-and-shellfish-wisely/readability-developing-and-pretesting-concepts-messages-materials) | Reading levels are rough clues. Some critical health material benefits from a grade 4 to 6 target. Use suitable tests and sample rules. | This is health-communication guidance, not proof of a universal grade target. It warns against sole reliance on formulas, including particular Flesch-Kincaid uses. |
| [CMS: testing with readers, chapter 1](https://www.cms.gov/Outreach-and-Education/Outreach/WrittenMaterialsToolkit/Downloads/ToolkitPart06Chapter01.pdf) | Reader feedback is key evidence that content can be understood and used. | The separate CMS Part 7 PDF could not be opened during research. Its unread contents are not used as evidence here. |
| [AI vendor guide: context engineering for agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Context includes instructions, tools, external data, and history. Keep useful context; use care with summaries and long runs. | Vendor guidance supports context selection, not unlimited memory access or a fixed universal inventory. |
| [Agent framework docs: session, state, and memory](https://adk.dev/sessions/) | Current session events, task state, and cross-session memory are distinct sources. | These are that framework's concepts. Other hosts may expose different stores or no memory. |
| [Microsoft: Human-AI Interaction guidelines](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/) | Check the first interaction, regular use, errors, and behavior over time. | Broad interaction research does not validate this exact writing skill. |
| [Microsoft HAX: recent interactions](https://www.microsoft.com/en-us/haxtoolkit/guideline/remember-recent-interactions/) | Recent context helps users refer back without repeating themselves. | Recall must stay within the host's access and privacy rules. |
| [MCP tools specification, 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | Tools have input schemas, result types, and error signals. | A versioned protocol is evidence for those boundaries, not a claim that every current host uses it. Plain prose must not break exact contracts. |
| [Liu et al., 2024: Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) | Tests found that information position can affect retrieval in long contexts. | The study tested particular models and tasks. It does not measure every current model or this skill. |
| [Liang et al., 2023: detector bias](https://arxiv.org/abs/2304.02819) | The tested detectors misclassified some non-native English writing and were sensitive to wording. | This is evidence against detector scores as this skill's quality gate, not proof that all later detectors behave alike. |

Resource gate: for package maintenance, run `mise run validate` first; ordinary use reads these files directly.

## Choices made for this skill

- Use plain-language review at every text-producing event. This extends the source guidance to an agent loop; it is an explicit skill rule, not a claim made by all sources.
- Use a broad context table plus a relevance test. The table covers known sources and events; the test catches new ones without forcing agents to fetch unrelated data.
- Keep grade 6 as the default English target, with narrow exceptions for exact or required specialist text. Require clear explanations where the format allows them.
- Check meaning before a reading score. A short sentence that loses “only” or a deadline is a worse result.
- Check both surface habits and deeper quality faults. [Human writing and slop](human-writing.md) links the wider writing research to rules for meaning, relevance, coherence, author voice, genre, and honest tone. Do not confuse a word pattern with proof of authorship.
- Ship plain Markdown without platform APIs, a required shell, runtime packages, or vendor-only activation fields. The skill can be read offline once installed.

## What validation can and cannot establish

Package checks can prove format and local links. Model trials can show behavior on the tested cases. Reading tools can estimate aspects of text difficulty. None proves that all future text will meet grade 6, that every reader will understand it, or that every host loads the skill.

For a host that needs strict enforcement, its owner must provide activation, context retention, event coverage, and output checks through that host's supported controls. This skill describes the needed behavior but does not install those controls.
