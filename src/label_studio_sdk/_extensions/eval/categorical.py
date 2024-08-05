from typing import List, Dict, Iterable
from sklearn.metrics import precision_recall_fscore_support


def _get_single_choice(annotation: Dict):
    """
    Get the single choice from the annotation.

    Args:
        annotation: Annotation dict

    Returns:
        Single choice
    """
    maybe_choice = next((r['value']['choices'][0] for r in annotation['result'] if r['type'] == 'choices'), None)
    if maybe_choice:
        return maybe_choice
    raise NotImplementedError('Only single choice is supported')


def get_precision_recall_f1_per_choice(annotations: Iterable[Dict], predictions: Iterable[Dict]) -> Dict:
    """
    Given the iterator over annotations and predictions, calculate precision, recall, and F1 per choice.
    Each annotation and prediction follows the format of the Label Studio output.

    Args:
        annotations: Iterable of annotation dicts
        predictions: Iterable of prediction dicts

    Returns:
        Dict with keys as choice names and values as tuples of (precision, recall, f1)
    """

    annotation_choices = [_get_single_choice(annotation) for annotation in annotations]
    prediction_choices = [_get_single_choice(prediction) for prediction in predictions]
    # get unique choices names
    unique_choices = sorted(set(annotation_choices + prediction_choices))

    metrics_per_choice = precision_recall_fscore_support(
        annotation_choices, prediction_choices,
        average=None, labels=unique_choices)

    results = {}
    for choice, metrics in zip(unique_choices, metrics_per_choice):
        results[choice] = {
            'precision': metrics[0],
            'recall': metrics[1],
            'f1': metrics[2],
        }

    return results
