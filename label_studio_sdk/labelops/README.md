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

Now it's time to search and label patterns by using the list of LabelOps. For example:

```python
result = label_ops.apply([{
    "name": "Product Positive Feedback",
    "label": "Positive",
    "pattern": [{
        "type": "Regex",
        "query": {
            "text": ".*great*"
        }
    }]
}])
```

## LabelOp

Each LabelOp is a JSON dict with the following structure:

- **name**: any arbitrary name, unique across current LabelOps
- **label**: label to be assigned by this LabelOp
- **pattern**: list of [patterns](#patterns) to search for.

## Patterns

Each pattern consists of 2 fields:

- **type**: the type of the pattern
- **query**: pattern's query. Each query is a JSON dict where keys define which field in task.data is used for search, and values are actual queries.

### Pattern queries

| `"type"`           | Description                                                                   | `"query"`                                                                                                                                                                                                                                                                                           | Example                                                                                                                  |
|--------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `"RawQuery"`       | Lowest-level raw query string                                                 | String that forms [Cypher WHERE](https://neo4j.com/docs/cypher-manual/current/clauses/where/) clause. There are 3 variables available to search over annotation graph: `d` (data node), `r` (region node) and `l` (label node)                                                                      | `d.text =~ '.*great.*' AND l.label = 'PRODUCT'`                                                                          |
| `"Regex"`          | Regular expression                                                            | [Java Regular expression](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/regex/Pattern.html) string                                                                                                                                                                         | `{"text": ".*great*"}`                                                                                                   |
| `"Entity"`         | Any generic entity of any type                                                | JSON dict with 2 keys: <ul><li>`"label"` - entity name.<li>`"type"` - entity type</ul>                                                                                                                                                                                                              | `{"text": {"label": "PRODUCT", "type": "ner"}}`                                                                          |
| `"NamedEntity"`    | Named entity extracted from text                                              | String that represents a named entity (`"CARDINAL"`, `"DATE"`, `"EVENT"`, `"FAC"`, `"GPE"`, `"LANGUAGE"`, `"LAW"`, `"LOC"`, `"MONEY"`, `"NORP"`, `"ORDINAL"`, `"ORG"`, `"PERCENT"`, `"PERSON"`, `"PRODUCT"`, `"QUANTITY"`, `"TIME"`, `"WORK_OF_ART"`                                                | `{"text": "PRODUCT"}`                                                                                                    |
| `"POSTag"`         | Part-of-Speech Tag                                                            | String that represents a part-of-speech tag ([check list of all available tags](https://spacy.io/usage/linguistic-features#pos-tagging))                                                                                                                                                            | `{"text": NOUN"}`                                                                                                        |
| `"Sentiment"`      | Sentiment analyzer                                                            | String that represents sentiment analysis result (`"positive"`, `"negative"`)                                                                                                                                                                                                                       | `{"text": "positive"}`                                                                                                   |
| `"EntitySequence"` | The sequence of generic entities                                              | JSON list that represents a directional path of connected entities. Each entity follows the same format as in `"Entity"` type.                                                                                                                                                                      | `{"text": [{"label": "VERB", "type": "head"}, {"label": "PRODUCT", "type": "ner"}] `                                     |
| `"Dependency"`     | Dependency parsing result in the form of head POS tag pointed to named entity | JSON list of 2 items: head [POS tag](https://spacy.io/usage/linguistic-features#pos-tagging) followed by named entity.                                                                                                                                                                              | `{"text": ["VERB", "PRODUCT"]} `                                                                                         |
| `"Prediction"`     | Prediction stored in Label Studio                                             | JSON dict with the following fields (check [Label Studio Prediction format](https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks) for details):  <ul><li>`"model_version"` - model version.<li>`"from_name"` - control tag name <li> `"label"` - predicted label</ul> | `{"text": {"model_version": "cardiffnlp/twitter-roberta-base-sentiment", "from_name": "my_label", "label": "LABEL_2"}} ` |
