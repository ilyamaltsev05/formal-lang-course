from pyformlang.cfg import CFG


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    return cfg.to_normal_form()
