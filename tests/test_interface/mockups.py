import json

# Example of the output of summary table for a specific project
# project_id  created_at                  all_data_columns               common_data_columns    created_annotations                                    created_labels                                                created_labels_drafts
# ----------  --------------------------  -----------------------------  ---------------------  -----------------------------------------------------  ------------------------------------------------------------  ----------------------------------------------------
# 9           2024-03-02 20:47:43.710926  {"text": 20, "sentiment": 20}  ["sentiment", "text"]  {"label|text|labels": 2, "sentiment|text|choices": 2}  {"label": {"PER": 1, "ORG": 1}, "sentiment": {"Positive": 1,  {"label": {"MISC": 1}, "sentiment": {"Negative": 1}}
#                                                                                                                                                       "Negative": 1}}


class SummaryMockup:
    """
    """

    created_labels = json.loads(
        '{"label": {"PER": 1, "ORG": 1}, "sentiment": {"Positive": 1, "Negative": 1}}'
    )
    created_labels_drafts = json.loads(
        '{"label": {"MISC": 1}, "sentiment": {"Negative": 1}}'
    )
    created_annotations = json.loads(
        '{"label|text|labels": 2, "sentiment|text|choices": 2}'
    )
