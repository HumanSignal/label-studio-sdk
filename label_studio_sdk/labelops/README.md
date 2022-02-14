# LabelOps

**LabelOps** is a framework for labeling automation inside Label Studio. The core idea behind LabelOps boils down to 2 general steps:

1. Search for specific _Patterns_ in Label Studio tasks
2. Assign labels to these Patterns

## Start using LabelOps

To start using LabelOps with python SDK, first create and initialize client instance attached to a specific `project_id` in Label Studio

```python
from label_studio_sdk.labelops import LabelOps

label_ops = LabelOps(project_id=123, api_key='LABEL-STUDIO-ACCESS-TOKEN')
label_ops.initialize_project()
```

Now it's time to search and label patterns by using LabelOps. For example:

```python
result = label_ops.apply([{
    "name": "Product Positive Feedback",
    "label": "Positive",
    "pattern": [{
        "type": "Contains",
        "query": "great product"
    }]
}])
```

Each item in a list of objects provided to `apply()` function represents an individual Labeling Operation (LabelOp),
that filters _regions_ based on a search `"pattern"` and assign a `"label"` to retrieved results. Each _region_ refers to an entire task, or selected region within particular task. To understand more, please address [Label Studio Data Model]() section.

## LabelOp

Each LabelOp is a JSON dict with the following structure:

- **name**: any arbitrary name, unique across current LabelOps
- **label**: label to be assigned by this LabelOp
- **pattern**: list of [patterns](#patterns) to search for. When multiple patterns are presented, the returning result is an intersection of specified conditions, e.g. when there are two `"Contains"` patterns with queries `"great"` and `"product"` - it searches for all regions where `"great"` and `"product"` both simultaneously presented.

## Patterns

Each pattern consists of the following fields:

- **type**: the type of the pattern
- **query**: pattern's query. Depending on pattern's type, query could be string or dict
- **field** (optional): specific Label Studio task data field for which search is performed. By default, search is made over all available fields.
- **context** (optional): boolean field that defines if search to be done in the context of target _region_. For example, you may want to search and label a specific `PRODUCT` entity in all strings that start from `Great...`. The following pattern config makes this job:
    ```json
    [{
      "type": "NamedEntity",
      "query": "PRODUCT"
    }, {
      "type": "StartsWith",
      "query": "Great",
      "context": true
    }]
    ```
    By default, non-contextual search is performed. 
- **id** (optional): pattern ID (could be used for debug purposes)
- other parameters depending on pattern's type (check table bellow)

### Pattern queries

| type               | Description                                                                   | query                                                                                                                                                                                                                                                                                                                                             | Example                                                                                                                                | Additional parameters                                                              |
|--------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| `"RawQuery"`       | Lowest-level raw query string                                                 | [Cypher query](https://neo4j.com/developer/cypher/). This query will be executed as [subquery](https://neo4j.com/docs/cypher-manual/current/clauses/call-subquery/) therefore `MATCH` clause should include `(r)` node that is reserved for searching regions                                                                                     | `MATCH (d:Data {field: "text"})-->(r)-->(l:Label) <br/>WHERE d.data =~ '.*great.*' AND l.label = 'PRODUCT'<br/>RETURN "unique_result"` ||
| `"Contains"`       | Substring search                                                              | Substring to be searched for exact match                                                                                                                                                                                                                                                                                                          | `"great"`                                                                                                                              ||
| `"StartsWith"`     | Prefix search                                                                 | Prefix to be searched for exact match                                                                                                                                                                                                                                                                                                             | `"Great "`                                                                                                                             ||
| `"Regex"`          | Regular expression                                                            | [Java Regular expression](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/regex/Pattern.html) string                                                                                                                                                                                                                       | `".*great*"`                                                                                                                           ||
| `"FullText"`       | Full text search                                                              | Full text search powered by [full text index](https://neo4j.com/docs/cypher-manual/current/indexes-for-full-text-search/)                                                                                                                                                                                                                         | `"great product"`                                                                                                                      | `"threshold"` (optional) - determines minimal threshold value for retrieved scores |
| `"TextDistance"`   | Textual distance                                                              | Search based on Levenshtein text distance                                                                                                                                                                                                                                                                                                         | `"great product"`                                                                                                                      | `"threshold"` - determines maximal char distance                                   |
| `"Entity"`         | Any generic entity of any type                                                | JSON dict with 2 keys: <ul><li>`"label"` - entity name.<li>`"type"` - entity type</ul>.                                                                                                                                                                                                                                                           | `{"label": "PRODUCT", "type": "ner"}`                                                                                                  ||
| `"NamedEntity"`    | Named entity extracted from text                                              | String that represents a named entity (`"CARDINAL"`, `"DATE"`, `"EVENT"`, `"FAC"`, `"GPE"`, `"LANGUAGE"`, `"LAW"`, `"LOC"`, `"MONEY"`, `"NORP"`, `"ORDINAL"`, `"ORG"`, `"PERCENT"`, `"PERSON"`, `"PRODUCT"`, `"QUANTITY"`, `"TIME"`, `"WORK_OF_ART"`                                                                                              | `"PRODUCT"`                                                                                                                            ||
| `"POSTag"`         | Part-of-Speech Tag                                                            | String that represents a part-of-speech tag ([check list of all available tags](https://spacy.io/usage/linguistic-features#pos-tagging))                                                                                                                                                                                                          | `"NOUN"`                                                                                                                               ||
| `"Sentiment"`      | Sentiment analyzer                                                            | String that represents sentiment analysis result (`"positive"`, `"negative"`)                                                                                                                                                                                                                                                                     | `"positive"`                                                                                                                           ||
| `"EntitySequence"` | The sequence of generic entities                                              | JSON list that represents a directional path of connected entities. Each entity follows the same format as in `"Entity"` type.                                                                                                                                                                                                                    | `[{"label": "VERB", "type": "head"}, {"label": "PRODUCT", "type": "ner"}] `                                                            ||
| `"Dependency"`     | Dependency parsing result in the form of head POS tag pointed to named entity | JSON list of 2 items: head [POS tag](https://spacy.io/usage/linguistic-features#pos-tagging) followed by named entity.                                                                                                                                                                                                                            | `["VERB", "PRODUCT"]`                                                                                                                  ||
| `"Prediction"`     | Prediction stored in Label Studio                                             | JSON dict with the following fields (check [Label Studio Prediction format](https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks) for details):  <ul><li>`"model_version"` - model version.<li>`"from_name"` - control tag name <li> `"label"` - predicted label <li> `"score"` - lowest model score threshold</ul> | `{"model_version": "cardiffnlp/twitter-roberta-base-sentiment", "from_name": "my_label", "label": "LABEL_2"}} `                        ||
