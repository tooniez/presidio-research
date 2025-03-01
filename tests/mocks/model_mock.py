from typing import List, Optional

from presidio_evaluator import InputSample
from presidio_evaluator.models import BaseModel


class MockModel(BaseModel):

    def predict(self, sample: InputSample, **kwargs) -> List[str]:
        pass

    def batch_predict(self, dataset: List[InputSample], **kwargs) -> List[List[str]]:
        return [self.predict(sample, **kwargs) for sample in dataset]



class MockTokensModel(BaseModel):
    """
    Simulates a real model, returns the prediction given in the constructor
    """

    def __init__(
        self,
        prediction: Optional[List[str]],
        entities_to_keep: List = None,
        verbose: bool = False,
        **kwargs
    ):
        super().__init__(entities_to_keep=entities_to_keep, verbose=verbose, **kwargs)
        self.prediction = prediction

    def predict(self, sample: InputSample, **kwargs) -> List[str]:
        return self.prediction

    def batch_predict(self, dataset: List[InputSample], **kwargs) -> List[List[str]]:
        return [self.predict(sample, **kwargs) for sample in dataset]


class IdentityTokensMockModel(BaseModel):
    """
    Simulates a real model, always return the label as prediction
    """

    def __init__(self, verbose: bool = False):
        super().__init__(verbose=verbose)

    def predict(self, sample: InputSample, **kwargs) -> List[str]:
        return sample.tags

    def batch_predict(self, dataset: List[InputSample], **kwargs) -> List[List[str]]:
        return [sample.tags for sample in dataset]


class FiftyFiftyIdentityTokensMockModel(BaseModel):
    """
    Simulates a real model, returns the label or no predictions (list of 'O')
    alternately
    """

    def __init__(self, entities_to_keep: List = None, verbose: bool = False):
        super().__init__(entities_to_keep=entities_to_keep, verbose=verbose)
        self.counter = 0

    def predict(self, sample: InputSample, **kwargs) -> List[str]:
        self.counter += 1
        if self.counter % 2 == 0:
            return sample.tags
        else:
            return ["O" for i in range(len(sample.tags))]

    def batch_predict(self, dataset: List[InputSample], **kwargs) -> List[List[str]]:
        return [self.predict(sample, **kwargs) for sample in dataset]
