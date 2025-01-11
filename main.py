from enum import Int
from functools import wraps
from services import get_instance_manager
from sims4.resources import Types
from sims.occult.occult_enums import OccultType
from sims.sim_info_types import Species, Age
from sims.sim import Sim


class Traits(Int):
    SIMLISH = 123456789
    SIXAMI = 987654321


def get_trait(trait_id):
    trait_manager = get_instance_manager(Types.TRAIT)
    return trait_manager.get(trait_id)


def sim_has_a_language(sim_info):
    for trait_id in Traits:
        trait = get_trait(trait_id)
        if sim_info.has_trait(trait):
            return True
    return False


def sim_needs_a_language(sim_info):
    if sim_has_a_language(sim_info):
        return False
    return (sim_info.species == Species.HUMAN) and (sim_info.age >= Age.CHILD)


def sim_should_speak_sixami(sim_info):
    return sim_info.occult_tracker.has_occult_type(OccultType.ALIEN)


def try_assign_language_trait(sim_info):
    if sim_needs_a_language(sim_info):
        trait_id = Traits.SIXAMI if sim_should_speak_sixami(sim_info) else Traits.SIMLISH
        trait = get_trait(trait_id)
        sim_info.add_trait(trait)


def inject(target_function, new_function):
    @wraps(target_function)
    def _inject(*args, **kwargs):
        return new_function(target_function, *args, **kwargs)

    return _inject


def inject_to(target_object, target_function_name):
    def _inject_to(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, inject(target_function, new_function))
        return new_function

    return _inject_to


@inject_to(Sim, 'on_add')
def on_sim_instanced(original, self, *args, **kwargs):
    result = original(self, *args, **kwargs)
    try:
        try_assign_language_trait(self.sim_info)
    except:
        pass
    return result
