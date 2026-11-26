# D2R MapPredictor

An offline feasibility study for estimating the direction of undiscovered exits and waypoints from visible Diablo II: Resurrected automap geometry.

**The Phase 1 offline experiment is available.** Its synthetic checks run locally. The D2R verdict is **INCONCLUSIVE** until independently annotated gameplay data is available. [Phase 1 results](docs/PHASE_1_RESULTS.md)

Start with **Catacombs Level 2, Normal difficulty, entering from Catacombs Level 1**. The two targets are the exit to Level 3 and the waypoint. Compare a geometry matcher against a baseline conditioned on entrance orientation. A waypoint arrival would reveal the waypoint immediately, so it would test a different question.

## Uruchomienie i użycie

Uruchom w PowerShellu z katalogu projektu. Wystarczy Python 3.11. Test działa offline na przykładach syntetycznych i nie wymaga instalowania bibliotek.

```powershell
python -m research.geometry_experiment validate fixtures/synthetic
python -m unittest discover -s tests -v
New-Item -ItemType Directory -Path local-data -Force | Out-Null
python -m research.geometry_experiment benchmark fixtures/synthetic --profile --output local-data/phase1-synthetic.json
```

W raporcie JSON sekcja `stages` zawiera wyniki z kolejnych klatek osobno dla zejścia (`NEXT`) i waypointu (`WP`). W `three_room_checkpoint` znajdziesz porównanie po odkryciu trzech pomieszczeń. Czytaj `accuracy` razem z `coverage`, czyli odsetkiem kwalifikujących się przypadków, w których metoda wskazała kierunek.

Aby użyć własnych nagrań, przygotuj trzy pliki JSON zgodnie z instrukcją zbierania i adnotacji danych. Umieść je np. w `local-data/real` i podaj tę ścieżkę zamiast `fixtures/synthetic`. Opcja `--development` ocenia zbiór rozwojowy, za każdym razem pozostawiając jedną mapę poza próbą uczącą. Domyślny benchmark ocenia wydzielone mapy testowe. [Instrukcja zbierania danych](docs/DATA_COLLECTION_GUIDE.md) · [Metodyka fazy 1](docs/EXPERIMENT_PROTOCOL.md)

| Document | Contents |
| --- | --- |
| [Project scope](docs/PROJECT_SCOPE.md) | Goals, inputs, constraints, and area selection |
| [Research](docs/RESEARCH.md) | Source review, map formats, and compatibility evidence |
| [Feasibility](docs/FEASIBILITY.md) | Candidate algorithms, risks, and continuation gates |
| [Architecture](docs/ARCHITECTURE.md) | Proposed offline data flow and matching contract |
| [Decisions](docs/DECISIONS.md) | Decisions and their rationale |
| [Phase 1 plan](docs/PHASE_1_PLAN.md) | Scope and audit findings |
| [Phase 1 results](docs/PHASE_1_RESULTS.md) | Synthetic replay, limitations and D2R verdict |
| [Environment](research/ENVIRONMENT.md) | Local prerequisites and verification limits |
| [Phase 0 benchmark proposal](benchmarks/PROTOCOL.md) | Original research design |

The CLI lives in `research/geometry_experiment/` with tests in `tests/` and synthetic inputs in `fixtures/synthetic/`. Keep licensed game data and local recordings outside version control. Use `local-data/` if a workspace-local location is needed.
