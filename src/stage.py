# -*- coding: utf-8 -*-
class Stage:
    def __init__(self, formula, valuation, disabled, speed=None, parent=None):
        self._formula   = formula
        self._valuation = valuation
        self._disabled  = disabled
        self._speed     = speed
        self._parent    = parent

    @property
    def formula(self):
        return self._formula

    @property
    def valuation(self):
        return self._valuation

    @property
    def disabled(self):
        return self._disabled

    @property
    def speed(self):
        return self._speed

    @property
    def parent(self):
        return self._parent

    def is_redundant(self):
        def subsumed_by(stage):
            return ((stage.valuation == self.valuation) and
                    (stage.disabled  == self.disabled)  and
                    (stage.formula.implies(self.formula)))

        stage = self.parent

        while stage != None:
            if subsumed_by(stage):
                return True
            else:
                stage = stage.parent

        return False

    def __str__(self):
        return "(Φ = {}\n π = {}\n T = {})".format(str(self._formula),
                                                   str(self._valuation),
                                                   str(self._disabled))

    def __repr__(self):
        return str(self)
