"""PARADOX_ENGINE_1.0 — Core sub-package."""
from paradox_engine.core.paradox import Paradox, ParadoxLibrary, ParadoxNode, Polarity, Proposition, SelfRefClass
from paradox_engine.core.simulation import ParadoxSimulation, SimulationState
from paradox_engine.core.resolver import RecursiveResolver, ResolutionResult, HaltReason
from paradox_engine.core.engine import ParadoxEngine
