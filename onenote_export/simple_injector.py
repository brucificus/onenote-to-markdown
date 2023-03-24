import dataclasses
import inspect
import itertools
from functools import cache, lru_cache
from typing import Dict, Tuple


@dataclasses.dataclass
class InjectableParameter:
    possible_names: tuple[str, ...]
    possible_types: tuple[type, ...]
    value_factory: callable

    def __post_init__(self):
        self.possible_names = tuple(self.possible_names)
        self.possible_types = tuple(self.possible_types)

        if not self.possible_names:
            raise ValueError('possible_names must not be empty')
        if not self.possible_types:
            raise ValueError('possible_types must not be empty')
        if not callable(self.value_factory):
            raise ValueError('value_factory must be callable')

    def compare_to(self, signature_param: inspect.Parameter) -> 'InjectableParameterSignatureComparison':
        return InjectableParameterSignatureComparison(self, signature_param)

    def __hash__(self):
        return hash((self.possible_names, self.possible_types, self.value_factory))


@dataclasses.dataclass
class InjectableParameterSignatureComparison:
    injectable_param: InjectableParameter
    signature_param: inspect.Parameter

    def __post_init__(self):
        self.injectable_param = self.injectable_param
        self.signature_param = self.signature_param

    @property
    @cache
    def is_match_by_annotation(self) -> bool:
        return any([t for t in self.injectable_param.possible_types if issubclass(t, self.signature_param.annotation)])

    @property
    @cache
    def is_match_by_name(self) -> bool:
        return any([n for n in self.injectable_param.possible_names if n == self.signature_param.name])

    @property
    @cache
    def is_match_contraindicated_by_annotation(self) -> bool:
        return self.signature_param.annotation != inspect.Parameter.empty and not self.is_match_by_annotation

    @property
    @cache
    def is_match_contraindicated_by_name(self) -> bool:
        return self.signature_param.name is not None and not self.is_match_by_name

    @property
    @cache
    def is_strong_match(self) -> bool:
        return self.is_match_by_annotation and not self.is_match_contraindicated_by_name or \
               self.is_match_by_name and not self.is_match_contraindicated_by_annotation or \
               self.is_weak_match

    @property
    @cache
    def is_weak_match(self) -> bool:
        return not self.is_match_contraindicated_by_name and not self.is_match_contraindicated_by_annotation

    def __hash__(self):
        return hash((self.injectable_param, self.signature_param))


@lru_cache(maxsize=128)
def prepare_action_params(action: callable, injectables: Tuple[InjectableParameter, ...]) -> tuple[tuple, dict]:
    """Returns a tuple of the parameters of the provided action."""

    signature_params = list(inspect.signature(action).parameters.values())
    remaining_injectables = injectables

    if len(signature_params) == 0:
        return (), {}

    if signature_params[0].name == 'self':
        signature_params = signature_params[1:]
        if len(signature_params) == 0:
            return (), {}

    positional_signature_params = tuple(itertools.takewhile(
        lambda p: p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD),
        signature_params))
    keyword_signature_params = tuple(itertools.dropwhile(lambda p: p in positional_signature_params, signature_params))

    result_args: Dict[int, callable] = {}

    # Look for strong matches for positional parameters first
    for signature_param_index in range(len(positional_signature_params)):
        signature_param = positional_signature_params[signature_param_index]

        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_strong_match:
                result_args[signature_param_index] = injectable_param.value_factory
                remaining_injectables = remaining_injectables[:injectable_param_index] \
                                        + remaining_injectables[injectable_param_index + 1:]
                break

    # Then look for strong matches for keyword parameters
    result_kwargs: Dict[str, callable] = {}
    for signature_param in keyword_signature_params:
        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_strong_match:
                result_kwargs[signature_param.name] = injectable_param.value_factory
                remaining_injectables = remaining_injectables[:injectable_param_index] \
                                        + remaining_injectables[injectable_param_index + 1:]
                break

        has_default_value = signature_param.default != inspect.Parameter.empty
        if not has_default_value:
            raise ValueError(f'Could not find a matching injectable for required parameter {signature_param.name} of {action.__name__}')

    # Then look for weak matches for positional parameters
    for signature_param_index in range(len(positional_signature_params)):
        signature_param = positional_signature_params[signature_param_index]
        if signature_param_index in result_args:
            continue

        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_weak_match:
                result_args[signature_param_index] = injectable_param.value_factory
                remaining_injectables = remaining_injectables[:injectable_param_index] \
                                        + remaining_injectables[injectable_param_index + 1:]
                break

        has_default_value = signature_param.default != inspect.Parameter.empty
        if not has_default_value:
            raise ValueError(f'Could not find a matching injectable for required parameter {signature_param.name} of {action.__name__}')

    # Then look for weak matches for keyword parameters
    for signature_param in keyword_signature_params:
        if signature_param.name in result_kwargs:
            continue

        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_weak_match:
                result_kwargs[signature_param.name] = injectable_param.value_factory
                remaining_injectables = remaining_injectables[:injectable_param_index] \
                                        + remaining_injectables[injectable_param_index + 1:]
                break

        has_default_value = signature_param.default != inspect.Parameter.empty
        if not has_default_value:
            raise ValueError(f'Could not find a matching injectable for required parameter {signature_param.name} of {action.__name__}')

    result_args_values = tuple([result_args[i]() for i in range(len(result_args))])
    result_kwargs_values = {k: v() for k, v in result_kwargs.items()}
    return result_args_values, result_kwargs_values
