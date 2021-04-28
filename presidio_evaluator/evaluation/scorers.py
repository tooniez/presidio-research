"""E2E scoring pipelines for the different models"""

import math
from typing import List, Optional

from presidio_analyzer import EntityRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine

from presidio_evaluator import InputSample
from presidio_evaluator.data_generator import read_synth_dataset
from presidio_evaluator.evaluation import EvaluationResult, Evaluator
from presidio_evaluator.models import (
    PresidioRecognizerWrapper,
    PresidioAnalyzerWrapper,
    BaseModel,
)


def score_model(
    model: BaseModel,
    entities_to_keep: List[str],
    input_samples: List[InputSample],
    verbose: bool = False,
    beta: float = 2.5,
) -> EvaluationResult:
    """
    Run data through a model and gather results and stats
    """

    print("Evaluating samples")

    evaluator = Evaluator(model=model, entities_to_keep=entities_to_keep)
    evaluated_samples = evaluator.evaluate_all(input_samples)

    print("Estimating metrics")
    evaluation_result = evaluator.calculate_score(
        evaluation_results=evaluated_samples, beta=beta
    )
    precision = evaluation_result.pii_precision
    recall = evaluation_result.pii_recall
    entity_recall = evaluation_result.entity_recall_dict
    entity_precision = evaluation_result.entity_precision_dict
    f = evaluation_result.pii_f
    errors = evaluation_result.model_errors
    #
    print(f"precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F {beta}: {f}")
    print(f"Precision per entity: {entity_precision}")
    print(f"Recall per entity: {entity_recall}")

    if verbose:

        false_negatives = [
            str(mistake) for mistake in errors if mistake.error_type == "FN"
        ]
        false_positives = [
            str(mistake) for mistake in errors if mistake.error_type == "FP"
        ]
        other_mistakes = [
            str(mistake) for mistake in errors if mistake.error_type not in ["FN", "FP"]
        ]

        print("False negatives: ")
        print("\n".join(false_negatives))
        print("\n******************\n")

        print("False positives: ")
        print("\n".join(false_positives))
        print("\n******************\n")

        print("Other mistakes: ")
        print("\n".join(other_mistakes))

    return evaluation_result


def score_presidio_recognizer(
    recognizer: EntityRecognizer,
    entities_to_keep: List[str],
    input_samples: Optional[List[InputSample]] = None,
    labeling_scheme: str = "BILUO",
    with_nlp_artifacts: bool = False,
    verbose: bool = False,
) -> EvaluationResult:
    """
    Run data through one EntityRecognizer and gather results and stats
    """

    if not input_samples:
        print("Reading dataset")
        input_samples = read_synth_dataset("../../data/synth_dataset.txt")
    else:
        input_samples = list(input_samples)

    print("Preparing dataset by aligning entity names to Presidio's entity names")

    updated_samples = Evaluator.align_entity_types(input_samples)

    model = PresidioRecognizerWrapper(
        recognizer=recognizer,
        entities_to_keep=entities_to_keep,
        labeling_scheme=labeling_scheme,
        nlp_engine=SpacyNlpEngine(),
        with_nlp_artifacts=with_nlp_artifacts,
    )
    return score_model(
        model=model,
        entities_to_keep=entities_to_keep,
        input_samples=updated_samples,
        verbose=verbose,
    )


def score_presidio_analyzer(
    input_samples: Optional[List[InputSample]] = None,
    entities_to_keep: Optional[List[str]] = None,
    labeling_scheme: str = "BILUO",
    verbose: bool = True,
) -> EvaluationResult:
    """"""
    if not input_samples:
        print("Reading dataset")
        input_samples = read_synth_dataset("../../data/synth_dataset.txt")
    else:
        input_samples = list(input_samples)

    print("Preparing dataset by aligning entity names to Presidio's entity names")

    updated_samples = Evaluator.align_entity_types(input_samples)

    flatten = lambda l: [item for sublist in l for item in sublist]
    from collections import Counter

    count_per_entity = Counter(
        [
            span.entity_type
            for span in flatten(
                [input_sample.spans for input_sample in updated_samples]
            )
        ]
    )
    if verbose:
        print("Count per entity:")
        print(count_per_entity)
    analyzer = PresidioAnalyzerWrapper(
        entities_to_keep=entities_to_keep, labeling_scheme=labeling_scheme
    )

    return score_model(
        model=analyzer,
        entities_to_keep=list(count_per_entity.keys()),
        input_samples=updated_samples,
        verbose=verbose,
    )


if __name__ == "__main__":
    score_presidio_analyzer()
