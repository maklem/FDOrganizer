# Questionnaire Fields

>[!NOTE]
>
> Adding questions does not make them appear in any output.
> They are saved in the database, but not beyond.

## Relevant files

* `server/static/schema.json`
  * stores questions and types of answers (string-type, mono/multi-select, answer-count, ...)
* `server/static/js/metadata/metadata-sections.js`
  * declares with question is part of which section
* `server/static/js/metadata/state.js`
  * in `function splitSchema(schema)`
    * defines sections in program
    * section `required` is derived automatically from `schema.json` where questions have "min answers > 0"
  * in `const LABELS = { ... }`
    * defines section titles

## adding a new questions

1. A new question needs to be defined in `schema.json`. See the examples within to construct a new question.

2. Add the question to a section.
   Unless the question requires at least one answer, add it by its id to a section in `metadata-sections.js`

## adding a new section

1. create a label in `const LABELS` in `state.js`

2. create a section in `function splitSchema(schema)` in `state.js`

3. create a new question and assign it to the new section (see above)
