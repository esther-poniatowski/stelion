# Writing Standards

Prose conventions for all documentation in this ecosystem: README files,
CONTRIBUTING guides, user guides, architecture documents, and ADR files.

These standards are the single authoritative source for writing rules.
The [documentation audit prompt](../audits/audit-documentation.md) enforces
them; individual projects must not redefine them.

---

## 1. Nominalization

Process nouns (`-tion`, `-ment`, `-ness`, `-ity`, `-ence`, `-ance`, `-ing`
as noun) must be replaced by the corresponding verb form when the verb is
shorter or more direct.

The rule applies in both subject and object position:

| Violation | Rewrite |
|---|---|
| "Spectral reshaping produces ..." | "The spectrum reshapes into ..." |
| "automation of dependency management" | "automates dependency management" |

**Adjective-position exception.** A nominalization that modifies another noun
as an adjective is acceptable: "configuration file", "validation rules",
"installation instructions".

**Lexicalized-noun exception.** Nouns that have become standard technical
terms and no longer carry an active verbal sense in context are acceptable:
"documentation", "implementation" when referring to artifacts (not processes);
"configuration" when referring to a file or object (not the act of
configuring).

---

## 2. Framing

Sentences must state results directly, not describe the act of establishing
them.

**Forbidden literal strings** (search mechanically):
- `the role of`
- `the nature of`
- `the act of`
- `plays a role in`
- `is responsible for`
- `is involved in`

**Vague procedural nominalizations.** A noun phrase referring to a process,
comparison, or relation must name its arguments explicitly:

| Violation | Rewrite |
|---|---|
| "the comparison" | "the comparison between X and Y" |
| "the integration" | "integrating A into B" |

**Concrete-subject rule.** The grammatical subject must be the actual object
or result, not the document, section, or tool:

| Violation | Rewrite |
|---|---|
| "This section derives the factorization of X" | "The ratio X factorizes into ..." |

---

## 3. Pronoun Discipline

### 3.1 Subjective Pronouns

The following are forbidden in all documentation prose:
- `you`, `your`
- `we`, `our`

Rewrite using impersonal constructions, the tool name as subject, or passive
voice.

### 3.2 Bare Pronouns (B6 Rule)

Sentences must not begin with `It`, `This`, `These`, or `They` without a
descriptive noun phrase immediately following the pronoun.

| Violation | Rewrite |
|---|---|
| "It follows that ..." | "This property follows from ..." |
| "This is necessary." | "This constraint is necessary." |

**Test:** if the pronoun can be replaced by a descriptive noun phrase that
adds information, the pronoun is bare.

---

## 4. Modifier Discipline

### 4.1 Compound-Modifier Rule

Any pre-nominal compound modifier that encodes a prepositional or clausal
relationship must be expanded:
- `-dependent`, `-determined`, `-driven`, `-weighted`, `-modulated`
- any stacked modifier sequence of two or more pre-nominal terms encoding a
  clausal relationship

Pattern: `[X]-dependent [noun]` → `[noun] that depends on [X]`.

**Lexicalized-compound exception.** Standard English adjectives that have
become lexicalized are acceptable and must NOT be expanded:
- `machine-readable`, `open-source`, `command-line`, `real-time`, `built-in`

### 4.2 Case-Scaffolding Rule

"The ... case" as a noun phrase and "In the ... case" as a sentence opener
are forbidden:

| Violation | Rewrite |
|---|---|
| "in the single-population case" | "for a single population" |
| "the commutative case" | "with commutative overlaps" |

---

## 5. Sentence Economy

Verbose constructions that increase cognitive load without proportional
informational gain must be eliminated.

**Forbidden patterns:**
- **Verbose preambles**: "It provides the following benefits:", "This tool
  introduces a centralized and extensible X that consolidates Y into Z."
- **Redundant lead-ins**: "In order to", "For the purpose of", "It is
  important to note that"
- **Long enumerations**: more than four items inlined in a single sentence
  (move to a list or split)
- **Stacked nominalizations**: chains of three or more abstract nouns acting
  as a compound subject or object
- **Double framing**: a sentence that frames an upcoming list AND the list
  items each re-frame their own content

---

## 6. Information Architecture

### 6.1 First Sentence

The opening sentence before the Table of Contents must convey the core
purpose directly. Feature lists belong in the Features section, not in the
opening description.

### 6.2 Document Structure

- A document must not open with mechanical content (badges, install commands)
  before establishing what the tool does.
- Installation must follow purpose, configuration must follow usage.
- Heading levels must not be skipped. Heading casing and depth must be
  consistent across sibling documents.
- Significant prose must not sit outside any heading.

---

## 7. Cross-Document Consistency

Parallel documents across projects must follow identical conventions:

- Installation sections: same header names, same intro patterns, same
  ordering.
- README structure: same section ordering and heading conventions across
  projects following the keystone template.
- ADR files: consistent voice, tense, and structure.
- Guide voice: impersonal voice throughout (no mixing with `you`-addressing).
