# 📘 Cahier des charges — **RTPA Studio** (v2025-09-06)

> **Cadre legal & ethique**
> Usage etude/formation/simulation uniquement (post-session, sandbox, self-play).
> Interdits : capture/overlay/hook live sur clients de poker, communication avec plateformes, anti-detection/evasion.
> Entrees autorisees : historiques de mains (HH), donnees de reference locales, saisie manuelle d'etats.

---

## 0) Synthese & adaptations
- Conservation : base C++20, architecture modulaire, CFR/CFR+/Deep CFR, UI d'etude (ImGui), haute perf, packaging, tests.
- Remplacement (vs propositions Cline temps reel) : pas de capture ecran/Windows API, pas d'integration Winamax/PokerStars/Bwin, pas de 'non-detectabilite'.
- Nouveautes (accelerer dev) : integration DeepStack-Leduc (toy game) et Hands_History comme ressources d'entrainement/validation et echantillons.

---

## 1) Portee & objectifs
- Pipeline complet : HH -> DB SQLite -> features -> CFR+ / Deep CFR (opt) -> evaluation -> UI etude & rapports.
- Seed initiale : (a) import Hands_History + (b) generation N mains synthetiques self-play baselines + (c) scenarios DeepStack-Leduc (validation/toy).
- Reproductibilite : seeds RNG, checkpoints modeles/datasets, configs YAML versionnees.
- Extensibilite : nouveaux parsers HH, nouveaux binnings, nouveaux algorithmes.
Hors perimetre : integration live, anti-cheat, automations systeme/Windows, interaction avec clients tiers.

---

## 2) Exigences
### 2.1 Fonctionnelles (FR-xx)
- FR-01 Import HH multi-rooms (Winamax, PokerStars) + auto-detection (RoomDetect).
- FR-02 Normalisation -> SQLite + index; migrations versionnees.
- FR-03 Encodage features (etat compact) + labels (action / size_bin).
- FR-04 Binnings actions/sizings contextualises (SPR/street), board textures, buckets 1326->K.
- FR-05 CFR+ discret : regrets>=0, averaging pondere, sampling External/Outcome.
- FR-06 Deep CFR (option torch) : A-Net/P-Net, buffers reservoir, cycles.
- FR-07 Evaluation : EV self-play, regret moyen, proxy exploitabilite (sous abstraction), ablations.
- FR-08 UI etude (Dashboard/Review/Sandbox/Training) + exports CSV/PDF.
- FR-09 Seed initiale : importer Hands_History + generer N mains synthetiques + importer scenarios Leduc.
- FR-10 Outils CLI : rtpa_db_init, rtpa_import_hh, rtpa_make_features, rtpa_train_cfr, rtpa_eval, rtpa_ui, rtpa_dump_bins, rtpa_seed_synth.

### 2.2 Non-fonctionnelles (NFR-xx)
- NFR-Perf : objectifs indicatifs Desktop moderne - CFR+ >= 50k actions/s binned ; EV MC >= 200k it/s.
- NFR-Robustesse : build OK sans torch (Deep CFR off) ; tests unitaires/integration ; ctest.
- NFR-Portabilite : Windows 10+/Linux x64 ; MSVC/Clang/GCC ; CMake >= 3.20.
- NFR-Securite : pas d'acces process externes ; pas de reseau par defaut.
- NFR-Evolutivite : interfaces stables, options CMake, configs YAML.

---

## 3) Architecture
### 3.1 Modules
```
core/  : arbres, CFR+, regrets/strategies, binnings, RNG, utils
deep/  : A-Net, P-Net, replay buffers (libtorch) [optionnel]
data/  : parsers HH, normalisation, FeatureEncoder, import DeepStack-Leduc
db/    : SQLite RAII, migrations, DAO, train_runs, eval_metrics
sim/   : EV/rollouts Monte-Carlo, self-play, baselines
ui/    : ImGui (Dashboard/Review/Sandbox/Training/Exports)
tools/ : CLI (db_init, import_hh, make_features, train_cfr, train_deep_cfr, eval, ui, dump_bins, seed_synth)
tests/ : unitaires, integration, perf, fuzz/property parsers
docs/  : guides (install/usage/datasets/algo/ui), samples (HH, Leduc), config_samples/
third_party/, cmake/, CMakeLists.txt
```

### 3.2 Options CMake
RTPA_WITH_DEEPCFR(OFF), RTPA_WITH_IMGUI(ON), RTPA_WITH_QT(OFF), RTPA_WITH_RUST_FFI(OFF).
Libs : fmt, spdlog, sqlite3 amalgamation, yaml-cpp, ImGui+GLFW, Catch2/GoogleTest.

---

## 4) Donnees & DB
### 4.1 Schema (DDL abrege)
Tables : players, hands, seats, actions, boards, showdowns, features, models, train_runs, eval_metrics, config.
Index : (hand_id, street) sur actions, (street) sur features, (model_id) sur train_runs.

### 4.2 Sources & licensing
- Hands_History/ (locaux) : importer -> normaliser ; verifier droits/licence ; anonymiser.
- DeepStack-Leduc/ : integrer scenarios Leduc (toy) pour tests/validation.
- Synthetiques : rtpa_seed_synth produit N mains self-play baseline (configurable).

### 4.3 Pipeline
/data/raw -> parse/normalize -> insert DB -> features -> split train/val/test (stratifie) -> dataset_tag.

---

## 5) Etats & abstractions
- Buckets cartes 1326->K (K in {32,64,128,...}) par equite vs ranges, isomorphismes et card-removal.
- Textures board : dry/semi-wet/wet, monotone/2-tone, paire, high/low, connecte.
- Binnings actions : {{Fold, Check/Call, Bet/Raise : 25/33/50/66/75/100/Pot/All-in}} filtres par SPR/street.
- Feature encoding : hero (bucket, pos, stack eff, SPR), board (texture +/- cartes), history (seq binned), contexte (nb joueurs).
- Labels : (action_class, size_bin), eventuellement logits/advantage.

---

## 6) Algorithmes
### 6.1 CFR / CFR+
Regret (I,a) :
R^t(I,a) = R^{t-1}(I,a) + sum_{z in Z_I} pi^{sigma}_{-i}(z[I]) * (u_i(sigma_{I->a}, z) - u_i(sigma, z))
Regret-matching :
sigma^{t+1}(I,a) = R^t(I,a)^+ / sum_b R^t(I,b)^+
CFR+ : clipping regrets >= 0 ; averaging pondere ; sampling External/Outcome.

### 6.2 Monte-Carlo EV
Rollouts partiels street-by-street ; RNG thread-local ; back-solves (river->turn->flop) pour amorcer regrets.

### 6.3 Deep CFR (option)
A-Net/P-Net, buffers reservoir ; cycles : traversals -> train A -> update sigma -> train P.
Hyperparams init : width 256-512, depth 3-5, dropout 0.1-0.2, lr 1e-3, batch 2k-8k, cosine decay.

### 6.4 Validation Leduc
Leduc Hold'em (etat reduit) pour tests unitaires : convergence CFR+ rapide ; verifs de coherence.
Pont d'abstraction : memes interfaces (GameTree/Infosets), autre jeu.

---

## 7) UI d'etude (ImGui)
Dashboard (KPIs, runs, checkpoints), Review (replayer HH + alternatives/EV), Sandbox (editeur d'etats), Training (jobs CFR/Deep), Exports (CSV/PDF).
Non-bloquante ; filtres ; themes ; ouverture dossiers exports/checkpoints.

---

## 8) Config, logs, qualite
YAML : global.yaml, bins.yaml, cfr.yaml, deep.yaml (docs/config_samples/).
Logs : spdlog rotatif ; niveaux ; timestamps ; journaux runs (DB).
Tests : unitaires/integration ; fuzz/property parsers ; perf microbench ; seuils regression optionnels.
Sanitizers : ASan/UBSan (Clang/GCC) ; /W4 /WX (MSVC).

---

## 9) Packaging & deploiement
cpack zip/7z : binaires, rtpa.db vierge, docs, samples (HH/Leduc), config, docs/config_samples.
RTPA_VERSION (semver) ; --version dans chaque binaire.

---

## 10) Roadmap & livrables
M1 DB+ingestion ; M2 EV+CFR+ ; M3 Deep CFR (opt) ; M4 UI ; M5 Eval+Docs.
Livrables : binaires, DB, checkpoints, scripts seeds, docs completes.

---

## 11) Risques & mitigations
Variabilite HH -> tests & fuzz ; licences/droits HH -> verif & anonymisation.
Perf -> binnings adaptatifs, Rust FFI (option).
Complexite Deep -> voie CFR+ only complete & stable.

---

## 12) Annexes
Pseudo-code CFR+/Deep CFR, exemples YAML, modeles rapports CSV.
Notes : mappages Leduc<->NLHE (abstractions, tailles d'actions) pour tests.
