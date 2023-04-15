import dataclasses
import inspect
import itertools
from functools import cache, lru_cache
from typing import Dict, Tuple, Optional, Any, Callable


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
        if not isinstance(self.injectable_param, InjectableParameter):
            raise ValueError('injectable_param must be an instance of InjectableParameter')

        if not isinstance(self.signature_param, inspect.Parameter):
            raise ValueError('signature_param must be an instance of inspect.Parameter')

        self.injectable_param = self.injectable_param
        self.signature_param = self.signature_param

    @property
    def is_match_by_annotation(self) -> Optional[bool]:
        sig_param_annotation = str(self.signature_param.annotation)
        sig_param_annotation_is_generic = '[' in sig_param_annotation
        if sig_param_annotation_is_generic:
            return None

        return any(t for t in self.injectable_param.possible_types if issubclass(t, self.signature_param.annotation))

    @property
    def is_match_by_name(self) -> bool:
        return any(n for n in self.injectable_param.possible_names if n == self.signature_param.name)

    @property
    def is_match_contraindicated_by_annotation(self) -> bool:
        return self.signature_param.annotation != inspect.Parameter.empty and self.is_match_by_annotation != False

    @property
    def is_match_contraindicated_by_name(self) -> bool:
        return self.signature_param.name is not None and not self.is_match_by_name

    @property
    def is_strong_match(self) -> bool:
        return self.is_match_by_annotation and not self.is_match_contraindicated_by_name or \
               self.is_match_by_name and not self.is_match_contraindicated_by_annotation or \
               self.is_weak_match

    @property
    def is_weak_match(self) -> bool:
        return not self.is_match_contraindicated_by_name and not self.is_match_contraindicated_by_annotation

    def __hash__(self):
        return hash((self.injectable_param, self.signature_param))


def default_resolution_fallback(signature_param: inspect.Parameter) -> Optional[Any]:
    raise ValueError(f"Could not find a matching injectable for parameter '{signature_param.name}'")

def default_should_try_injection(signature_param: inspect.Parameter) -> bool:
    return True

@lru_cache(maxsize=128)
def prepare_action_params(action: callable, injectables: Tuple[InjectableParameter, ...], should_try_injection: Callable[[inspect.Parameter], bool] = default_should_try_injection, resolution_fallback: Callable[[inspect.Parameter], Optional[Any]] = default_resolution_fallback) -> tuple[tuple, dict]:
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
        lambda p: p.kind in (inspect.Parameter.POSITIONAL_ONLY,),
        signature_params))
    keyword_signature_params = tuple(itertools.dropwhile(lambda p: p in positional_signature_params, signature_params))

    result_args: Dict[int, callable] = {}

    # Look for strong matches for positional parameters first
    for signature_param_index in range(len(positional_signature_params)):
        signature_param = positional_signature_params[signature_param_index]
        if not should_try_injection(signature_param):
            continue

        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_strong_match:
                result_args[signature_param_index] = injectable_param.value_factory
                remaining_injectables = tuple(i for i in remaining_injectables if i != injectable_param)
                break

    # Then look for strong matches for keyword parameters
    result_kwargs: Dict[str, callable] = {}
    for signature_param in keyword_signature_params:
        if not should_try_injection(signature_param):
            continue
        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_strong_match:
                result_kwargs[signature_param.name] = injectable_param.value_factory
                remaining_injectables = tuple(i for i in remaining_injectables if i != injectable_param)
                break

    # Then look for weak matches for positional parameters
    for signature_param_index in range(len(positional_signature_params)):
        signature_param = positional_signature_params[signature_param_index]
        if signature_param_index in result_args:
            continue
        if not should_try_injection(signature_param):
            continue

        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_weak_match:
                result_args[signature_param_index] = injectable_param.value_factory
                remaining_injectables = tuple(i for i in remaining_injectables if i != injectable_param)
                break

        has_default_value = signature_param.default != inspect.Parameter.empty
        if not has_default_value:
            resolution_fallback_result = resolution_fallback(signature_param)
            if resolution_fallback_result is not None:
                result_kwargs[signature_param.name] = lambda: resolution_fallback_result

    # Then look for weak matches for keyword parameters
    for signature_param in keyword_signature_params:
        if signature_param.name in result_kwargs:
            continue
        if not should_try_injection(signature_param):
            continue

        for injectable_param_index in range(len(remaining_injectables)):
            injectable_param = remaining_injectables[injectable_param_index]
            comparison = injectable_param.compare_to(signature_param)

            if comparison.is_weak_match:
                result_kwargs[signature_param.name] = injectable_param.value_factory
                remaining_injectables = tuple(i for i in remaining_injectables if i != injectable_param)
                break

        has_default_value = signature_param.default != inspect.Parameter.empty
        if not has_default_value:
            resolution_fallback_result = resolution_fallback(signature_param)
            if resolution_fallback_result is not None:
                result_kwargs[signature_param.name] = lambda: resolution_fallback_result

    result_args_values = tuple(result_args[i]() for i in range(len(result_args)))
    result_kwargs_values = {k: v() for k, v in result_kwargs.items()}
    return result_args_values, result_kwargs_values
