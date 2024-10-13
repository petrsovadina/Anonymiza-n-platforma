from typing import List, Optional
import re
from presidio_analyzer import EntityRecognizer, RecognizerResult, Pattern

class CzechNameRecognizer(EntityRecognizer):
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "PERSON",
        context: Optional[List[str]] = None,
    ):
        self.patterns = [
            Pattern(
                name="czech_full_name",
                regex=r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+(\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+){1,3}\b",
                score=0.85,
            ),
        ]
        super().__init__(
            supported_entities=[supported_entity],
            supported_language=supported_language,
            context=context,
        )

    def load(self) -> None:
        # Není potřeba nic načítat
        pass

    def analyze(self, text: str, entities: List[str], nlp_artifacts: None) -> List[RecognizerResult]:
        results = []
        for pattern in self.patterns:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                start, end = match.span()
                results.append(
                    RecognizerResult(
                        entity_type=self.supported_entities[0],
                        start=start,
                        end=end,
                        score=pattern.score,
                    )
                )
        return results

class CzechAddressRecognizer(EntityRecognizer):
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "ADDRESS",
        context: Optional[List[str]] = None,
    ):
        self.patterns = [
            Pattern(
                name="czech_address",
                regex=r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+(\s+\d+(/\d+[A-Z]?)?),?\s+\d{3}\s+\d{2}\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]+\b",
                score=0.6,
            ),
        ]
        super().__init__(
            supported_entities=[supported_entity],
            supported_language=supported_language,
            context=context,
        )

    def load(self) -> None:
        # Není potřeba nic načítat
        pass

    def analyze(self, text: str, entities: List[str], nlp_artifacts: None) -> List[RecognizerResult]:
        results = []
        for pattern in self.patterns:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                start, end = match.span()
                results.append(
                    RecognizerResult(
                        entity_type=self.supported_entities[0],
                        start=start,
                        end=end,
                        score=pattern.score,
                    )
                )
        return results

class CzechDateRecognizer(EntityRecognizer):
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "DATE",
        context: Optional[List[str]] = None,
    ):
        self.patterns = [
            Pattern(
                name="czech_date",
                regex=r"\b\d{1,2}\.\s*(ledna|února|března|dubna|května|června|července|srpna|září|října|listopadu|prosince)\s*\d{4}\b",
                score=0.85,
            ),
            Pattern(
                name="czech_date_numeric",
                regex=r"\b\d{1,2}\.\s*\d{1,2}\.\s*\d{4}\b",
                score=0.85,
            ),
        ]
        super().__init__(
            supported_entities=[supported_entity],
            supported_language=supported_language,
            context=context,
        )

    def load(self) -> None:
        pass

    def analyze(self, text: str, entities: List[str], nlp_artifacts: None) -> List[RecognizerResult]:
        results = []
        for pattern in self.patterns:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                start, end = match.span()
                results.append(
                    RecognizerResult(
                        entity_type=self.supported_entities[0],
                        start=start,
                        end=end,
                        score=pattern.score,
                    )
                )
        return results

class CzechPhoneRecognizer(EntityRecognizer):
    def __init__(
        self,
        supported_language: str = "cs",
        supported_entity: str = "PHONE_NUMBER",
        context: Optional[List[str]] = None,
    ):
        self.patterns = [
            Pattern(
                name="czech_phone",
                regex=r"\b(\+420)?\s*\d{3}\s*\d{3}\s*\d{3}\b",
                score=0.85,
            ),
        ]
        super().__init__(
            supported_entities=[supported_entity],
            supported_language=supported_language,
            context=context,
        )

    def analyze(self, text: str, entities: List[str], nlp_artifacts: None) -> List[RecognizerResult]:
        results = []
        for pattern in self.patterns:
            matches = re.finditer(pattern.regex, text)
            for match in matches:
                start, end = match.span()
                results.append(
                    RecognizerResult(
                        entity_type=self.supported_entities[0],
                        start=start,
                        end=end,
                        score=pattern.score,
                    )
                )
        return results

def create_czech_custom_recognizers():
    return [
        CzechNameRecognizer(),
        CzechDateRecognizer(),
        CzechPhoneRecognizer(),
    ]
