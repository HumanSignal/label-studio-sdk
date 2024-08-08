import logging
from typing import List, Dict, Iterable

logger = logging.getLogger(__name__)

try:
    # TODO: after python 3.8 support is dropped (Oct'24), remove try-except block
    from sklearn.metrics import precision_recall_fscore_support
except ImportError:
    logger.warning('scikit-learn is not installed. Please install scikit-learn to use this module.')
    precision_recall_fscore_support = None


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
        Dict of the following format:
        {
            'precision': {
                'choice1': 0.5,
                'choice2': 0.7,
                ...
            },
            'recall': {
                'choice1': 0.5,
                'choice2': 0.7,
                ...
            },
            'f1': {
                'choice1': 0.5,
                'choice2': 0.7,
                ...
            },
            'support': {
                'choice1': 10,
                'choice2': 20,
                ...
            },
        }
    """

    if precision_recall_fscore_support is None:
        raise ImportError('scikit-learn is not installed. Please install scikit-learn to use this module.')

    annotation_choices = [_get_single_choice(annotation) for annotation in annotations]
    prediction_choices = [_get_single_choice(prediction) for prediction in predictions]
    # get unique choices names
    unique_choices = sorted(set(annotation_choices + prediction_choices))

    metrics_per_choice = precision_recall_fscore_support(
        annotation_choices, prediction_choices,
        average=None, labels=unique_choices)

    results = {}
    for metric_name, metric_per_choice in zip(['precision', 'recall', 'f1', 'support'], metrics_per_choice):
        results[metric_name] = {}
        for choice, metric in zip(unique_choices, metric_per_choice):
            results[metric_name][choice] = metric

    return results
